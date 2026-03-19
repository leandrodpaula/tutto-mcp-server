import asyncio
import sys
import os
from datetime import datetime

# Add the project root to sys.path to allow importing from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv
load_dotenv() # Load from .env

from src.core.database import connect_to_mongo, db_manager
from src.repositories.plan_repository import PlanRepository
from src.repositories.coupon_repository import CouponRepository
from src.models.plan import PlanCreate, PlanUpdate
from src.models.coupon import CouponCreate, CouponUpdate
from src.core.config import settings
from src.core.logging import get_logger, setup_logging

# Initialize logging for the script
setup_logging()
logger = get_logger("init_database")

async def init_plans(db):
    repo = PlanRepository(db)
    
    plans = [
        PlanCreate(
            name="silver",
            title="Plano Silver",
            description=(
                "Gestão completa de agendamentos e treinamento do Agent sobre a barbearia."
            ),
            price=15.90,
            is_active=True,
            features=[
                "Agendamento de serviços",
                "Alteração de agendamentos",
                "Cancelamento de agendamentos",
                "Instruir Agent sobre serviços e produtos"
            ]
        ),
        PlanCreate(
            name="gold",
            title="Plano Gold",
            description=(
                "Tudo do plano Silver + Módulo de Marketing e Engajamento automático."
            ),
            price=39.90,
            is_active=True,
            features=[
                "Agendamento de serviços",
                "Alteração de agendamentos",
                "Cancelamento de agendamentos",
                "Instruir Agent sobre serviços e produtos",
                "Marketing Automático",
                "Campanhas de engajamento (Datas comemorativas)",
                "Envio de mensagens automáticas para clientes"
            ]
        )
    ]
    
    logger.info(f"Initializing {len(plans)} plans...")
    for plan in plans:
        existing = await repo.get_by_name(plan.name)
        if existing:
            logger.info(f"Plan '{plan.name}' exists. Updating...")
            update_data = PlanUpdate(
                title=plan.title,
                description=plan.description,
                price=plan.price,
                is_active=plan.is_active,
                features=plan.features,
                change_reason="Initialize/Update default plans"
            )
            updated = await repo.update(str(existing["id"]), update_data)
            logger.info(f"Updated plan: {updated['title']} ({updated['name']})")
        else:
            try:
                created = await repo.create(plan)
                logger.info(f"Created plan: {created['title']} ({created['name']})")
            except Exception as e:
                logger.error(f"Error creating plan '{plan.name}': {str(e)}")

async def init_coupons(db):
    repo = CouponRepository(db)
    
    coupons = [
        CouponCreate(
            short_code="FIRST",
            title="Primeira Experiência",
            description="Período de teste gratuito para novos usuários.",
            ttl=7, # 7 dias
            is_active=True
        )
    ]
    
    logger.info(f"Initializing {len(coupons)} coupons...")
    for coupon in coupons:
        existing = await repo.get_by_short_code(coupon.short_code)
        if existing:
            logger.info(f"Coupon '{coupon.short_code}' exists. Updating...")
            update_data = CouponUpdate(
                title=coupon.title,
                description=coupon.description,
                ttl=coupon.ttl,
                is_active=coupon.is_active
            )
            updated = await repo.update(str(existing["id"]), update_data)
            logger.info(f"Updated coupon: {updated['short_code']}")
        else:
            try:
                created = await repo.create(coupon)
                logger.info(f"Created coupon: {created['short_code']}")
            except Exception as e:
                logger.error(f"Error creating coupon '{coupon.short_code}': {str(e)}")

async def main():
    logger.info(f"Connecting to MongoDB at {settings.MONGODB_DATABASE_NAME}...")
    await connect_to_mongo()
    
    if db_manager.db is None:
        logger.error("Failed to connect to database.")
        sys.exit(1)

    logger.info("--- Initializing Plans ---")
    await init_plans(db_manager.db)
    
    logger.info("--- Initializing Coupons ---")
    await init_coupons(db_manager.db)
    
    logger.info("Initialization complete.")

if __name__ == "__main__":
    asyncio.run(main())
