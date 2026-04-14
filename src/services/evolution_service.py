from typing import List, Optional

import httpx

from src.core.config import settings


class EvolutionServiceError(Exception):
    """Exceção customizada para erros no serviço da Evolution API."""

    pass


class EvolutionService:
    """Cliente de serviço para interagir com a Evolution API."""

    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None):
        self.base_url = (base_url or settings.EVOLUTION_API_URL).rstrip("/")
        self.api_key = api_key or settings.EVOLUTION_API_KEY
        self.headers = {
            "apikey": self.api_key,
            "Content-Type": "application/json",
        }

    def _handle_response(self, response: httpx.Response) -> dict:
        """Processa a resposta HTTP e extrai dados ou mensagens de erro."""
        try:
            data = response.json()
        except Exception as exc:
            raise EvolutionServiceError(f"Resposta inválida da API: {response.text}") from exc

        if response.status_code >= 400 or data.get("error"):
            msg = (
                data.get("response", {}).get("message")
                if isinstance(data.get("response"), dict)
                else None
            )
            if not msg:
                msg = data.get("message", data)
            raise EvolutionServiceError(msg)
        return data

    async def create_instance(
        self,
        instance_name: str,
        integration: str = "WHATSAPP-BAILEYS",
        qrcode: bool = True,
        token: Optional[str] = None,
        webhook_url: Optional[str] = None,
        webhook_events: Optional[List[str]] = None,
    ) -> dict:
        """Cria uma nova instância na Evolution API."""
        payload: dict = {
            "instanceName": instance_name,
            "integration": integration,
            "qrcode": qrcode,
        }
        if token:
            payload["token"] = token
        if webhook_url:
            payload["webhook"] = {
                "enabled": True,
                "url": webhook_url,
                "events": webhook_events or [],
            }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/instance/create",
                    headers=self.headers,
                    json=payload,
                    timeout=30.0,
                )
                return self._handle_response(response)
        except httpx.TimeoutException as exc:
            raise EvolutionServiceError(
                "Tempo esgotado ao criar instância na Evolution API."
            ) from exc
        except httpx.HTTPError as exc:
            raise EvolutionServiceError(f"Erro de comunicação com a Evolution API: {exc}") from exc

    async def connect_instance(self, instance_name: str) -> dict:
        """Obtém o QR code ou estado de conexão de uma instância."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/instance/connect/{instance_name}",
                    headers=self.headers,
                    timeout=30.0,
                )
                return self._handle_response(response)
        except httpx.TimeoutException as exc:
            raise EvolutionServiceError("Tempo esgotado ao conectar instância.") from exc
        except httpx.HTTPError as exc:
            raise EvolutionServiceError(f"Erro de comunicação com a Evolution API: {exc}") from exc

    async def set_webhook(
        self,
        instance_name: str,
        url: str,
        enabled: bool = True,
        events: Optional[List[str]] = None,
    ) -> dict:
        """Configura o webhook de uma instância."""
        payload = {
            "webhook": {
                "enabled": enabled,
                "url": url,
                "events": events or [],
            }
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/webhook/set/{instance_name}",
                    headers=self.headers,
                    json=payload,
                    timeout=30.0,
                )
                return self._handle_response(response)
        except httpx.TimeoutException as exc:
            raise EvolutionServiceError("Tempo esgotado ao configurar webhook.") from exc
        except httpx.HTTPError as exc:
            raise EvolutionServiceError(f"Erro de comunicação com a Evolution API: {exc}") from exc

    async def send_text(
        self,
        instance_name: str,
        number: str,
        text: str,
        delay: int = 1200,
    ) -> dict:
        """Envia uma mensagem de texto via instância informada."""
        payload = {
            "number": number,
            "text": text,
            "delay": delay,
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/message/sendText/{instance_name}",
                    headers=self.headers,
                    json=payload,
                    timeout=30.0,
                )
                return self._handle_response(response)
        except httpx.TimeoutException as exc:
            raise EvolutionServiceError(
                "Tempo esgotado ao enviar mensagem." " A instância pode estar desconectada."
            ) from exc
        except httpx.HTTPError as exc:
            raise EvolutionServiceError(f"Erro de comunicação com a Evolution API: {exc}") from exc
