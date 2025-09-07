from fastapi import APIRouter, Request, Response, HTTPException
from fastapi.responses import PlainTextResponse
import json
import logging
from typing import Dict, Any
import hashlib
import hmac
import base64
import os
from urllib.parse import urlencode
import httpx
import asyncio

router = APIRouter()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Twilio configuration from environment variables
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")

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

async def send_whatsapp_message(to_number: str, message_text: str) -> bool:
    """
    Send WhatsApp message using Twilio API actively
    """
    if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
        logger.error("Twilio credentials not configured")
        return False
    
    try:
        async with httpx.AsyncClient() as client:
            auth = (TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
            
            data = {
                'To': f'whatsapp:{to_number}',
                'From': 'whatsapp:+14155238886',  # Tu número de Twilio
                'Body': message_text
            }
            
            response = await client.post(
                f'https://api.twilio.com/2010-04-01/Accounts/{TWILIO_ACCOUNT_SID}/Messages.json',
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

@router.post("/twilio/webhook")
async def twilio_webhook(request: Request):
    """
    Endpoint para recibir mensajes de WhatsApp desde Twilio
    URL para configurar en Twilio: https://webhook.sintestesia.cl/twilio/webhook
    """
    try:
        # Get the raw body and form data
        body = await request.body()
        form_data = await request.form()
        
        # Convert form data to dict
        message_data = dict(form_data)
        
        # Log the incoming message
        logger.info(f"Received Twilio webhook: {message_data}")
        
        # Temporarily disable signature validation for debugging
        # TODO: Fix signature validation logic
        signature = request.headers.get('X-Twilio-Signature', '')
        logger.info(f"Twilio signature received: {signature}")
        logger.info(f"Request URL: {str(request.url)}")
        
        # Skip validation for now
        # if TWILIO_AUTH_TOKEN and signature:
        #     is_valid = validate_twilio_request(
        #         str(request.url),
        #         message_data,
        #         TWILIO_AUTH_TOKEN,
        #         signature
        #     )
        #     if not is_valid:
        #         logger.error("Invalid Twilio signature")
        #         raise HTTPException(status_code=403, detail="Invalid signature")
        
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
            logger.info(f"WhatsApp message from {phone_number}: {message_body}")
            
            # Here you can integrate with your existing bot logic
            # For now, we'll just log and respond with a simple message
            
            # You can integrate this with your existing bot logic in routers/bot.py
            # by calling the appropriate functions based on the message content
            
            # Use TwiML response (doesn't consume daily limit in sandbox)
            # For Twilio, we'll use ACME Corporation as the default tenant
            tenant_id = "0c063a0b-a773-46d7-a8d3-8bec58aaa5ef"  # ACME Corporation
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
async def test_twilio_integration():
    """
    Endpoint de prueba para verificar que la integración está funcionando
    """
    try:
        return {
            "status": "active",
            "message": "Twilio integration is working",
            "webhook_url": "https://webhook.sintestesia.cl/twilio/webhook",
            "status_callback_url": "https://webhook.sintestesia.cl/twilio/status",
            "configured_number": TWILIO_WHATSAPP_NUMBER,
            "account_sid": TWILIO_ACCOUNT_SID[:8] + "..." if TWILIO_ACCOUNT_SID else None,
            "auth_token_configured": bool(TWILIO_AUTH_TOKEN),
            "environment_check": {
                "TWILIO_ACCOUNT_SID": TWILIO_ACCOUNT_SID is not None,
                "TWILIO_AUTH_TOKEN": TWILIO_AUTH_TOKEN is not None,
                "TWILIO_WHATSAPP_NUMBER": TWILIO_WHATSAPP_NUMBER is not None
            }
        }
    except Exception as e:
        logger.error(f"Error in Twilio test endpoint: {str(e)}")
        return {
            "status": "error",
            "message": f"Error: {str(e)}",
            "error_type": type(e).__name__
        }