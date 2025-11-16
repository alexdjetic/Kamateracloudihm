"""Client léger pour l'API Kamatera Cloud.

Ce module fournit la classe :class:`KamateraCloudManagement` qui encapsule
les appels HTTP vers les endpoints REST de Kamatera Cloud.

Le but est d'offrir une interface simple pour lister, créer, supprimer et
contrôler des serveurs. Les réponses sont formatées de façon uniforme par
``_format_response`` et les erreurs par ``_format_error``.

Exemple rapide:

>>> client = KamateraCloudManagement(api_key="sk_test_...")
>>> res = client.list_servers()
>>> assert isinstance(res, dict)

Toutes les méthodes publiques renvoient un dictionnaire contenant au moins
les clés ``message``, ``status`` et ``data``.
"""

from typing import Any, Dict, Optional, List, Tuple
import os
import requests


class KamateraCloudManagement:
    """Client léger pour l'API Kamatera Cloud.

    Fournit des méthodes pour interagir avec les endpoints de gestion des
    serveurs (liste, création, suppression, démarrage/arrêt, snapshot, etc.).

    Attributs
    ---------
    api_key:
        Clé d'API utilisée pour l'authentification Bearer.
    base_url:
        URL de base des endpoints REST. Par défaut ``https://console.kamatera.com``.
    session:
        Session ``requests.Session`` réutilisée pour les appels HTTP.

    Note
    ----
    Cette classe ne gère pas la pagination avancée ni le throttling. Les
    consommateurs doivent adapter le timeout et le retry s'ils en ont besoin.
    """

    def __init__(self, api_key: str, base_url: str = "https://console.kamatera.com/service") -> None:
        """Initialise le client.

        Parameters
        ----------
        api_key:
            Clé d'API Bearer fournie par Kamatera.
        base_url:
            URL de base pour les endpoints REST (valeur par défaut fournie).

        Raises
        ------
        ValueError
            Si ``api_key`` est vide.
        """
        if not api_key:
            raise ValueError("api_key must be fourni")
        self.api_key: str = api_key
        # Allow overriding the base URL via environment variable to support
        # non-default API endpoints or debugging (KAMATERA_BASE_URL).
        self.base_url: str = os.getenv("KAMATERA_BASE_URL", base_url)
        self.session: requests.Session = requests.Session()

    def _headers(self) -> Dict[str, str]:
        """Retourne les en-têtes HTTP à inclure dans chaque requête.

        Returns
        -------
        dict
            Dictionnaire contenant Authorization Bearer, Accept et Content-Type.
        """
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    def _headers_delete(self) -> Dict[str, str]:
        """Retourne les en-têtes HTTP pour DELETE.
        
        Kamatera API DELETE /terminate needs Content-Type header but requests shouldn't
        auto-add Content-Length. We'll use a custom approach.

        Returns
        -------
        dict
            Dictionnaire avec Authorization et Accept (Content-Type sera omis).
        """
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
        }

    # Small helpers to keep formatters simple (reduce cognitive complexity)
    def _is_html_content(self, content_type: str) -> bool:
        """Return True if Content-Type indicates HTML.

        Isolé pour faciliter la lecture des formateurs.
        """
        return "html" in (content_type or "").lower()

    def _parse_json_safe(self, response: requests.Response) -> Any:
        """Try to parse response as JSON, otherwise return text or empty list.

        Kept as a helper to minimize branching in the main formatter.
        """
        try:
            return response.json()
        except Exception:
            return response.text or []

    def _normalize_payload(self, payload: Any) -> Tuple[Optional[str], List[Any]]:
        """Normalize different payload shapes into (message, list).

        Returns (message, data_list). Message can be None.
        """
        if isinstance(payload, list):
            return None, payload

        if isinstance(payload, dict):
            if "data" in payload and isinstance(payload["data"], list):
                return payload.get("message"), payload["data"]
            if "servers" in payload and isinstance(payload["servers"], list):
                return payload.get("message"), payload["servers"]
            if payload == {}:
                return payload.get("message"), []
            return payload.get("message"), [payload]

        return None, [payload]

    def _extract_first_error_message(self, parsed: Any) -> Optional[str]:
        """Retourne le message contenu dans ``parsed['errors']`` si présent.

        Ce helper isole le parcours de la structure d'erreurs pour simplifier
        le code appelant.
        """
        if not isinstance(parsed, dict):
            return None
        errs = parsed.get("errors") or []
        if not errs or not isinstance(errs, list):
            return None
        first = errs[0]
        if isinstance(first, dict):
            return first.get("info") or first.get("message") or str(first)
        return str(first)

    def _parse_http_error(self, err: requests.HTTPError) -> Tuple[int, str]:
        """Parse la réponse jointe à une HTTPError et renvoie (status, message).

        Extrait la logique hors de _format_error pour réduire la complexité
        cognitive de cette dernière.
        """
        resp = err.response
        st = resp.status_code if resp is not None else 500
        ct = resp.headers.get("content-type", "") if resp is not None else ""
        if self._is_html_content(ct):
            return st, "Réponse HTML reçue. Utilise les endpoints REST API."

        try:
            parsed = resp.json() if resp is not None else None
        except Exception:
            return 500, "Erreur lors du parsing de la réponse JSON"
        # Extraire un message d'erreur si présent
        if isinstance(parsed, dict):
            msg = self._extract_first_error_message(parsed)
            if msg:
                return st, msg
            return st, parsed.get("message") or parsed.get("error") or str(parsed)

        return st, str(parsed)

    def _format_response(self, resp: requests.Response) -> Dict[str, Any]:
        """Formate la réponse HTTP en une structure uniforme.

        Utilise des helpers pour réduire la logique imbriquée.
        """
        content_type: str = resp.headers.get("content-type", "")
        if self._is_html_content(content_type):
            # The API returned HTML (likely the web console or an auth/login page).
            # Treat this as a bad gateway / proxy error so callers and UIs
            # surface it as a failure instead of a 200 OK with an empty list.
            return {
                "message": (
                    "Réponse HTML reçue. Vérifie que tu utilises le bon endpoint API "
                    "et non la console web. Vérifie également la valeur de `base_url`/KAMATERA_BASE_URL."
                ),
                "status": 502,
                "data": [],
            }

        payload: Any = self._parse_json_safe(resp)

        # Cas d'erreurs renvoyées par l'API
        if isinstance(payload, dict) and "errors" in payload:
            errs = payload.get("errors") or []
            if not errs:
                return {"message": "Unknown error", "status": resp.status_code, "data": []}
            first = errs[0]
            if isinstance(first, dict):
                err_msg = first.get("info") or first.get("message") or str(first)
            else:
                err_msg = str(first)
            return {"message": err_msg, "status": resp.status_code, "data": []}

        # Normaliser le payload vers une liste et extraire un éventuel message
        message, data = self._normalize_payload(payload)
        return {"message": message or resp.reason or "OK", "status": resp.status_code, "data": data}

    def _format_error(self, exc: Exception) -> Dict[str, Any]:
        """Formate une exception Request en un dict uniforme.

        Le parsing de la réponse d'erreur est isolé dans un helper local pour
        réduire la complexité de cette méthode.
        """
        status: int = 500
        message: str = str(exc)

        if isinstance(exc, requests.HTTPError) and exc.response is not None:
            status, message = self._parse_http_error(exc)

        return {"message": message, "status": status, "data": []}

    # ---------------------- Actions Serveur ---------------------- #

    def list_servers(self, timeout: Optional[float] = 10.0) -> Dict[str, Any]:
        """Récupère la liste des serveurs pour le compte.

        Parameters
        ----------
        timeout:
            Timeout en secondes pour la requête HTTP (flottant). Valeur par défaut 10.0.

        Returns
        -------
        dict
            Dictionnaire formaté par ``_format_response`` contenant la liste des serveurs
            dans ``data``.
        """
        try:
            resp: requests.Response = self.session.get(f"{self.base_url}/servers", headers=self._headers(), timeout=timeout)
            resp.raise_for_status()
            return self._format_response(resp)
        except requests.RequestException as exc:
            return self._format_error(exc)

    def delete_server(self, server_id: str, timeout: Optional[float] = 10.0) -> Dict[str, Any]:
        """Supprime un serveur identifié par ``server_id``.

        Parameters
        ----------
        server_id:
            Identifiant du serveur à supprimer.
        timeout:
            Timeout en secondes pour la requête.

        Returns
        -------
        dict
            Réponse formatée de l'API.
        """
        try:
            # Build request manually to have complete control over body
            headers = self._headers_delete()
            headers["Content-Type"] = "application/json"
            
            # Create a Request object
            req = requests.Request(
                method='DELETE',
                url=f"{self.base_url}/server/{server_id}/terminate",
                headers=headers
            )
            
            # Prepare it
            prepared = self.session.prepare_request(req)
            
            # Make sure there's no body
            prepared.body = None
            
            # Send it
            resp: requests.Response = self.session.send(prepared, timeout=timeout)
            resp.raise_for_status()
            return self._format_response(resp)
        except requests.RequestException as exc:
            return self._format_error(exc)

    def get_server_details(self, server_id: str, timeout: Optional[float] = 10.0) -> Dict[str, Any]:
        """Récupère les détails d'un serveur donné.

        Returns
        -------
        dict
            Détails du serveur dans la clé ``data`` si succès.
        """
        try:
            resp: requests.Response = self.session.get(f"{self.base_url}/server/{server_id}", headers=self._headers(), timeout=timeout)
            resp.raise_for_status()
            return self._format_response(resp)
        except requests.RequestException as exc:
            return self._format_error(exc)

    def stop_server(self, server_id: str, timeout: Optional[float] = 10.0) -> Dict[str, Any]:
        """Arrête proprement un serveur via l'endpoint ``/power``."""
        try:
            resp: requests.Response = self.session.put(f"{self.base_url}/server/{server_id}/power", headers=self._headers(), json={"power": "off"}, timeout=timeout)
            resp.raise_for_status()
            return self._format_response(resp)
        except requests.RequestException as exc:
            return self._format_error(exc)

    def start_server(self, server_id: str, timeout: Optional[float] = 10.0) -> Dict[str, Any]:
        """Démarre un serveur via l'endpoint ``/power``."""
        try:
            resp: requests.Response = self.session.put(f"{self.base_url}/server/{server_id}/power", headers=self._headers(), json={"power": "on"}, timeout=timeout)
            resp.raise_for_status()
            return self._format_response(resp)
        except requests.RequestException as exc:
            return self._format_error(exc)
        
    def reboot_server(self, server_id: str, timeout: Optional[float] = 10.0) -> Dict[str, Any]:
        """Redémarre un serveur via l'endpoint ``/power``."""
        try:
            resp: requests.Response = self.session.put(f"{self.base_url}/server/{server_id}/power", headers=self._headers(), json={"power": "restart"}, timeout=timeout)
            resp.raise_for_status()
            return self._format_response(resp)
        except requests.RequestException as exc:
            return self._format_error(exc)

    def rename_server(self, server_id: str, new_name: str, timeout: Optional[float] = 10.0) -> Dict[str, Any]:
        """Renomme un serveur.

        Parameters
        ----------
        new_size:
            Dictionnaire décrivant la nouvelle configuration attendue par l'API.
        """
        try:
            resp: requests.Response = self.session.put(f"{self.base_url}/server/{server_id}/rename", headers=self._headers(), json={"name": new_name}, timeout=timeout)
            resp.raise_for_status()
            return self._format_response(resp)
        except requests.RequestException as exc:
            return self._format_error(exc)

    def clone_server(self, server_id: str, name: Optional[str] = None, password: Optional[str] = None, billing: str = "hour", timeout: Optional[float] = 60.0) -> Dict[str, Any]:
        """Clone un serveur avec une nouvelle IP publique mais sans le démarrer.

        Parameters
        ----------
        server_id:
            Identifiant du serveur à cloner (source).
        name:
            Nom optionnel pour le serveur cloné. Si non fourni, Kamatera génère un nom par défaut.
        password:
            Mot de passe root pour le nouveau serveur cloné. Requis par l'API Kamatera.
        billing:
            Type de facturation: "hour" (à l'heure) ou "month" (mensuel). Par défaut "hour".
        timeout:
            Timeout en secondes pour la requête.

        Returns
        -------
        dict
            Réponse formatée de l'API contenant les détails du serveur cloné.
        """
        try:
            payload = {
                "source": server_id,
                "powerOn": "no",
                "billing": billing
            }
            if name:
                payload["name"] = name
            if password:
                payload["password"] = password
            
            resp: requests.Response = self.session.post(
                f"{self.base_url}/server/clone",
                headers=self._headers(),
                json=payload,
                timeout=timeout
            )
            resp.raise_for_status()
            return self._format_response(resp)
        except requests.RequestException as exc:
            return self._format_error(exc)
