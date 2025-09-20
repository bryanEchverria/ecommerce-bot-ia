from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime

# Base schemas para configuración por proveedor
class TwilioSettings(BaseModel):
    """Configuración específica de Twilio"""
    account_sid: str = Field(..., description="Twilio Account SID")
    auth_token: str = Field(..., description="Twilio Auth Token")
    from_number: str = Field(..., description="Número WhatsApp de Twilio (ej: whatsapp:+14155238886)")

class MetaSettings(BaseModel):
    """Configuración específica de Meta WhatsApp Cloud API"""
    token: str = Field(..., description="Meta WhatsApp Business Token")
    phone_number_id: str = Field(..., description="ID del número de teléfono de Meta")
    graph_api_version: str = Field(default="v21.0", description="Versión de Graph API")

# Schemas principales
class WhatsAppSettingsBase(BaseModel):
    """Base para configuración global de WhatsApp"""
    provider: Literal["twilio", "meta"] = Field(..., description="Proveedor de WhatsApp")
    is_active: bool = Field(default=True, description="Si el canal está activo")

class WhatsAppSettingsCreate(WhatsAppSettingsBase):
    """Schema para crear configuración de WhatsApp"""
    twilio_settings: Optional[TwilioSettings] = None
    meta_settings: Optional[MetaSettings] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "provider": "meta",
                "is_active": True,
                "meta_settings": {
                    "token": "EAAG...",
                    "phone_number_id": "123456789012345",
                    "graph_api_version": "v21.0"
                }
            }
        }

class WhatsAppSettingsUpdate(BaseModel):
    """Schema para actualizar configuración de WhatsApp"""
    provider: Optional[Literal["twilio", "meta"]] = None
    is_active: Optional[bool] = None
    twilio_settings: Optional[TwilioSettings] = None
    meta_settings: Optional[MetaSettings] = None

class WhatsAppSettingsResponse(WhatsAppSettingsBase):
    """Schema para respuesta de configuración (sin exponer tokens)"""
    id: int
    
    # Flags de configuración sin exponer tokens reales
    has_twilio_config: bool = Field(description="Si tiene configuración de Twilio")
    has_meta_config: bool = Field(description="Si tiene configuración de Meta")
    
    # Campos públicos de configuración
    twilio_from: Optional[str] = None
    meta_phone_number_id: Optional[str] = None
    meta_graph_api_version: Optional[str] = None
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class WhatsAppTestRequest(BaseModel):
    """Schema para probar configuración de WhatsApp"""
    phone_number: str = Field(..., description="Número de teléfono para prueba (ej: +56912345678)")
    message: Optional[str] = Field(default="Mensaje de prueba desde configuración WhatsApp", description="Mensaje de prueba")

class WhatsAppTestResponse(BaseModel):
    """Schema para respuesta de prueba"""
    success: bool
    provider_used: str
    message: str
    details: Optional[dict] = None

# Schemas para listado y configuración por tenant
class WhatsAppProviderStatus(BaseModel):
    """Status de un proveedor específico"""
    name: str
    available: bool
    configured: bool
    error: Optional[str] = None

class WhatsAppProvidersInfo(BaseModel):
    """Información de proveedores disponibles"""
    current_provider: str
    providers: dict[str, WhatsAppProviderStatus]