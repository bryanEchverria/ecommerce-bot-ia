import logging
from typing import Optional, Dict, Any
import sys
from pathlib import Path

# Add parent directory to path to import settings
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.append(str(parent_dir))

from settings import get_adapter

logger = logging.getLogger(__name__)

class MessagingService:
    """Servicio de mensajería unificado para WhatsApp"""
    
    @staticmethod
    async def send_text(to: str, text: str, tenant_id: Optional[str] = None) -> bool:
        """
        Envía un mensaje de texto
        
        Args:
            to: Número de teléfono destino
            text: Texto del mensaje
            tenant_id: ID del tenant (opcional, para futuro uso)
            
        Returns:
            bool: True si el envío fue exitoso
        """
        try:
            adapter = get_adapter(tenant_id)
            result = await adapter.send_text(to, text)
            
            if result:
                logger.info(f"Message sent successfully via {adapter.get_provider_name()} to {to}")
            else:
                logger.error(f"Failed to send message via {adapter.get_provider_name()} to {to}")
                
            return result
            
        except Exception as e:
            logger.error(f"Error in messaging service send_text: {str(e)}")
            return False
    
    @staticmethod
    async def send_template(
        to: str, 
        template_name: str, 
        lang: str = "es", 
        components: Optional[Dict[str, Any]] = None,
        tenant_id: Optional[str] = None
    ) -> bool:
        """
        Envía un template de mensaje
        
        Args:
            to: Número de teléfono destino
            template_name: Nombre del template
            lang: Código de idioma (default: "es")
            components: Componentes del template (headers, body, buttons)
            tenant_id: ID del tenant (opcional, para futuro uso)
            
        Returns:
            bool: True si el envío fue exitoso
        """
        try:
            adapter = get_adapter(tenant_id)
            result = await adapter.send_template(to, template_name, lang, components)
            
            if result:
                logger.info(f"Template {template_name} sent successfully via {adapter.get_provider_name()} to {to}")
            else:
                logger.error(f"Failed to send template {template_name} via {adapter.get_provider_name()} to {to}")
                
            return result
            
        except Exception as e:
            logger.error(f"Error in messaging service send_template: {str(e)}")
            return False
    
    @staticmethod
    def get_current_provider(tenant_id: Optional[str] = None) -> str:
        """
        Obtiene el nombre del proveedor actual
        
        Args:
            tenant_id: ID del tenant (opcional, para futuro uso)
            
        Returns:
            str: Nombre del proveedor actual
        """
        try:
            adapter = get_adapter(tenant_id)
            return adapter.get_provider_name()
        except Exception as e:
            logger.error(f"Error getting current provider: {str(e)}")
            return "unknown"

# Funciones de conveniencia para mantener compatibilidad
async def send_text(to: str, text: str, tenant_id: Optional[str] = None) -> bool:
    """Función de conveniencia para enviar texto"""
    return await MessagingService.send_text(to, text, tenant_id)

async def send_template(
    to: str, 
    template_name: str, 
    lang: str = "es", 
    components: Optional[Dict[str, Any]] = None,
    tenant_id: Optional[str] = None
) -> bool:
    """Función de conveniencia para enviar template"""
    return await MessagingService.send_template(to, template_name, lang, components, tenant_id)