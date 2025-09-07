"""
Router para configuración Twilio multi-tenant
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
import logging
import uuid

from database import get_db
from models import TwilioAccount
from auth_models import TenantClient
from twilio_schemas import TwilioConfigIn, TwilioConfigOut, TwilioWebhookUrl
from crypto_utils import encrypt_token, decrypt_token
from tenant_middleware import get_tenant_id

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/integrations/twilio", tags=["twilio-integration"])

def _get_tenant_slug(db: Session, tenant_id_str: str) -> Optional[str]:
    """Get tenant slug from tenant_id string"""
    # tenant_clients.id is VARCHAR, not UUID, so use the string directly
    row = db.query(TenantClient).filter(TenantClient.id == tenant_id_str).one_or_none()
    return row.slug if row else None

@router.get("/config", response_model=TwilioConfigOut)
async def get_twilio_config(db: Session = Depends(get_db)):
    """Obtener configuración Twilio del tenant actual"""
    tenant_id_str = get_tenant_id()
    tenant_id = uuid.UUID(tenant_id_str)
    
    tw = db.query(TwilioAccount).filter(TwilioAccount.tenant_id == tenant_id).one_or_none()
    
    tenant_slug = _get_tenant_slug(db, tenant_id_str)
    if not tenant_slug:
        raise HTTPException(status_code=404, detail="Tenant slug not found")
    
    webhook_url = f"https://{tenant_slug}.sintestesia.cl/bot/twilio/webhook"
    
    if not tw:
        raise HTTPException(status_code=404, detail="Twilio configuration not found")
    
    return TwilioConfigOut(
        tenant_id=tenant_id_str,
        account_sid=tw.account_sid,
        from_number=tw.from_number,
        webhook_url=webhook_url,
        status=tw.status
    )

@router.post("/config", response_model=TwilioConfigOut)
async def upsert_twilio_config(
    payload: TwilioConfigIn,
    db: Session = Depends(get_db)
):
    """Crear/actualizar configuración Twilio del tenant actual"""
    tenant_id_str = get_tenant_id()
    tenant_id = uuid.UUID(tenant_id_str)
    
    tenant_slug = _get_tenant_slug(db, tenant_id_str)
    if not tenant_slug:
        raise HTTPException(status_code=404, detail="Tenant slug not found")
    
    tw = db.query(TwilioAccount).filter(TwilioAccount.tenant_id == tenant_id).one_or_none()
    
    # Encrypt auth token
    encrypted_token = encrypt_token(payload.auth_token.get_secret_value())
    
    if not tw:
        # Create new
        tw = TwilioAccount(
            tenant_id=tenant_id,
            account_sid=payload.account_sid,
            auth_token_enc=encrypted_token,
            from_number=payload.from_number,
            status="active"
        )
        db.add(tw)
        logger.info(f"Created Twilio config for tenant {tenant_id_str}")
    else:
        # Update existing
        tw.account_sid = payload.account_sid
        tw.auth_token_enc = encrypted_token
        tw.from_number = payload.from_number
        tw.status = "active"
        logger.info(f"Updated Twilio config for tenant {tenant_id_str}")
    
    db.commit()
    db.refresh(tw)
    
    webhook_url = f"https://{tenant_slug}.sintestesia.cl/bot/twilio/webhook"
    
    return TwilioConfigOut(
        tenant_id=tenant_id_str,
        account_sid=tw.account_sid,
        from_number=tw.from_number,
        webhook_url=webhook_url,
        status=tw.status
    )

@router.get("/webhook-url", response_model=TwilioWebhookUrl)
async def get_webhook_url(db: Session = Depends(get_db)):
    """Obtener URL de webhook para el tenant actual"""
    tenant_id_str = get_tenant_id()
    tenant_slug = _get_tenant_slug(db, tenant_id_str)
    
    if not tenant_slug:
        raise HTTPException(status_code=404, detail="Tenant slug not found")
    
    webhook_url = f"https://{tenant_slug}.sintestesia.cl/bot/twilio/webhook"
    
    return TwilioWebhookUrl(
        webhook_url=webhook_url,
        tenant_slug=tenant_slug
    )

@router.delete("/config")
async def delete_twilio_config(db: Session = Depends(get_db)):
    """Eliminar configuración Twilio del tenant actual"""
    tenant_id_str = get_tenant_id()
    tenant_id = uuid.UUID(tenant_id_str)
    
    twilio_account = db.query(TwilioAccount).filter(
        TwilioAccount.tenant_id == tenant_id
    ).first()
    
    if not twilio_account:
        raise HTTPException(status_code=404, detail="Twilio configuration not found")
    
    db.delete(twilio_account)
    db.commit()
    
    logger.info(f"Deleted Twilio config for tenant {tenant_id_str}")
    
    return {"message": "Twilio configuration deleted successfully"}