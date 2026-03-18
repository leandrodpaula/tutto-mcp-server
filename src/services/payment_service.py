import mercadopago
from src.core.config import settings
from typing import Dict, Any

class PaymentService:
    def __init__(self):
        self.sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)

    async def create_payment_link(self, tenant_id: str, plan_name: str, price: float) -> str:
        """
        Creates a Mercado Pago preference and returns the init_point (payment link).
        """
        if price <= 0:
            return "No payment required for this plan."

        preference_data: Dict[str, Any] = {
            "items": [
                {
                    "title": f"Assinatura Tutto MCP - Plano {plan_name.capitalize()}",
                    "quantity": 1,
                    "unit_price": price,
                    "currency_id": "BRL"
                }
            ],
            "external_reference": tenant_id,
            "back_urls": {
                "success": f"{settings.MERCADO_PAGO_BACK_URL_BASE}/success",
                "failure": f"{settings.MERCADO_PAGO_BACK_URL_BASE}/failure",
                "pending": f"{settings.MERCADO_PAGO_BACK_URL_BASE}/pending"
            },
            "auto_return": "approved",
        }

        # The SDK is synchronous, but we can call it in a thread if needed. 
        # For simplicity in this MCP server, we'll call it directly as it's usually fast.
        preference_response = self.sdk.preference().create(preference_data)
        
        if preference_response["status"] >= 400:
            raise Exception(f"Mercado Pago error: {preference_response['response']}")
            
        return preference_response["response"]["init_point"]
