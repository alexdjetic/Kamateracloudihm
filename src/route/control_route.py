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
from models.control_modele import ControlModel, RenameModel, CloneModel
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
    api_key: Optional[str] = _get_api_key()
    if not api_key:
        return ORJSONResponse(content={"message": API_KEY_MISSING_MSG}, status_code=status.HTTP_401_UNAUTHORIZED)

    client: KamateraCloudManagement = KamateraCloudManagement(api_key=api_key)
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
    api_key: Optional[str] = _get_api_key()
    if not api_key:
        return ORJSONResponse(content={"message": API_KEY_MISSING_MSG}, status_code=status.HTTP_401_UNAUTHORIZED)

    client: KamateraCloudManagement = KamateraCloudManagement(api_key=api_key)
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
    api_key: Optional[str] = _get_api_key()
    if not api_key:
        return ORJSONResponse(content={"message": API_KEY_MISSING_MSG}, status_code=status.HTTP_401_UNAUTHORIZED)

    client: KamateraCloudManagement = KamateraCloudManagement(api_key=api_key)
    try:
        res: dict[str, Any] = client.reboot_server(payload.server_id)
    except Exception as exc:
        return ORJSONResponse(content={"message": str(exc)}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return ORJSONResponse(content=res, status_code=res.get("status", 200))


@router.post(
    "/clone",
    response_class=ORJSONResponse,
    description="Clone un serveur Kamatera via l'API avec un nom personnalisé.",
    status_code=status.HTTP_200_OK,
)
async def clone_server(payload: CloneModel) -> ORJSONResponse:
    """Clone le serveur indiqué par ``payload.server_id``.
    
    Le nouveau serveur recevra une nouvelle IP publique mais ne sera pas démarré.
    Un nom personnalisé peut être fourni via ``payload.name``.
    """
    api_key: Optional[str] = _get_api_key()
    if not api_key:
        return ORJSONResponse(content={"message": API_KEY_MISSING_MSG}, status_code=status.HTTP_401_UNAUTHORIZED)

    client: KamateraCloudManagement = KamateraCloudManagement(api_key=api_key)
    try:
        res: dict[str, Any] = client.clone_server(payload.server_id, payload.name, payload.password, payload.billing)
    except Exception as exc:
        return ORJSONResponse(content={"message": str(exc)}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return ORJSONResponse(content=res, status_code=res.get("status", 200))


@router.put(
    "/rename",
    response_class=ORJSONResponse,
    description="Renomme un serveur Kamatera via l'API.",
    status_code=status.HTTP_200_OK,
)
async def rename_server(payload: RenameModel) -> ORJSONResponse:
    """Renomme le serveur indiqué par ``payload.server_id``.
    
    Le nouveau nom est fourni dans ``payload.name``.
    """
    api_key: Optional[str] = _get_api_key()
    if not api_key:
        return ORJSONResponse(content={"message": API_KEY_MISSING_MSG}, status_code=status.HTTP_401_UNAUTHORIZED)

    client: KamateraCloudManagement = KamateraCloudManagement(api_key=api_key)
    try:
        res: dict[str, Any] = client.rename_server(payload.server_id, payload.name)
    except Exception as exc:
        return ORJSONResponse(content={"message": str(exc)}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return ORJSONResponse(content=res, status_code=res.get("status", 200))


@router.delete(
    "/destroy",
    response_class=ORJSONResponse,
    description="Détruit/supprime un serveur Kamatera via l'API.",
    status_code=status.HTTP_200_OK,
)
async def destroy_server(server_id: Optional[str] = None) -> ORJSONResponse:
    """Détruit le serveur indiqué par le paramètre query ``server_id``.
    
    Attention: Cette action est irréversible!
    """
    if not server_id:
        return ORJSONResponse(content={"message": "server_id query parameter required"}, status_code=status.HTTP_400_BAD_REQUEST)
    
    api_key: Optional[str] = _get_api_key()
    if not api_key:
        return ORJSONResponse(content={"message": API_KEY_MISSING_MSG}, status_code=status.HTTP_401_UNAUTHORIZED)

    client: KamateraCloudManagement = KamateraCloudManagement(api_key=api_key)
    try:
        res: dict[str, Any] = client.delete_server(server_id)
    except Exception as exc:
        return ORJSONResponse(content={"message": str(exc)}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return ORJSONResponse(content=res, status_code=res.get("status", 200))
