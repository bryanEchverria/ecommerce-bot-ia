from fastapi import APIRouter, Request, HTTPException, Query
from fastapi.responses import PlainTextResponse
import os
import logging
import json
from typing import Dict, Any
import sys
from pathlib import Path

# Add parent directory to path for imports
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
services_dir = parent_dir / "services"
sys.path.append(str(parent_dir))
sys.path.append(str(services_dir))

from services.messaging import send_text
from services.chat_service import procesar_mensaje

router = APIRouter()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Meta WhatsApp webhook configuration
WEBHOOK_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "tu_token_de_verificacion_secreto")

@router.get("/webhook/meta")
async def verify_webhook(
    hub_mode: str = Query(alias="hub.mode"),
    hub_verify_token: str = Query(alias="hub.verify_token"), 
    hub_challenge: str = Query(alias="hub.challenge")
):
    """
    Verificación del webhook de Meta WhatsApp Cloud API
    Facebook/Meta envía este request para verificar que el webhook es válido
    """
    try:
        logger.info(f"Webhook verification request: mode={hub_mode}, token={hub_verify_token}")
        
        # Verificar que el token coincida
        if hub_mode == "subscribe" and hub_verify_token == WEBHOOK_VERIFY_TOKEN:
            logger.info("Webhook verification successful")
            return PlainTextResponse(content=hub_challenge, status_code=200)
        else:
            logger.error(f"Webhook verification failed. Expected token: {WEBHOOK_VERIFY_TOKEN}")
            raise HTTPException(status_code=403, detail="Verification token mismatch")
            
    except Exception as e:
        logger.error(f"Error in webhook verification: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/webhook/meta")
async def webhook_meta(request: Request):
    """
    Webhook principal para recibir mensajes de Meta WhatsApp Cloud API
    Procesa eventos entrantes y responde con mensajes inteligentes
    """
    try:
        # Obtener el payload JSON
        body = await request.body()
        webhook_data = json.loads(body.decode('utf-8'))
        
        logger.info(f"Meta webhook received: {json.dumps(webhook_data, indent=2)}")
        
        # Verificar que es una notificación de WhatsApp Business
        if webhook_data.get("object") != "whatsapp_business_account":
            logger.warning("Received webhook for non-WhatsApp Business object")
            return {"status": "ignored"}
        
        # Procesar cada entrada
        entries = webhook_data.get("entry", [])
        for entry in entries:
            # Procesar cada cambio
            changes = entry.get("changes", [])
            for change in changes:
                # Verificar que es un mensaje
                if change.get("field") != "messages":
                    continue
                
                value = change.get("value", {})
                
                # Procesar mensajes entrantes
                messages = value.get("messages", [])
                for message in messages:
                    await process_incoming_message(message, value)
                
                # Procesar estados de mensajes (delivered, read, etc.)
                statuses = value.get("statuses", [])
                for status in statuses:
                    await process_message_status(status)
        
        return {"status": "success"}
        
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in webhook: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid JSON")
    except Exception as e:
        logger.error(f"Error processing Meta webhook: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def process_incoming_message(message: Dict[str, Any], value: Dict[str, Any]) -> None:
    """
    Procesa un mensaje entrante de WhatsApp
    
    Args:
        message: Datos del mensaje
        value: Contexto del webhook
    """
    try:
        message_type = message.get("type")
        from_number = message.get("from")
        message_id = message.get("id")
        timestamp = message.get("timestamp")
        
        logger.info(f"Processing message {message_id} from {from_number}, type: {message_type}")
        
        # Solo procesar mensajes de texto por ahora
        if message_type == "text":
            text_content = message.get("text", {}).get("body", "")
            
            if not text_content:
                logger.warning(f"Empty text message from {from_number}")
                return
            
            # Formatear número de teléfono
            phone_number = format_phone_number(from_number)
            
            logger.info(f"Text message from {phone_number}: {text_content}")
            
            # Procesar mensaje con IA y obtener respuesta
            try:
                response_text = await procesar_mensaje(phone_number, text_content)
                
                # Enviar respuesta usando el servicio de mensajería
                success = await send_text(phone_number, response_text)
                
                if success:
                    logger.info(f"Response sent successfully to {phone_number}")
                else:
                    logger.error(f"Failed to send response to {phone_number}")
                    
            except Exception as e:
                logger.error(f"Error processing message with AI: {str(e)}")
                # Enviar mensaje de error genérico
                error_message = "Lo siento, ocurrió un error procesando tu mensaje. Por favor intenta de nuevo."
                await send_text(phone_number, error_message)
        
        elif message_type in ["image", "document", "audio", "video"]:
            # Por ahora, responder que no soportamos estos tipos
            phone_number = format_phone_number(from_number)
            unsupported_message = "Por ahora solo puedo procesar mensajes de texto. Por favor envía tu consulta como texto."
            await send_text(phone_number, unsupported_message)
        
        else:
            logger.info(f"Unsupported message type: {message_type}")
            
    except Exception as e:
        logger.error(f"Error processing incoming message: {str(e)}")

async def process_message_status(status: Dict[str, Any]) -> None:
    """
    Procesa estados de mensajes (delivered, read, etc.)
    
    Args:
        status: Datos del estado del mensaje
    """
    try:
        message_id = status.get("id")
        recipient_id = status.get("recipient_id")
        status_type = status.get("status")
        timestamp = status.get("timestamp")
        
        logger.info(f"Message {message_id} to {recipient_id} status: {status_type}")
        
        # Aquí puedes agregar lógica para manejar diferentes estados
        # Por ejemplo, actualizar base de datos con estado del mensaje
        
    except Exception as e:
        logger.error(f"Error processing message status: {str(e)}")

def format_phone_number(phone_number: str) -> str:
    """
    Formatea número de teléfono al formato estándar E.164
    
    Args:
        phone_number: Número de teléfono original
        
    Returns:
        str: Número formateado con +
    """
    if not phone_number:
        return ""
    
    # Limpiar el número
    clean_number = phone_number.strip()
    
    # Si ya tiene +, devolverlo como está
    if clean_number.startswith('+'):
        return clean_number
    
    # Si no tiene +, agregarlo
    return '+' + clean_number

@router.get("/webhook/meta/test")
async def test_meta_webhook():
    """Endpoint de prueba para verificar configuración del webhook Meta"""
    from settings import get_available_providers
    
    providers_info = get_available_providers()
    
    return {
        "status": "Meta WhatsApp webhook active",
        "verify_token_configured": bool(WEBHOOK_VERIFY_TOKEN),
        "webhook_url": "/webhook/meta",
        "verification_url": "/webhook/meta?hub.mode=subscribe&hub.verify_token=YOUR_TOKEN&hub.challenge=CHALLENGE",
        "providers": providers_info
    }