"""
Twilio WhatsApp webhook router for multi-tenant support
"""
from fastapi import APIRouter, Request, Response, HTTPException, Depends
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session
import json
import logging
from typing import Dict, Any, Optional
import hashlib
import hmac
import base64
import os
import uuid
from urllib.parse import urlencode
import httpx
import asyncio

from database import get_db, SessionLocal
from models import TwilioAccount
from auth_models import TenantClient

router = APIRouter()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_tenant_twilio_config(db: Session, host: str) -> Optional[TwilioAccount]:
    """
    Obtiene la configuración Twilio del tenant basado en el host
    """
    try:
        # Extract subdomain from host (e.g., "acme.sintestesia.cl" -> "acme")
        if not host or '.' not in host:
            logger.warning(f"Invalid host format: {host}")
            return None
            
        subdomain = host.split('.')[0]
        
        # Find tenant by slug (subdomain)
        tenant = db.query(TenantClient).filter(TenantClient.slug == subdomain).first()
        if not tenant:
            logger.warning(f"Tenant not found for subdomain: {subdomain}")
            return None
        
        # Get Twilio configuration for this tenant
        twilio_config = db.query(TwilioAccount).filter(
            TwilioAccount.tenant_id == tenant.id
        ).first()
        
        if not twilio_config:
            logger.warning(f"Twilio config not found for tenant: {tenant.id}")
            return None
            
        return twilio_config
        
    except Exception as e:
        logger.error(f"Error getting tenant Twilio config: {e}")
        return None

def validate_twilio_request(request_url: str, post_params: Dict[str, Any], auth_token: str, signature: str) -> bool:
    """Validate that the request came from Twilio"""
    if not auth_token:
        logger.warning("Twilio Auth Token not configured, skipping validation")
        return True
    
    # Create the string to sign
    data = urlencode(sorted(post_params.items()))
    string_to_sign = request_url + data
    
    # Create the expected signature
    expected_signature = base64.b64encode(
        hmac.new(
            auth_token.encode('utf-8'),
            string_to_sign.encode('utf-8'),
            hashlib.sha1
        ).digest()
    ).decode('utf-8')
    
    return hmac.compare_digest(signature, expected_signature)

@router.post("/bot/twilio/webhook")
async def twilio_webhook_multi_tenant(request: Request, db: Session = Depends(get_db)):
    """
    Endpoint multi-tenant para recibir mensajes de WhatsApp desde Twilio
    URL para configurar en Twilio: https://<slug>.sintestesia.cl/bot/twilio/webhook
    """
    try:
        # Get the raw body and form data
        body = await request.body()
        form_data = await request.form()
        
        # Convert form data to dict
        message_data = dict(form_data)
        
        # Get host from request
        host = request.headers.get('host', '')
        logger.info(f"Received Twilio webhook for host: {host}")
        
        # Get tenant's Twilio configuration
        twilio_config = get_tenant_twilio_config(db, host)
        if not twilio_config:
            logger.error(f"Twilio configuration not found for host: {host}")
            return PlainTextResponse(content="", status_code=404)
        
        # For simplicity, skip signature validation in the bot (can be added later)
        logger.info(f"Processing message for tenant: {twilio_config.tenant_id}")
        
        # Log the incoming message (without sensitive data)
        logger.info(f"Twilio webhook - Host: {host}, From: {message_data.get('From', '')}, Body: {message_data.get('Body', '')[:50]}...")
        
        # Extract message information
        from_number = message_data.get('From', '')
        to_number = message_data.get('To', '')
        message_body = message_data.get('Body', '')
        message_sid = message_data.get('MessageSid', '')
        
        # Process WhatsApp message
        if from_number.startswith('whatsapp:'):
            # Clean and normalize phone number
            phone_number = from_number.replace('whatsapp:', '').strip()
            if not phone_number.startswith('+'):
                phone_number = '+' + phone_number
                
            # Get tenant ID from the Twilio config
            tenant_id = str(twilio_config.tenant_id)
            
            # Process message with the tenant's context
            response_message = await process_whatsapp_message(phone_number, message_body, message_sid, tenant_id)
            
            return PlainTextResponse(
                content=response_message,
                status_code=200,
                media_type="text/xml",
                headers={"Content-Type": "text/xml; charset=utf-8"}
            )
        
        return PlainTextResponse(content="", status_code=200)
        
    except Exception as e:
        logger.error(f"Error processing Twilio webhook: {str(e)}")
        return PlainTextResponse(content="", status_code=200)

async def process_whatsapp_message(phone_number: str, message: str, message_sid: str, tenant_id: str = None) -> str:
    """
    Procesa un mensaje de WhatsApp usando el servicio de chat y devuelve una respuesta en formato TwiML
    """
    try:
        # Import chat service
        try:
            from services.chat_service import procesar_mensaje
            # Process message with chat service
            response_text = await procesar_mensaje(phone_number, message, tenant_id)
        except ImportError:
            logger.error("Chat service not available")
            response_text = "⚠️ Sistema de chat inteligente no disponible. Intenta más tarde."
        except Exception as e:
            logger.error(f"Error in chat service: {str(e)}")
            response_text = f"❌ Error procesando mensaje: {str(e)}"
        
        # Return TwiML response
        twiml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{response_text}</Message>
</Response>"""
        
        logger.info(f"Sending response to {phone_number}: {response_text[:100]}...")
        return twiml_response
        
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        return """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>Lo siento, ocurrió un error procesando tu mensaje. Intenta de nuevo.</Message>
</Response>"""

@router.get("/twilio/test")
async def test_twilio_integration(request: Request, db: Session = Depends(get_db)):
    """
    Endpoint de prueba para verificar que la integración multi-tenant está funcionando
    """
    try:
        host = request.headers.get('host', '')
        twilio_config = get_tenant_twilio_config(db, host)
        
        if not twilio_config:
            return {
                "status": "error",
                "message": f"No Twilio configuration found for host: {host}",
                "host": host
            }
        
        return {
            "status": "active",
            "message": "Twilio multi-tenant integration is working",
            "host": host,
            "webhook_url": f"https://{host}/bot/twilio/webhook",
            "tenant_id": str(twilio_config.tenant_id),
            "account_sid": twilio_config.account_sid[:8] + "..." if twilio_config.account_sid else None,
            "from_number": twilio_config.from_number,
            "status": twilio_config.status
        }
    except Exception as e:
        logger.error(f"Error in Twilio test endpoint: {str(e)}")
        return {
            "status": "error",
            "message": f"Error: {str(e)}",
            "error_type": type(e).__name__
        }