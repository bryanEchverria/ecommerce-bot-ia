"""
Schemas para configuración Twilio multi-tenant
"""
from pydantic import BaseModel, SecretStr
from typing import Optional

class TwilioConfigIn(BaseModel):
    """Input para configuración Twilio"""
    account_sid: str
    auth_token: SecretStr
    from_number: Optional[str] = None

class TwilioConfigOut(BaseModel):
    """Output para configuración Twilio"""
    tenant_id: str
    account_sid: str
    from_number: Optional[str] = None
    webhook_url: str
    status: str = "active"

class TwilioWebhookUrl(BaseModel):
    """Response para webhook URL"""
    webhook_url: str
    tenant_slug: str