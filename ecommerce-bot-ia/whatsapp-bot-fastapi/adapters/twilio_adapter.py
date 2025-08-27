import os
import httpx
import logging
from typing import Dict, Any, Optional
from .base import WhatsAppAdapter

logger = logging.getLogger(__name__)

class TwilioAdapter(WhatsAppAdapter):
    """Adapter para Twilio WhatsApp API"""
    
    def __init__(self):
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.whatsapp_number = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")
        
        if not self.account_sid or not self.auth_token:
            raise ValueError("TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN must be set")
    
    async def send_text(self, to: str, text: str) -> bool:
        """Envía un mensaje de texto usando Twilio API"""
        try:
            # Normalizar número de teléfono
            if not to.startswith('whatsapp:'):
                if not to.startswith('+'):
                    to = '+' + to
                to = f'whatsapp:{to}'
            
            async with httpx.AsyncClient() as client:
                auth = (self.account_sid, self.auth_token)
                
                data = {
                    'To': to,
                    'From': self.whatsapp_number,
                    'Body': text
                }
                
                response = await client.post(
                    f'https://api.twilio.com/2010-04-01/Accounts/{self.account_sid}/Messages.json',
                    auth=auth,
                    data=data
                )
                
                if response.status_code == 201:
                    logger.info(f"Twilio message sent successfully to {to}")
                    return True
                else:
                    logger.error(f"Twilio failed to send message: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Twilio error sending message: {str(e)}")
            return False
    
    async def send_template(
        self, 
        to: str, 
        template_name: str, 
        lang: str = "es", 
        components: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Envía un template usando Twilio
        Nota: Twilio maneja templates de forma diferente a Meta
        """
        try:
            # Normalizar número de teléfono
            if not to.startswith('whatsapp:'):
                if not to.startswith('+'):
                    to = '+' + to
                to = f'whatsapp:{to}'
            
            async with httpx.AsyncClient() as client:
                auth = (self.account_sid, self.auth_token)
                
                # Para Twilio, usamos ContentSid en lugar de template personalizado
                data = {
                    'To': to,
                    'From': self.whatsapp_number,
                }
                
                # Si tenemos un ContentSid específico para el template
                content_sid = self._get_content_sid(template_name)
                if content_sid:
                    data['ContentSid'] = content_sid
                    if components:
                        # Convertir components a formato Twilio
                        data['ContentVariables'] = self._format_twilio_variables(components)
                else:
                    # Fallback: enviar como mensaje de texto simple
                    data['Body'] = f"Template: {template_name}"
                
                response = await client.post(
                    f'https://api.twilio.com/2010-04-01/Accounts/{self.account_sid}/Messages.json',
                    auth=auth,
                    data=data
                )
                
                if response.status_code == 201:
                    logger.info(f"Twilio template sent successfully to {to}")
                    return True
                else:
                    logger.error(f"Twilio failed to send template: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Twilio error sending template: {str(e)}")
            return False
    
    def _get_content_sid(self, template_name: str) -> Optional[str]:
        """Mapea nombres de templates a ContentSid de Twilio"""
        # Mapeo de templates comunes - puedes expandir según tus templates
        template_map = {
            "welcome": os.getenv("TWILIO_WELCOME_TEMPLATE_SID"),
            "order_confirmation": os.getenv("TWILIO_ORDER_TEMPLATE_SID"),
            "payment_reminder": os.getenv("TWILIO_PAYMENT_TEMPLATE_SID"),
        }
        return template_map.get(template_name)
    
    def _format_twilio_variables(self, components: Dict[str, Any]) -> str:
        """Convierte components a formato JSON para Twilio ContentVariables"""
        import json
        try:
            # Simplificar components para formato Twilio
            variables = {}
            if 'body' in components and isinstance(components['body'], list):
                for i, param in enumerate(components['body']):
                    if isinstance(param, dict) and 'text' in param:
                        variables[f'body_{i+1}'] = param['text']
            return json.dumps(variables)
        except Exception:
            return "{}"
    
    def get_provider_name(self) -> str:
        return "twilio"