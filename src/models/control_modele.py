from pydantic import BaseModel


class ControlModel(BaseModel):
    """Modèle de données pour le contrôle des serveurs Kamatera."""
    server_id: str
    action: str