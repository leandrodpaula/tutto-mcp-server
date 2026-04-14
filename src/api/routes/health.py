"""Health check endpoint."""

from fastapi import APIRouter, status

router = APIRouter(tags=["health"])


@router.get("/healthz", status_code=status.HTTP_200_OK)
async def healthz() -> dict:
    """Health check endpoint para Cloud Run."""
    return {"status": "ok", "service": "tutto-mcp-server"}
