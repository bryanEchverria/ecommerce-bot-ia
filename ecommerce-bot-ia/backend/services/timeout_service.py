"""
Servicio para manejar timeouts de conversación automáticamente
"""
import asyncio
import os
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database import SessionLocal
from models import FlowSesion
import httpx
import logging

logger = logging.getLogger(__name__)

# Configuración de timeout (PRUEBA RÁPIDA - CAMBIAR A MINUTOS EN PRODUCCIÓN)
TIMEOUT_CHECK_INTERVAL = 10   # Verificar cada 10 segundos (PRUEBA)
WARNING_TIMEOUT_MINUTES = 0.5  # Advertencia a los 30 segundos (PRUEBA)
FINAL_TIMEOUT_MINUTES = 1     # Finalizar a los 60 segundos (PRUEBA)

async def send_timeout_message(telefono: str, mensaje: str):
    """Envía mensaje de timeout usando Twilio directamente"""
    try:
        # Usar Twilio directamente para enviar mensajes de timeout
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        whatsapp_number = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")
        
        if not account_sid or not auth_token:
            logger.error("Twilio credentials not configured for timeout messages")
            return
        
        # Normalizar número de teléfono
        if not telefono.startswith('whatsapp:'):
            if not telefono.startswith('+'):
                telefono = '+' + telefono
            telefono = f'whatsapp:{telefono}'
        
        async with httpx.AsyncClient() as client:
            auth = (account_sid, auth_token)
            
            data = {
                'To': telefono,
                'From': whatsapp_number,
                'Body': mensaje
            }
            
            response = await client.post(
                f'https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json',
                auth=auth,
                data=data
            )
            
            if response.status_code == 201:
                logger.info(f"Timeout message sent successfully to {telefono}")
            else:
                logger.error(f"Failed to send timeout message: {response.status_code} - {response.text}")
            
    except Exception as e:
        logger.error(f"Error sending timeout message: {str(e)}")

async def check_and_handle_timeouts():
    """Verifica y maneja timeouts de todas las sesiones activas"""
    db = SessionLocal()
    try:
        now = datetime.utcnow()
        
        # Buscar sesiones activas que necesiten advertencia (30 min)
        warning_threshold = now - timedelta(minutes=WARNING_TIMEOUT_MINUTES)
        sesiones_warning = db.query(FlowSesion).filter(
            FlowSesion.conversation_active == True,
            FlowSesion.timeout_warning_sent == False,
            FlowSesion.last_message_at <= warning_threshold,
            FlowSesion.estado != "FINALIZADA"
        ).all()
        
        # Enviar advertencias
        for sesion in sesiones_warning:
            mensaje_warning = """⏰ *Seguimiento de Conversación*
            
¡Hola! Veo que ha pasado un tiempo desde tu último mensaje.

¿Sigues interesado en completar tu compra o necesitas más información?

👉 Escribe *continuar* para seguir, o *finalizar* para terminar la conversación.

⏳ Si no respondes en 30 minutos más, finalizaré automáticamente la sesión."""
            
            await send_timeout_message(sesion.telefono, mensaje_warning)
            sesion.timeout_warning_sent = True
            
        # Buscar sesiones para finalizar (60 min)
        final_threshold = now - timedelta(minutes=FINAL_TIMEOUT_MINUTES)
        sesiones_final = db.query(FlowSesion).filter(
            FlowSesion.conversation_active == True,
            FlowSesion.last_message_at <= final_threshold,
            FlowSesion.estado != "FINALIZADA"
        ).all()
        
        # Finalizar conversaciones
        for sesion in sesiones_final:
            mensaje_final = """🔚 *Conversación Finalizada*

Por tu seguridad y para optimizar nuestro servicio, he finalizado esta conversación por inactividad.

Si necesitas ayuda nuevamente, envía *hola* para iniciar una nueva sesión.

¡Gracias por contactar Sintestesia! 🙏"""
            
            await send_timeout_message(sesion.telefono, mensaje_final)
            sesion.conversation_active = False
            sesion.estado = "FINALIZADA"
            
        db.commit()
        logger.info(f"Processed {len(sesiones_warning)} warnings, {len(sesiones_final)} finalizations")
        
    except Exception as e:
        logger.error(f"Error in timeout check: {str(e)}")
        db.rollback()
    finally:
        db.close()

async def timeout_service_loop():
    """Loop principal del servicio de timeouts"""
    logger.info("Starting conversation timeout service...")
    
    while True:
        try:
            await check_and_handle_timeouts()
            await asyncio.sleep(TIMEOUT_CHECK_INTERVAL)
        except Exception as e:
            logger.error(f"Error in timeout service loop: {str(e)}")
            await asyncio.sleep(60)  # Esperar 1 minuto antes de reintentar

def start_timeout_service():
    """Inicia el servicio de timeouts en background"""
    if os.getenv("ENABLE_TIMEOUT_SERVICE", "true").lower() == "true":
        asyncio.create_task(timeout_service_loop())
        logger.info("Conversation timeout service started")
    else:
        logger.info("Timeout service disabled by configuration")