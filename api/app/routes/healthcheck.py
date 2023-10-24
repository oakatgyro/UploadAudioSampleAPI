
from fastapi import APIRouter
router = APIRouter()


@router.get("", status_code=200)
async def health_check():
    """health_check
    Returns:
        {"health_check": "OK"}
    """

    return {"health_check": "OK"}