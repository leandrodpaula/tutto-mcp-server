"""Rotas HTTP para operações de Tenant (QR code e conexão Evolution API)."""

from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from src.api.customer_auth import require_customer_auth
from src.api.deps import get_db
from src.core.config import settings
from src.core.logging import get_logger
from src.repositories.tenant_repository import TenantRepository
from src.services.evolution_service import EvolutionService, EvolutionServiceError

logger = get_logger(__name__)
router = APIRouter(prefix="/tenants", tags=["tenants"])


def _ensure_customer_tenant_access(customer: dict, tenant_id: str) -> None:
    if str(customer.get("tenant_id")) != str(tenant_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this tenant",
        )


@router.get("/{tenant_id}/qr-code")
async def get_tenant_qr_code(
    tenant_id: str,
    customer: dict = Depends(require_customer_auth),  # noqa: B008
    db: AsyncIOMotorDatabase = Depends(get_db),  # noqa: B008
) -> dict:
    """Retorna o QR code da instância WhatsApp do tenant via Evolution API."""
    _ensure_customer_tenant_access(customer, tenant_id)

    tenant_repo = TenantRepository(db)
    tenant = await tenant_repo.get_by_id(tenant_id)
    if not tenant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")

    instance_name = tenant.get("evolution_instance_name")
    if not instance_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tenant is not connected to Evolution API",
        )

    try:
        evolution = EvolutionService()
        connect_data = await evolution.connect_instance(instance_name)
        return {
            "tenant_id": tenant_id,
            "instance_name": instance_name,
            "qr_code": connect_data,
        }
    except EvolutionServiceError as exc:
        logger.error(f"Error fetching QR code for tenant {tenant_id}: {exc}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Evolution API error: {exc}",
        ) from exc
    except Exception as exc:
        logger.error(f"Unexpected error fetching QR code for tenant {tenant_id}: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error"
        ) from exc


@router.post("/{tenant_id}/connect")
async def connect_tenant(
    tenant_id: str,
    customer: dict = Depends(require_customer_auth),  # noqa: B008
    db: AsyncIOMotorDatabase = Depends(get_db),  # noqa: B008
) -> dict:
    """Conecta o tenant à Evolution API (WhatsApp) e persiste os dados de conexão."""
    _ensure_customer_tenant_access(customer, tenant_id)

    tenant_repo = TenantRepository(db)
    tenant = await tenant_repo.get_by_id(tenant_id)
    if not tenant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")

    instance_name = tenant.get("evolution_instance_name") or f"tenant-{tenant_id}"
    webhook_url = f"{settings.WEBHOOK_BASE_URL.rstrip('/')}/webhook/events"
    events = ["MESSAGES_UPSERT", "QRCODE_UPDATED", "CONNECTION_UPDATE"]

    try:
        evolution = EvolutionService()

        # 1. Cria instância na Evolution API
        create_data = await evolution.create_instance(
            instance_name=instance_name,
            token=tenant.get("token"),
            webhook_url=webhook_url,
            webhook_events=events,
        )
        logger.info(f"Evolution instance created: {create_data}")

        # Extrai apikey da resposta (pode vir em formatos distintos)
        api_key = None
        if isinstance(create_data, dict):
            api_key = create_data.get("hash", {}).get("apikey") or create_data.get("apikey")

        # 2. Configura webhook explicitamente (garantia)
        await evolution.set_webhook(
            instance_name=instance_name,
            url=webhook_url,
            enabled=True,
            events=events,
        )

        # 3. Solicita conexão / QR code
        connect_data = await evolution.connect_instance(instance_name)

        # 4. Persiste no tenant
        update_data = {
            "evolution_instance_name": instance_name,
            "evolution_status": "connecting",
        }
        if api_key:
            update_data["evolution_api_key"] = api_key

        updated_tenant = await tenant_repo.update(tenant_id, update_data)

        return {
            "message": "Tenant connected to Evolution API successfully",
            "tenant_id": tenant_id,
            "instance_name": instance_name,
            "api_key": api_key,
            "qr_code": connect_data,
            "tenant": updated_tenant,
        }
    except EvolutionServiceError as exc:
        logger.error(f"Error connecting tenant {tenant_id} to Evolution API: {exc}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Evolution API error: {exc}",
        ) from exc
    except Exception as exc:
        logger.error(f"Unexpected error connecting tenant {tenant_id}: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error"
        ) from exc
