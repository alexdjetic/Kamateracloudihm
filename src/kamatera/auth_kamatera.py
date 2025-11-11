import requests
from typing import Any, Dict, Optional

def get_kamatera_token(
    client_id: str,
    secret: str,
    base_url: str = "https://console.kamatera.com",
    timeout: Optional[float] = 10.0,
) -> Dict[str, Optional[str]]:
    """
    Authentifie auprès de Kamatera avec clientId/secret et retourne le token.

    Parameters
    ----------
    client_id : str
        Le clientId fourni par Kamatera.
    secret : str
        Le secret associé.
    base_url : str
        Base URL de l'API (par défaut console.kamatera.com).
    timeout : float | None
        Timeout de la requête en secondes.

    Returns
    -------
    dict
        {'token': str|None, 'expires': int|None, 'raw': dict|None, 'error': str|None}

    Raises
    ------
    requests.RequestException
        En cas d'erreur réseau ou réponse non-2xx (la méthode lève l'exception).
    """
    url: str = f"{base_url.rstrip('/')}/service/authenticate"
    payload: Dict[str, str] = {"clientId": client_id, "secret": secret}
    headers: Dict[str, str] = {"Accept": "application/json", "Content-Type": "application/json"}

    resp: requests.Response = requests.post(url, json=payload, headers=headers, timeout=timeout)

    # Lève HTTPError pour codes >= 400
    resp.raise_for_status()

    # Si on reçoit du HTML, très probablement mauvais endpoint
    ct: str = resp.headers.get("content-type", "")
    if "html" in ct.lower():
        return {"token": None, "expires": None, "raw": None, "error": "HTML response — vérifie l'URL (tu as peut-être appelé la console web)"}

    # Parse JSON
    data: Dict[str, Any] = resp.json() if resp.content else {}

    # Cherche le champ du token — Kamatera peut renvoyer "authentication" ou "token"/"access_token"
    token: Optional[str] = None
    expires: Optional[int] = None
    
    if isinstance(data, dict):
        token = data.get("authentication") or data.get("token") or data.get("access_token") or data.get("authentication_token")
        expires = data.get("expires") or data.get("expires_in") or data.get("expiration")

    return {"token": token, "expires": expires, "raw": data, "error": None}
