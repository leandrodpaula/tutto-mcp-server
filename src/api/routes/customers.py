"""Rotas HTTP para cadastro e consulta de Customers."""

from fastapi import APIRouter, Depends, HTTPException, status
from src.api.auth import require_auth, require_customer_auth
from motor.motor_asyncio import AsyncIOMotorDatabase
from src.api.deps import get_db
from src.core.logging import get_logger
from src.models.customer import CustomerCreate, CustomerOut
from src.repositories.customer_repository import CustomerRepository
from src.services.customer_service import CustomerService, CustomerServiceError

logger = get_logger(__name__)
router = APIRouter(prefix="/customers", tags=["customers"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def register_customer(
    payload: CustomerCreate,
    db: AsyncIOMotorDatabase = Depends(get_db),  # noqa: B008
    identity: dict = Depends(require_auth),  # noqa: B008
) -> dict:
    """Cadastra um novo customer vinculado a um tenant."""
    try:
        repo = CustomerRepository(db)
        service = CustomerService(repo)
        customer = await service.register(payload.model_dump())
        return {
            "message": "Customer registered successfully",
            "customer": CustomerOut(**customer).model_dump(by_alias=True),
        }
    except CustomerServiceError as exc:
        logger.warning(f"Customer registration failed: {exc}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception as exc:
        logger.error(f"Unexpected error registering customer: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error"
        ) from exc


@router.get("/")
async def get_customer(
    customer: dict = Depends(require_customer_auth),  # noqa: B008
) -> dict:
    """Retorna o profile do customer autenticado via JWT."""
    return {
        "customer": CustomerOut(**customer).model_dump(by_alias=True),
    }
