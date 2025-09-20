"""
Adapters para diferentes proveedores de WhatsApp
"""
from .base import WhatsAppAdapter
from .twilio_adapter import TwilioAdapter
from .meta_adapter import MetaAdapter

__all__ = ["WhatsAppAdapter", "TwilioAdapter", "MetaAdapter"]