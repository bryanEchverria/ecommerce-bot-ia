"""
Router para configuración Flow multi-tenant
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
import logging
import uuid

from database import get_db
from models import FlowAccount
from auth_models import TenantClient
from flow_schemas import FlowConfigIn, FlowConfigOut, FlowWebhookUrls
from crypto_utils import encrypt_token, decrypt_token
from tenant_middleware import get_tenant_id

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/integrations/flow", tags=["flow-integration"])

def _get_tenant_slug(db: Session, tenant_id_str: str) -> Optional[str]:
    """Get tenant slug from tenant_id string"""
    # tenant_clients.id is VARCHAR, not UUID, so use the string directly
    row = db.query(TenantClient).filter(TenantClient.id == tenant_id_str).one_or_none()
    return row.slug if row else None

@router.get("/config", response_model=FlowConfigOut)
async def get_flow_config(db: Session = Depends(get_db)):
    """Obtener configuración Flow del tenant actual"""
    tenant_id_str = get_tenant_id()
    
    flow_account = db.query(FlowAccount).filter(FlowAccount.tenant_id == tenant_id_str).one_or_none()
    
    tenant_slug = _get_tenant_slug(db, tenant_id_str)
    if not tenant_slug:
        raise HTTPException(status_code=404, detail="Tenant slug not found")
    
    webhook_base = flow_account.webhook_base_url if flow_account and flow_account.webhook_base_url else "https://webhook.sintestesia.cl"
    confirm_url = f"{webhook_base}/flow/confirm"
    return_url = f"{webhook_base}/flow/return"
    
    if not flow_account:
        raise HTTPException(status_code=404, detail="Flow configuration not found")
    
    environment = "production" if "flow.cl/api" in flow_account.base_url and "sandbox" not in flow_account.base_url else "sandbox"
    
    return FlowConfigOut(
        tenant_id=tenant_id_str,
        api_key=flow_account.api_key,
        base_url=flow_account.base_url,
        webhook_base_url=flow_account.webhook_base_url,
        confirm_url=confirm_url,
        return_url=return_url,
        environment=environment,
        status=flow_account.status
    )

@router.post("/config", response_model=FlowConfigOut)
async def upsert_flow_config(
    payload: FlowConfigIn,
    db: Session = Depends(get_db)
):
    """Crear/actualizar configuración Flow del tenant actual"""
    tenant_id_str = get_tenant_id()
    
    tenant_slug = _get_tenant_slug(db, tenant_id_str)
    if not tenant_slug:
        raise HTTPException(status_code=404, detail="Tenant slug not found")
    
    flow_account = db.query(FlowAccount).filter(FlowAccount.tenant_id == tenant_id_str).one_or_none()
    
    # Encrypt secret key
    encrypted_secret = encrypt_token(payload.secret_key.get_secret_value())
    
    webhook_base = payload.webhook_base_url if payload.webhook_base_url else "https://webhook.sintestesia.cl"
    confirm_url = f"{webhook_base}/flow/confirm"
    return_url = f"{webhook_base}/flow/return"
    
    if not flow_account:
        # Create new
        flow_account = FlowAccount(
            tenant_id=tenant_id_str,
            api_key=payload.api_key,
            secret_key_enc=encrypted_secret,
            base_url=payload.base_url,
            webhook_base_url=payload.webhook_base_url,
            status="active"
        )
        db.add(flow_account)
        logger.info(f"Created Flow config for tenant {tenant_id_str}")
    else:
        # Update existing
        flow_account.api_key = payload.api_key
        flow_account.secret_key_enc = encrypted_secret
        flow_account.base_url = payload.base_url
        flow_account.webhook_base_url = payload.webhook_base_url
        flow_account.status = "active"
        logger.info(f"Updated Flow config for tenant {tenant_id_str}")
    
    db.commit()
    db.refresh(flow_account)
    
    environment = "production" if "flow.cl/api" in flow_account.base_url and "sandbox" not in flow_account.base_url else "sandbox"
    
    return FlowConfigOut(
        tenant_id=tenant_id_str,
        api_key=flow_account.api_key,
        base_url=flow_account.base_url,
        webhook_base_url=flow_account.webhook_base_url,
        confirm_url=confirm_url,
        return_url=return_url,
        environment=environment,
        status=flow_account.status
    )

@router.get("/webhook-urls", response_model=FlowWebhookUrls)
async def get_flow_webhook_urls(db: Session = Depends(get_db)):
    """Obtener URLs de webhooks Flow para el tenant actual"""
    tenant_id_str = get_tenant_id()
    tenant_slug = _get_tenant_slug(db, tenant_id_str)
    
    if not tenant_slug:
        raise HTTPException(status_code=404, detail="Tenant slug not found")
    
    flow_account = db.query(FlowAccount).filter(FlowAccount.tenant_id == tenant_id_str).one_or_none()
    
    webhook_base = flow_account.webhook_base_url if flow_account and flow_account.webhook_base_url else "https://webhook.sintestesia.cl"
    confirm_url = f"{webhook_base}/flow/confirm"
    return_url = f"{webhook_base}/flow/return"
    
    environment = "sandbox"
    if flow_account and flow_account.base_url:
        environment = "production" if "flow.cl/api" in flow_account.base_url and "sandbox" not in flow_account.base_url else "sandbox"
    
    return FlowWebhookUrls(
        confirm_url=confirm_url,
        return_url=return_url,
        tenant_slug=tenant_slug,
        environment=environment
    )

@router.delete("/config")
async def delete_flow_config(db: Session = Depends(get_db)):
    """Eliminar configuración Flow del tenant actual"""
    tenant_id_str = get_tenant_id()
    
    flow_account = db.query(FlowAccount).filter(
        FlowAccount.tenant_id == tenant_id_str
    ).first()
    
    if not flow_account:
        raise HTTPException(status_code=404, detail="Flow configuration not found")
    
    db.delete(flow_account)
    db.commit()
    
    logger.info(f"Deleted Flow config for tenant {tenant_id_str}")
    
    return {"message": "Flow configuration deleted successfully"}