from pydantic import BaseModel
from typing import Optional


class ControlModel(BaseModel):
    """Modèle de données pour le contrôle des serveurs Kamatera."""
    server_id: str
    action: Optional[str] = None


class RenameModel(BaseModel):
    """Modèle de données pour renommer un serveur Kamatera."""
    server_id: str
    name: str


class CloneModel(BaseModel):
    """Modèle de données pour cloner un serveur Kamatera."""
    server_id: str
    name: Optional[str] = None
    password: Optional[str] = None
    billing: str = "hour"