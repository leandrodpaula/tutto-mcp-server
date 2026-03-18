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
    
    print(f"Initializing {len(plans)} plans...", flush=True)
    for plan in plans:
        existing = await repo.get_by_name(plan.name)
        if existing:
            print(f"Plan '{plan.name}' exists. Updating...", flush=True)
            update_data = PlanUpdate(
                title=plan.title,
                description=plan.description,
                price=plan.price,
                is_active=plan.is_active,
                features=plan.features,
                change_reason="Initialize/Update default plans"
            )
            updated = await repo.update(str(existing["id"]), update_data)
            print(f"Updated plan: {updated['title']} ({updated['name']})", flush=True)
        else:
            try:
                created = await repo.create(plan)
                print(f"Created plan: {created['title']} ({created['name']})", flush=True)
            except Exception as e:
                print(f"Error creating plan '{plan.name}': {str(e)}", flush=True)

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
    
    print(f"Initializing {len(coupons)} coupons...", flush=True)
    for coupon in coupons:
        existing = await repo.get_by_short_code(coupon.short_code)
        if existing:
            print(f"Coupon '{coupon.short_code}' exists. Updating...", flush=True)
            update_data = CouponUpdate(
                title=coupon.title,
                description=coupon.description,
                ttl=coupon.ttl,
                is_active=coupon.is_active
            )
            updated = await repo.update(str(existing["id"]), update_data)
            print(f"Updated coupon: {updated['short_code']}", flush=True)
        else:
            try:
                created = await repo.create(coupon)
                print(f"Created coupon: {created['short_code']}", flush=True)
            except Exception as e:
                print(f"Error creating coupon '{coupon.short_code}': {str(e)}", flush=True)

async def main():
    print(f"Connecting to MongoDB at {settings.MONGODB_DATABASE_NAME}...", flush=True)
    await connect_to_mongo()
    
    if db_manager.db is None:
        print("Failed to connect to database.", flush=True)
        sys.exit(1)

    print("\n--- Initializing Plans ---", flush=True)
    await init_plans(db_manager.db)
    
    print("\n--- Initializing Coupons ---", flush=True)
    await init_coupons(db_manager.db)
    
    print("\nInitialization complete.", flush=True)

if __name__ == "__main__":
    asyncio.run(main())
