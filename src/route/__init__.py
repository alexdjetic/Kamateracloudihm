from fastapi import APIRouter
from fastapi.responses import ORJSONResponse

router = APIRouter()

@router.get("/health")
async def health_check():
    return {"status": "ok"}