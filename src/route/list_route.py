"""Routes pour la consultation des serveurs (liste et détails).

Ces endpoints utilisent la variable d'environnement `KAMATERA_API_KEY` qui
peut être mise à jour automatiquement par le job de rafraîchissement.
"""

from os import getenv
from typing import Any, Optional

from fastapi import APIRouter
from fastapi.responses import ORJSONResponse
from fastapi import status

from kamatera.Kamatera_cloud_management import KamateraCloudManagement
from logger import get_logger


router = APIRouter()
API_KEY_MISSING_MSG: str = "KAMATERA_API_KEY not set"
logger = get_logger(__name__)


def _get_api_key() -> Optional[str]:
    """Récupère la clé API.

    Comportement:
    - Si ``KAMATERA_API_KEY`` est présent dans l'environnement, le retourne.
    - Sinon retourne ``None``.
    """
    # Try env var (set by background refresher or manually)
    token: str = getenv("KAMATERA_API_KEY")
    if token:
        return token

    # Nothing available
    logger.debug("No KAMATERA_API_KEY and no client_id/secret available")
    return None


@router.get(
    "/servers",
    response_class=ORJSONResponse,
    description="Liste les serveurs Kamatera via l'API.",
)
async def list_servers() -> ORJSONResponse:
    """Retourne la liste des serveurs via le client Kamatera.

    Si la clé API n'est pas configurée, renvoie 401.
    """
    api_key: Optional[str] = _get_api_key()
    if not api_key:
        return ORJSONResponse(content={"message": API_KEY_MISSING_MSG}, status_code=status.HTTP_401_UNAUTHORIZED)

    # Avoid logging secrets. Show a masked form to help debugging without
    # exposing the full API key value in logs.
    print(api_key)
    try:
        masked = f"{api_key[:4]}...{api_key[-4:]}" if api_key and len(api_key) > 8 else "****"
    except Exception:
        masked = "****"
    logger.info("Using KAMATERA_API_KEY (masked): %s", masked)

    # Log which base_url is being used (do not include credentials). This
    # helps diagnose situations where the default base_url points to the
    # web console rather than the REST API.
    try:
        client: KamateraCloudManagement = KamateraCloudManagement(api_key=api_key)
        used_base = client.base_url
        logger.info("Using Kamatera base_url: %s", used_base)
    except Exception:
        # If client construction fails for unexpected reasons, still continue
        client: KamateraCloudManagement = KamateraCloudManagement(api_key=api_key)

    # client variable is already initialised above
    try:
        res: dict[str, Any] = client.list_servers()
    except Exception as exc:
        return ORJSONResponse(content={"message": str(exc)}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return ORJSONResponse(content=res, status_code=res.get("status", 200))


@router.get(
    "/server",
    response_class=ORJSONResponse,
    description="Récupère les détails d'un serveur via l'API (query param `server_id`).",
)
async def get_server(server_id: str) -> ORJSONResponse:
    """Récupère les détails d'un serveur identifié par le query param `server_id`.

    Exemple: GET /server?server_id=abcd
    """
    if not server_id:
        return ORJSONResponse(content={"message": "server_id required"}, status_code=status.HTTP_400_BAD_REQUEST)

    api_key: Optional[str] = _get_api_key()
    print(api_key)
    if not api_key:
        return ORJSONResponse(content={"message": API_KEY_MISSING_MSG}, status_code=status.HTTP_401_UNAUTHORIZED)

    client: KamateraCloudManagement = KamateraCloudManagement(api_key=api_key)
    try:
        res: dict[str, Any] = client.get_server_details(server_id)
    except Exception as exc:
        return ORJSONResponse(content={"message": str(exc)}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return ORJSONResponse(content=res, status_code=res.get("status", 200))
