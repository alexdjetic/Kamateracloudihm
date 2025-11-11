"""Routes pour les actions de contrôle des serveurs (start/stop/reboot).

Ces endpoints s'appuient sur une variable d'environnement ``KAMATERA_API_KEY``
populée soit manuellement, soit par le job de rafraîchissement (lifespan).
"""

from os import getenv
from typing import Any, Optional

from fastapi import APIRouter
from fastapi.responses import ORJSONResponse
from fastapi import status

from kamatera.Kamatera_cloud_management import KamateraCloudManagement
from models.control_modele import ControlModel
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


@router.post(
    "/start",
    response_class=ORJSONResponse,
    description="Démarre un serveur Kamatera via l'API.",
    status_code=status.HTTP_200_OK,
)
async def start_server(payload: ControlModel) -> ORJSONResponse:
    """Démarre le serveur indiqué par ``payload.server_id``.

    Exige que la variable d'environnement `KAMATERA_API_KEY` soit définie.
    """
    api_key = _get_api_key()
    if not api_key:
        return ORJSONResponse(content={"message": API_KEY_MISSING_MSG}, status_code=status.HTTP_401_UNAUTHORIZED)

    client = KamateraCloudManagement(api_key=api_key)
    try:
        res: dict[str, Any] = client.start_server(payload.server_id)
    except Exception as exc:
        return ORJSONResponse(content={"message": str(exc)}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return ORJSONResponse(content=res, status_code=res.get("status", 200))


@router.post(
    "/stop",
    response_class=ORJSONResponse,
    description="Arrête un serveur Kamatera via l'API.",
    status_code=status.HTTP_200_OK,
)
async def stop_server(payload: ControlModel) -> ORJSONResponse:
    """Arrête le serveur indiqué par ``payload.server_id``."""
    api_key = _get_api_key()
    if not api_key:
        return ORJSONResponse(content={"message": API_KEY_MISSING_MSG}, status_code=status.HTTP_401_UNAUTHORIZED)

    client = KamateraCloudManagement(api_key=api_key)
    try:
        res: dict[str, Any] = client.stop_server(payload.server_id)
    except Exception as exc:
        return ORJSONResponse(content={"message": str(exc)}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return ORJSONResponse(content=res, status_code=res.get("status", 200))


@router.post(
    "/reboot",
    response_class=ORJSONResponse,
    description="Redémarre un serveur Kamatera via l'API.",
    status_code=status.HTTP_200_OK,
)
async def reboot_server(payload: ControlModel) -> ORJSONResponse:
    """Redémarre le serveur indiqué par ``payload.server_id``."""
    api_key = _get_api_key()
    if not api_key:
        return ORJSONResponse(content={"message": API_KEY_MISSING_MSG}, status_code=status.HTTP_401_UNAUTHORIZED)

    client = KamateraCloudManagement(api_key=api_key)
    try:
        res: dict[str, Any] = client.reboot_server(payload.server_id)
    except Exception as exc:
        return ORJSONResponse(content={"message": str(exc)}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return ORJSONResponse(content=res, status_code=res.get("status", 200))


@router.post(
    "/destroy",
    response_class=ORJSONResponse,
    description="Détruit/supprime un serveur Kamatera via l'API.",
    status_code=status.HTTP_200_OK,
)
async def destroy_server(payload: ControlModel) -> ORJSONResponse:
    """Détruit le serveur indiqué par ``payload.server_id``.
    
    Cette action est irréversible et supprime définitivement le serveur.
    """
    api_key = _get_api_key()
    if not api_key:
        return ORJSONResponse(content={"message": API_KEY_MISSING_MSG}, status_code=status.HTTP_401_UNAUTHORIZED)

    client = KamateraCloudManagement(api_key=api_key)
    try:
        res: dict[str, Any] = client.delete_server(payload.server_id)
    except Exception as exc:
        return ORJSONResponse(content={"message": str(exc)}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return ORJSONResponse(content=res, status_code=res.get("status", 200))
