import os
import httpx
import logging
from typing import Dict, Any, Optional
from .base import WhatsAppAdapter

logger = logging.getLogger(__name__)

class MetaAdapter(WhatsAppAdapter):
    """Adapter para Meta WhatsApp Cloud API"""
    
    def __init__(self):
        self.token = os.getenv("WHATSAPP_TOKEN")
        self.phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
        self.graph_api_version = os.getenv("GRAPH_API_VERSION", "v21.0")
        
        if not self.token or not self.phone_number_id:
            raise ValueError("WHATSAPP_TOKEN and WHATSAPP_PHONE_NUMBER_ID must be set")
        
        self.base_url = f"https://graph.facebook.com/{self.graph_api_version}/{self.phone_number_id}/messages"
    
    async def send_text(self, to: str, text: str) -> bool:
        """Envía un mensaje de texto usando Meta WhatsApp Cloud API"""
        try:
            # Normalizar número de teléfono (remover whatsapp: si existe)
            if to.startswith('whatsapp:'):
                to = to.replace('whatsapp:', '')
            if not to.startswith('+'):
                to = '+' + to
            
            async with httpx.AsyncClient() as client:
                headers = {
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "messaging_product": "whatsapp",
                    "to": to,
                    "type": "text",
                    "text": {
                        "body": text
                    }
                }
                
                response = await client.post(
                    self.base_url,
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    logger.info(f"Meta message sent successfully to {to}")
                    return True
                else:
                    logger.error(f"Meta failed to send message: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Meta error sending message: {str(e)}")
            return False
    
    async def send_template(
        self, 
        to: str, 
        template_name: str, 
        lang: str = "es", 
        components: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Envía un template usando Meta WhatsApp Cloud API"""
        try:
            # Normalizar número de teléfono
            if to.startswith('whatsapp:'):
                to = to.replace('whatsapp:', '')
            if not to.startswith('+'):
                to = '+' + to
            
            async with httpx.AsyncClient() as client:
                headers = {
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json"
                }
                
                # Construir payload del template
                template_payload = {
                    "name": template_name,
                    "language": {
                        "code": lang
                    }
                }
                
                # Agregar componentes si existen
                if components:
                    template_components = []
                    
                    # Header component
                    if "header" in components:
                        header_component = {
                            "type": "header"
                        }
                        if isinstance(components["header"], list):
                            header_component["parameters"] = components["header"]
                        template_components.append(header_component)
                    
                    # Body component
                    if "body" in components:
                        body_component = {
                            "type": "body"
                        }
                        if isinstance(components["body"], list):
                            body_component["parameters"] = components["body"]
                        template_components.append(body_component)
                    
                    # Button component
                    if "buttons" in components:
                        for i, button in enumerate(components["buttons"]):
                            button_component = {
                                "type": "button",
                                "sub_type": button.get("type", "quick_reply"),
                                "index": str(i)
                            }
                            if "parameters" in button:
                                button_component["parameters"] = button["parameters"]
                            template_components.append(button_component)
                    
                    if template_components:
                        template_payload["components"] = template_components
                
                payload = {
                    "messaging_product": "whatsapp",
                    "to": to,
                    "type": "template",
                    "template": template_payload
                }
                
                response = await client.post(
                    self.base_url,
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    logger.info(f"Meta template sent successfully to {to}")
                    return True
                else:
                    logger.error(f"Meta failed to send template: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Meta error sending template: {str(e)}")
            return False
    
    async def send_interactive_buttons(
        self,
        to: str,
        body_text: str,
        buttons: list,
        header_text: Optional[str] = None,
        footer_text: Optional[str] = None
    ) -> bool:
        """
        Envía un mensaje con botones interactivos
        
        Args:
            to: Número de teléfono destino
            body_text: Texto principal del mensaje
            buttons: Lista de botones [{"id": "btn1", "title": "Botón 1"}, ...]
            header_text: Texto del encabezado (opcional)
            footer_text: Texto del pie (opcional)
            
        Returns:
            bool: True si el envío fue exitoso
        """
        try:
            # Normalizar número de teléfono
            if to.startswith('whatsapp:'):
                to = to.replace('whatsapp:', '')
            if not to.startswith('+'):
                to = '+' + to
            
            async with httpx.AsyncClient() as client:
                headers = {
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json"
                }
                
                # Construir estructura del mensaje interactivo
                interactive = {
                    "type": "button",
                    "body": {"text": body_text}
                }
                
                # Agregar header si existe
                if header_text:
                    interactive["header"] = {
                        "type": "text",
                        "text": header_text
                    }
                
                # Agregar footer si existe
                if footer_text:
                    interactive["footer"] = {"text": footer_text}
                
                # Construir botones (máximo 3 para Meta)
                interactive_buttons = []
                for i, button in enumerate(buttons[:3]):  # Meta permite máx 3 botones
                    interactive_buttons.append({
                        "type": "reply",
                        "reply": {
                            "id": button.get("id", f"btn_{i}"),
                            "title": button.get("title", f"Opción {i+1}")
                        }
                    })
                
                interactive["action"] = {"buttons": interactive_buttons}
                
                payload = {
                    "messaging_product": "whatsapp",
                    "to": to,
                    "type": "interactive",
                    "interactive": interactive
                }
                
                response = await client.post(
                    self.base_url,
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    logger.info(f"Meta interactive buttons sent successfully to {to}")
                    return True
                else:
                    logger.error(f"Meta failed to send interactive buttons: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Meta error sending interactive buttons: {str(e)}")
            return False
    
    def get_provider_name(self) -> str:
        return "meta"