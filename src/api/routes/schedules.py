"""Rotas HTTP para gerenciamento de Schedules."""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from src.api.auth import require_auth
from src.api.deps import get_db
from src.core.logging import get_logger
from src.models.schedule import ScheduleCreate, ScheduleOut
from src.repositories.schedule_repository import ScheduleRepository
from src.services.schedule_service import ScheduleService, ScheduleServiceError

logger = get_logger(__name__)
router = APIRouter(
    prefix="/schedules",
    tags=["schedules"],
    dependencies=[Depends(require_auth)],
)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_schedule(
    payload: ScheduleCreate,
    db: AsyncIOMotorDatabase = Depends(get_db),  # noqa: B008
) -> dict:
    """Cria um novo agendamento."""
    try:
        repo = ScheduleRepository(db)
        service = ScheduleService(repo)
        schedule = await service.create_schedule(payload)
        return {
            "message": "Schedule created successfully",
            "schedule": ScheduleOut(**schedule).model_dump(by_alias=True),
        }
    except ScheduleServiceError as exc:
        logger.warning(f"Schedule creation failed: {exc}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception as exc:
        logger.error(f"Unexpected error creating schedule: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        ) from exc


@router.get("")
async def list_schedules(
    tenant_id: str = Query(..., description="ID do tenant"),  # noqa: B008
    status_filter: Optional[str] = Query(  # noqa: B008
        None, alias="status", description="Filtrar por status"
    ),
    date_from: Optional[datetime] = Query(  # noqa: B008
        None, description="Data inicial (ISO 8601)"
    ),
    date_to: Optional[datetime] = Query(None, description="Data final (ISO 8601)"),  # noqa: B008
    db: AsyncIOMotorDatabase = Depends(get_db),  # noqa: B008
) -> dict:
    """Lista agendamentos de um tenant com filtros opcionais."""
    try:
        repo = ScheduleRepository(db)
        service = ScheduleService(repo)

        filters: dict = {}
        if status_filter:
            filters["status"] = status_filter
        if date_from:
            filters["date_from"] = date_from
        if date_to:
            filters["date_to"] = date_to

        schedules = await service.list_schedules(tenant_id, filters if filters else None)
        return {
            "schedules": [ScheduleOut(**s).model_dump(by_alias=True) for s in schedules],
        }
    except ScheduleServiceError as exc:
        logger.warning(f"Schedule listing failed: {exc}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception as exc:
        logger.error(f"Unexpected error listing schedules: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        ) from exc


@router.get("/{schedule_id}")
async def get_schedule(
    schedule_id: str,
    tenant_id: str = Query(..., description="ID do tenant do agendamento"),  # noqa: B008
    db: AsyncIOMotorDatabase = Depends(get_db),  # noqa: B008
) -> dict:
    """Retorna os detalhes de um agendamento."""
    try:
        repo = ScheduleRepository(db)
        service = ScheduleService(repo)
        schedule = await service.get_schedule(schedule_id)
        if schedule.get("tenant_id") != tenant_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Schedule not found for this tenant",
            )
        return {
            "schedule": ScheduleOut(**schedule).model_dump(by_alias=True),
        }
    except ScheduleServiceError as exc:
        logger.warning(f"Schedule retrieval failed: {exc}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except Exception as exc:
        logger.error(f"Unexpected error retrieving schedule: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        ) from exc
