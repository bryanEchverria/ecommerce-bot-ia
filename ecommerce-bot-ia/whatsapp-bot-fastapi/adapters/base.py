from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class WhatsAppAdapter(ABC):
    """Interfaz base para adapters de WhatsApp"""
    
    @abstractmethod
    async def send_text(self, to: str, text: str) -> bool:
        """
        Envía un mensaje de texto
        
        Args:
            to: Número de teléfono destino (formato E.164 con +)
            text: Texto del mensaje
            
        Returns:
            bool: True si el envío fue exitoso
        """
        pass
    
    @abstractmethod
    async def send_template(
        self, 
        to: str, 
        template_name: str, 
        lang: str = "es", 
        components: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Envía un mensaje de template
        
        Args:
            to: Número de teléfono destino (formato E.164 con +)
            template_name: Nombre del template
            lang: Código de idioma
            components: Componentes del template (headers, body, buttons)
            
        Returns:
            bool: True si el envío fue exitoso
        """
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """Retorna el nombre del proveedor"""
        pass