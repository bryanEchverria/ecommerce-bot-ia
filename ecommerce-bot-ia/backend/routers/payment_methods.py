"""
Router para configuración de métodos de pago (Twilio + Flow)
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
import logging

from database import get_db
from models import TwilioAccount, FlowAccount
from auth_models import TenantClient
from flow_schemas import PaymentMethodsConfigOut
from tenant_middleware import get_tenant_id

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/payment-methods", tags=["payment-methods"])

def _get_tenant_slug(db: Session, tenant_id_str: str) -> Optional[str]:
    """Get tenant slug from tenant_id string"""
    row = db.query(TenantClient).filter(TenantClient.id == tenant_id_str).one_or_none()
    return row.slug if row else None

@router.get("/config", response_model=PaymentMethodsConfigOut)
async def get_payment_methods_config(db: Session = Depends(get_db)):
    """Obtener configuración completa de métodos de pago del tenant actual"""
    tenant_id_str = get_tenant_id()
    
    tenant_slug = _get_tenant_slug(db, tenant_id_str)
    if not tenant_slug:
        raise HTTPException(status_code=404, detail="Tenant slug not found")
    
    # Get Twilio configuration
    twilio_account = db.query(TwilioAccount).filter(TwilioAccount.tenant_id == tenant_id_str).one_or_none()
    twilio_config = None
    if twilio_account:
        twilio_config = {
            "account_sid": twilio_account.account_sid,
            "from_number": twilio_account.from_number,
            "webhook_url": f"https://{tenant_slug}.sintestesia.cl/bot/twilio/webhook",
            "status": twilio_account.status
        }
    
    # Get Flow configuration
    flow_account = db.query(FlowAccount).filter(FlowAccount.tenant_id == tenant_id_str).one_or_none()
    flow_config = None
    if flow_account:
        webhook_base = flow_account.webhook_base_url if flow_account.webhook_base_url else "https://webhook.sintestesia.cl"
        environment = "production" if "flow.cl/api" in flow_account.base_url and "sandbox" not in flow_account.base_url else "sandbox"
        
        flow_config = {
            "api_key": flow_account.api_key,
            "base_url": flow_account.base_url,
            "webhook_base_url": flow_account.webhook_base_url,
            "confirm_url": f"{webhook_base}/flow/confirm",
            "return_url": f"{webhook_base}/flow/return",
            "environment": environment,
            "status": flow_account.status
        }
    
    return PaymentMethodsConfigOut(
        twilio_config=twilio_config,
        flow_config=flow_config,
        tenant_id=tenant_id_str,
        tenant_slug=tenant_slug
    )

@router.get("/status")
async def get_payment_methods_status(db: Session = Depends(get_db)):
    """Obtener estado de configuración de métodos de pago"""
    tenant_id_str = get_tenant_id()
    
    twilio_account = db.query(TwilioAccount).filter(TwilioAccount.tenant_id == tenant_id_str).one_or_none()
    flow_account = db.query(FlowAccount).filter(FlowAccount.tenant_id == tenant_id_str).one_or_none()
    
    return {
        "tenant_id": tenant_id_str,
        "integrations": {
            "twilio": {
                "configured": bool(twilio_account),
                "status": twilio_account.status if twilio_account else "not_configured"
            },
            "flow": {
                "configured": bool(flow_account),
                "status": flow_account.status if flow_account else "not_configured"
            }
        }
    }