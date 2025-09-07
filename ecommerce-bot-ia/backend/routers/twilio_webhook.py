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

from database import get_db
from models import TwilioAccount
from auth_models import TenantClient
from crypto_utils import decrypt_token

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
        # Convert tenant.id (string) to UUID for the TwilioAccount query
        tenant_uuid = uuid.UUID(tenant.id)
        twilio_config = db.query(TwilioAccount).filter(
            TwilioAccount.tenant_id == tenant_uuid
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

async def send_whatsapp_message_tenant(to_number: str, message_text: str, twilio_config: TwilioAccount) -> bool:
    """
    Send WhatsApp message using Twilio API actively for specific tenant
    """
    try:
        auth_token = decrypt_token(twilio_config.auth_token_enc)
    except Exception as e:
        logger.error(f"Error decrypting auth token: {e}")
        return False
    
    try:
        async with httpx.AsyncClient() as client:
            auth = (twilio_config.account_sid, auth_token)
            
            data = {
                'To': f'whatsapp:{to_number}',
                'From': twilio_config.from_number,
                'Body': message_text
            }
            
            response = await client.post(
                f'https://api.twilio.com/2010-04-01/Accounts/{twilio_config.account_sid}/Messages.json',
                auth=auth,
                data=data
            )
            
            if response.status_code == 201:
                logger.info(f"Message sent successfully to {to_number}")
                return True
            else:
                logger.error(f"Failed to send message: {response.status_code} - {response.text}")
                return False
                
    except Exception as e:
        logger.error(f"Error sending message: {str(e)}")
        return False

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
        
        # Decrypt auth token for signature validation
        try:
            auth_token = decrypt_token(twilio_config.auth_token_enc)
        except Exception as e:
            logger.error(f"Error decrypting auth token: {e}")
            return PlainTextResponse(content="", status_code=500)
        
        # Validate Twilio signature for security
        signature = request.headers.get('X-Twilio-Signature', '')
        if signature and auth_token:
            is_valid = validate_twilio_request(
                str(request.url),
                message_data,
                auth_token,
                signature
            )
            if not is_valid:
                logger.error("Invalid Twilio signature")
                return PlainTextResponse(content="", status_code=403)
        else:
            logger.warning("No signature validation performed (missing signature or auth token)")
        
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

async def process_whatsapp_message_text(phone_number: str, message: str, message_sid: str, tenant_id: str = None) -> str:
    """
    Procesa un mensaje de WhatsApp usando OpenAI y devuelve solo el texto de respuesta
    """
    try:
        # Import Flow chat service with proper order processing
        try:
            from services.flow_chat_service import procesar_mensaje_flow
            from database import SessionLocal
            # Use Flow service with real DB session (sync)
            sync_db = SessionLocal()
            try:
                response_text = procesar_mensaje_flow(sync_db, phone_number, message, tenant_id)
                return response_text
            finally:
                sync_db.close()
        except ImportError:
            logger.error("Chat service not available")
            return "⚠️ Sistema de chat inteligente no disponible. Intenta más tarde."
        except Exception as e:
            logger.error(f"Error in chat service: {str(e)}")
            return f"❌ Error procesando mensaje: {str(e)}"
        
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        return "Lo siento, ocurrió un error procesando tu mensaje. Intenta de nuevo."

async def process_whatsapp_message(phone_number: str, message: str, message_sid: str, tenant_id: str = None) -> str:
    """
    Procesa un mensaje de WhatsApp usando OpenAI y devuelve una respuesta en formato TwiML
    """
    try:
        # Import Flow chat service with proper order processing
        try:
            from services.flow_chat_service import procesar_mensaje_flow
            from database import SessionLocal
            # Use Flow service with real DB session (sync)
            sync_db = SessionLocal()
            try:
                response_text = procesar_mensaje_flow(sync_db, phone_number, message, tenant_id)
            finally:
                sync_db.close()
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

@router.get("/twilio/status")
async def twilio_status_callback(request: Request):
    """
    Endpoint GET para callback de estado de Twilio
    URL para configurar en Twilio: https://webhook.sintestesia.cl/twilio/status
    """
    try:
        # Get query parameters
        params = dict(request.query_params)
        
        # Log the status callback
        logger.info(f"Twilio status callback: {params}")
        
        # Extract status information
        message_sid = params.get('MessageSid', '')
        message_status = params.get('MessageStatus', '')
        error_code = params.get('ErrorCode', '')
        error_message = params.get('ErrorMessage', '')
        
        # Log message status
        if message_status:
            logger.info(f"Message {message_sid} status: {message_status}")
            
        if error_code:
            logger.error(f"Message {message_sid} error {error_code}: {error_message}")
        
        # You can store this information in your database if needed
        # For now, we'll just return a success response
        
        return {"status": "received", "message_sid": message_sid, "message_status": message_status}
        
    except Exception as e:
        logger.error(f"Error processing status callback: {str(e)}")
        return {"status": "error", "message": str(e)}

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
            "status_callback_url": f"https://{host}/twilio/status",
            "tenant_id": str(twilio_config.tenant_id),
            "account_sid": twilio_config.account_sid[:8] + "..." if twilio_config.account_sid else None,
            "from_number": twilio_config.from_number,
            "auth_token_configured": bool(twilio_config.auth_token_enc),
            "status": twilio_config.status
        }
    except Exception as e:
        logger.error(f"Error in Twilio test endpoint: {str(e)}")
        return {
            "status": "error",
            "message": f"Error: {str(e)}",
            "error_type": type(e).__name__
        }