from typing import List, Optional

from fastmcp import FastMCP

from src.core.logging import get_logger
from src.services.evolution_service import EvolutionService, EvolutionServiceError

logger = get_logger(__name__)


def register_whatsapp_tools(mcp: FastMCP) -> None:
    """Registra as tools de integração com a WhatsApp via Evolution API."""

    @mcp.tool()
    async def create_whatsapp_instance(
        instance_name: str,
        integration: str = "WHATSAPP-BAILEYS",
        qrcode: bool = True,
        token: Optional[str] = None,
        webhook_url: Optional[str] = None,
    ) -> str:
        """
        Cria uma nova instância de WhatsApp na Evolution API.

        Args:
            instance_name: Nome único da instância.
            integration: Tipo de integração (padrão: WHATSAPP-BAILEYS).
            qrcode: Se deve gerar QR code na criação.
            token: Token customizado da instância (opcional).
            webhook_url: URL do webhook a ser configurado na criação (opcional).

        Returns:
            Mensagem de sucesso com hash da instância criada.
        """
        try:
            service = EvolutionService()
            result = await service.create_instance(
                instance_name=instance_name,
                integration=integration,
                qrcode=qrcode,
                token=token,
                webhook_url=webhook_url,
            )
            qr_info = ""
            if result.get("qrcode") and result["qrcode"].get("base64"):
                qr_info = (
                    " QR Code gerado na criação." " Use connect_whatsapp_instance para visualizar."
                )
            return (
                f"Instância '{instance_name}' criada com sucesso."
                f" Hash: {result.get('hash')}.{qr_info}"
            )
        except EvolutionServiceError as e:
            logger.error(f"Erro ao criar instância {instance_name}: {str(e)}")
            raise

    @mcp.tool()
    async def connect_whatsapp_instance(instance_name: str) -> str:
        """
        Obtém o QR code ou o estado de conexão de uma instância de WhatsApp.

        Args:
            instance_name: Nome da instância.

        Returns:
            QR code em base64 ou status da conexão.
        """
        try:
            service = EvolutionService()
            result = await service.connect_instance(instance_name)
            qrcode = result.get("qrcode", {})
            if qrcode and qrcode.get("base64"):
                return (
                    f"QR Code para conexão da instância '{instance_name}':\n" f"{qrcode['base64']}"
                )
            status = result.get("instance", {}).get("status", "desconhecido")
            return (
                f"Status da instância '{instance_name}': {status}."
                " Nenhum QR code disponível no momento."
            )
        except EvolutionServiceError as e:
            logger.error(f"Erro ao conectar instância {instance_name}: {str(e)}")
            raise

    @mcp.tool()
    async def set_whatsapp_webhook(
        instance_name: str,
        webhook_url: str,
        enabled: bool = True,
        events: Optional[List[str]] = None,
    ) -> str:
        """
        Configura o webhook de uma instância de WhatsApp existente.

        Args:
            instance_name: Nome da instância.
            webhook_url: URL para onde os eventos serão enviados.
            enabled: Se o webhook deve estar ativo.
            events: Lista de eventos a serem escutados (opcional).

        Returns:
            Mensagem de confirmação.
        """
        try:
            service = EvolutionService()
            result = await service.set_webhook(
                instance_name=instance_name,
                url=webhook_url,
                enabled=enabled,
                events=events,
            )
            return (
                f"Webhook configurado com sucesso para a instância" f" '{instance_name}': {result}"
            )
        except EvolutionServiceError as e:
            logger.error(f"Erro ao configurar webhook para {instance_name}: {str(e)}")
            raise

    @mcp.tool()
    async def send_whatsapp_text_message(
        instance_name: str,
        number: str,
        text: str,
        delay: int = 1200,
    ) -> str:
        """
        Envia uma mensagem de texto via instância de WhatsApp da Evolution API.

        Args:
            instance_name: Nome da instância que enviará a mensagem.
            number: Número do destinatário (com código do país, ex: 5511999999999).
            text: Conteúdo da mensagem.
            delay: Delay em ms antes do envio (padrão: 1200).

        Returns:
            Mensagem de confirmação de envio.
        """
        try:
            service = EvolutionService()
            result = await service.send_text(
                instance_name=instance_name,
                number=number,
                text=text,
                delay=delay,
            )
            return f"Mensagem enviada com sucesso pela instância" f" '{instance_name}': {result}"
        except EvolutionServiceError as e:
            logger.error(f"Erro ao enviar mensagem pela instância {instance_name}: {str(e)}")
            raise
