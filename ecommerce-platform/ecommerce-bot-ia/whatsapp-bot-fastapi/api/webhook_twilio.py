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
            await process_whatsapp_message(phone_number, message_body, message_sid, tenant_id, twilio_config)
            
            # Return empty response since message is sent via API
            return PlainTextResponse(content="", status_code=200)
        
        return PlainTextResponse(content="", status_code=200)
        
    except Exception as e:
        logger.error(f"Error processing Twilio webhook: {str(e)}")
        return PlainTextResponse(content="", status_code=200)

async def process_whatsapp_message(phone_number: str, message: str, message_sid: str, tenant_id: str = None, twilio_config = None) -> str:
    """
    Procesa un mensaje de WhatsApp usando el servicio Flow integrado y envía la respuesta usando Twilio API
    """
    try:
        # Import Flow chat service and Twilio adapter
        try:
            from services.flow_chat_service import procesar_mensaje_flow
            from adapters.twilio_adapter import TwilioAdapter
            
            # Create database session
            db = SessionLocal()
            try:
                # Use the Flow chat service with tenant context
                response_text = procesar_mensaje_flow(db, phone_number, message, tenant_id)
                
                # Limit response length for WhatsApp (Twilio limit is 1600 chars)
                if len(response_text) > 1500:
                    # Get tenant name dynamically
                    tenant_name = None
                    if twilio_config:
                        try:
                            from auth_models import TenantClient
                            tenant = db.query(TenantClient).filter(TenantClient.id == tenant_id).first()
                            if tenant:
                                tenant_name = tenant.name
                        except:
                            pass
                    response_text = truncate_response_for_whatsapp(response_text, message, tenant_name)
                
                logger.info(f"Flow service response: {response_text[:100]}...")
            finally:
                db.close()
                
            # Send response using Twilio API with tenant configuration
            if twilio_config:
                # Decrypt auth token using the proper crypto utilities
                try:
                    from crypto_utils import decrypt_token
                    # Convert from database bytes/memoryview to actual bytes if needed
                    encrypted_token = twilio_config.auth_token_enc
                    if isinstance(encrypted_token, memoryview):
                        encrypted_token = encrypted_token.tobytes()
                    # For bytea from PostgreSQL, encrypted_token should already be bytes
                    # No need to convert from hex if it's already bytes
                    auth_token = decrypt_token(encrypted_token)
                    
                    twilio_adapter = TwilioAdapter(
                        account_sid=twilio_config.account_sid,
                        auth_token=auth_token,
                        from_number=twilio_config.from_number
                    )
                    logger.info(f"Using tenant-specific Twilio config: {twilio_config.account_sid[:8]}...")
                except Exception as e:
                    logger.error(f"Error decrypting Twilio token: {e}")
                    # Fallback to environment variables
                    twilio_adapter = TwilioAdapter()
            else:
                twilio_adapter = TwilioAdapter()
            
            success = await twilio_adapter.send_text(phone_number, response_text)
            
            if success:
                logger.info(f"Message sent successfully to {phone_number}")
            else:
                logger.error(f"Failed to send message to {phone_number}")
                
        except ImportError as e:
            logger.error(f"Flow chat service not available: {str(e)}")
            response_text = "⚠️ Sistema de chat inteligente no disponible. Intenta más tarde."
            # Still try to send the error message
            try:
                from adapters.twilio_adapter import TwilioAdapter
                if twilio_config:
                    try:
                        from crypto_utils import decrypt_token
                        encrypted_token = twilio_config.auth_token_enc
                        if isinstance(encrypted_token, memoryview):
                            encrypted_token = encrypted_token.tobytes()
                        auth_token = decrypt_token(encrypted_token)
                        twilio_adapter = TwilioAdapter(
                            account_sid=twilio_config.account_sid,
                            auth_token=auth_token,
                            from_number=twilio_config.from_number
                        )
                    except:
                        twilio_adapter = TwilioAdapter()
                else:
                    twilio_adapter = TwilioAdapter()
                await twilio_adapter.send_text(phone_number, response_text)
            except:
                pass
        except Exception as e:
            logger.error(f"Error in Flow chat service: {str(e)}")
            # Fallback to simple response
            response_text = f"🌿 ¡Hola! Estamos experimentando problemas técnicos. Intenta de nuevo en unos momentos."
            try:
                from adapters.twilio_adapter import TwilioAdapter
                if twilio_config:
                    try:
                        from crypto_utils import decrypt_token
                        encrypted_token = twilio_config.auth_token_enc
                        if isinstance(encrypted_token, memoryview):
                            encrypted_token = encrypted_token.tobytes()
                        auth_token = decrypt_token(encrypted_token)
                        twilio_adapter = TwilioAdapter(
                            account_sid=twilio_config.account_sid,
                            auth_token=auth_token,
                            from_number=twilio_config.from_number
                        )
                    except:
                        twilio_adapter = TwilioAdapter()
                else:
                    twilio_adapter = TwilioAdapter()
                await twilio_adapter.send_text(phone_number, response_text)
            except:
                pass
        
        # Return empty response since we're sending via API
        return ""
        
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        # Try to send error message
        try:
            from adapters.twilio_adapter import TwilioAdapter
            if twilio_config:
                twilio_adapter = TwilioAdapter(
                    account_sid=twilio_config.account_sid,
                    auth_token=os.getenv("TWILIO_AUTH_TOKEN"),
                    from_number=twilio_config.from_number
                )
            else:
                twilio_adapter = TwilioAdapter()
            await twilio_adapter.send_text(phone_number, "Lo siento, ocurrió un error procesando tu mensaje. Intenta de nuevo.")
        except:
            pass
        return ""

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

def truncate_response_for_whatsapp(response_text: str, original_message: str, tenant_name: str = None) -> str:
    """
    Trunca respuestas largas para WhatsApp manteniendo la información más relevante
    Twilio WhatsApp tiene límite de 1600 caracteres
    """
    if len(response_text) <= 1500:
        return response_text
    
    # Detectar si es consulta de categoría específica
    message_lower = original_message.lower()
    
    # LÓGICA HARDCODEADA ELIMINADA - AHORA USA GPT INTELIGENTE
    # La clasificación por categorías se maneja en ai_improvements.py con GPT
    
    category_keyword = ""
    detected_category = ""
    
    # Esta lógica hardcodeada se reemplazó por clasificación GPT inteligente
    # TODO: Eliminar este bloque completo una vez confirmado que funciona
    if False:  # Deshabilitado
        
        # Extraer solo productos de la categoría solicitada
        lines = response_text.split('\n')
        filtered_lines = []
        current_product = []
        found_category_products = 0
        
        for line in lines:
            if line.strip().startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '10.')):
                # Es inicio de un producto
                if current_product and any(category_keyword.lower() in p.lower() for p in current_product):
                    filtered_lines.extend(current_product)
                    found_category_products += 1
                    if found_category_products >= 5:  # Limitar a 5 productos
                        break
                current_product = [line]
            elif current_product:
                current_product.append(line)
        
        # Agregar último producto si aplica
        if current_product and any(category_keyword.lower() in p.lower() for p in current_product) and found_category_products < 5:
            filtered_lines.extend(current_product)
        
        if filtered_lines:
            # Construir respuesta acortada para la categoría - COMPLETAMENTE DINÁMICO
            store_name = tenant_name or "nuestra tienda"
            category_display = detected_category.title() if detected_category else category_keyword.title()
            header = f"🌿 **{category_display} disponibles en {store_name}:**\n\n"
            footer = f"\n💬 *Para comprar:* Escribe 'Quiero [nombre del producto]'\n📱 *Ver más:* Escribe 'ver catálogo completo'"
            
            filtered_response = header + '\n'.join(filtered_lines) + footer
            
            if len(filtered_response) <= 1500:
                return filtered_response
    
    # Fallback: truncar respuesta manteniendo el formato
    lines = response_text.split('\n')
    truncated_lines = []
    char_count = 0
    
    for line in lines:
        if char_count + len(line) + 100 > 1400:  # Dejar espacio para el mensaje final
            break
        truncated_lines.append(line)
        char_count += len(line) + 1
    
    # Agregar mensaje de continuación
    truncated_response = '\n'.join(truncated_lines)
    truncated_response += f"\n\n📱 *Respuesta acortada por WhatsApp*\n💬 *Ver catálogo completo:* Escribe 'ver todo'"
    
    return truncated_response