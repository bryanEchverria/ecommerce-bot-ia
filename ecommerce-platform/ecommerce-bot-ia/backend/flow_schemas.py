"""
Schemas para configuración Flow multi-tenant
"""
from pydantic import BaseModel, SecretStr
from typing import Optional

class FlowConfigIn(BaseModel):
    """Input para configuración Flow"""
    api_key: str
    secret_key: SecretStr
    base_url: Optional[str] = "https://sandbox.flow.cl/api"
    webhook_base_url: Optional[str] = None

class FlowConfigOut(BaseModel):
    """Output para configuración Flow"""
    tenant_id: str
    api_key: str
    base_url: str
    webhook_base_url: Optional[str] = None
    confirm_url: str
    return_url: str
    environment: str = "sandbox"
    status: str = "active"

class FlowWebhookUrls(BaseModel):
    """Response para URLs de webhooks Flow"""
    confirm_url: str
    return_url: str
    tenant_slug: str
    environment: str = "sandbox"

class PaymentMethodsConfigOut(BaseModel):
    """Output combinado para configuración de métodos de pago"""
    twilio_config: Optional[dict] = None
    flow_config: Optional[dict] = None
    tenant_id: str
    tenant_slug: str