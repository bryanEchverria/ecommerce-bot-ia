from fastapi import FastAPI, Depends, Request, Query
from fastapi.responses import HTMLResponse, PlainTextResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
import os
import requests
import logging

from core.db import get_db
from services.chat_service import procesar_mensaje
from services.pagos_service import verificar_pago_flow, validar_firma, _firmar
from models.pedido import Pedido  

# Configuración de logging
logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI()

# Variables de entorno
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "mi_token_seguro")
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")

# Modelo para el webhook de mensajes
class WebhookInput(BaseModel):
    telefono: str
    mensaje: str

@app.get("/")
def home():
    return {"status": "Bot corriendo correctamente"}

"""***********************Webhook para recibir mensajes******************************"""
@app.post("/webhook")
def webhook(data: WebhookInput, db: Session = Depends(get_db)):
    logger.info(f"📲 [Webhook] Mensaje recibido de {data.telefono}: {data.mensaje}")
    respuesta = procesar_mensaje(db, data.telefono, data.mensaje)
    logger.info(f"📤 [Webhook] Respuesta enviada a {data.telefono}: {respuesta}")
    return {"telefono": data.telefono, "respuesta": respuesta}


"""***********************Integración con Flow*************************************"""
@app.post("/flow/confirm")
async def confirmar_pago_flow(request: Request, db: Session = Depends(get_db)):
    data = dict(await request.form())
    logger.info(f"📩 [Flow Confirm] Datos recibidos: {data}")

    if not validar_firma(data.copy()):
        logger.warning("❌ [Flow Confirm] Firma inválida, callback rechazado.")
        return {"status": "error", "message": "Firma inválida"}

    order_id = data.get("commerceOrder")
    if not order_id:
        logger.warning("⚠️ [Flow Confirm] order_id faltante en el callback.")
        return {"status": "error", "message": "Falta order_id"}

    # Obtener el status directamente del callback (más confiable que consultar API)
    status_flow = data.get("status")
    logger.info(f"🆔 [Flow Confirm] Status recibido en callback: {status_flow} para orden #{order_id}")

    try:
        # Status "2" significa pago exitoso según documentación de Flow
        pagado = (status_flow == "2")
        logger.info(f"💰 [Flow Confirm] Interpretando pago como: {'EXITOSO' if pagado else 'PENDIENTE/FALLIDO'}")

        if pagado:
            pedido = db.query(Pedido).filter_by(id=order_id).first()
            if pedido:
                pedido.estado = "pagado"
                db.commit()
                logger.info(f"✅ [Flow Confirm] Pedido #{order_id} marcado como PAGADO en la BD.")
                return {"status": "ok", "message": f"Pedido {order_id} pagado"}
            else:
                logger.warning(f"⚠️ [Flow Confirm] Pedido #{order_id} no encontrado en la BD.")
                return {"status": "error", "message": "Pedido no encontrado"}
        
        logger.info(f"⏳ [Flow Confirm] Pedido #{order_id} aún PENDIENTE de pago (status: {status_flow}).")
        return {"status": "pending"}

    except Exception as e:
        logger.error(f"⚠️ [Flow Confirm] ERROR interno al verificar pedido #{order_id}: {e}")
        return {"status": "error", "message": str(e)}

@app.api_route("/flow/return", methods=["GET", "POST"], response_class=HTMLResponse)
async def flow_return(request: Request, db: Session = Depends(get_db)):
    data = dict(await request.form()) if request.method == "POST" else dict(request.query_params)
    logger.info(f"🔄 [Flow Return] Datos recibidos: {data}")

    status = data.get("status")
    commerceOrder = data.get("commerceOrder")
    token = data.get("token")

    if not commerceOrder and token:
        flow_base_url = "https://sandbox.flow.cl/api"
        api_key = os.getenv("FLOW_API_KEY")
        params = {"apiKey": api_key, "token": token}
        params["s"] = _firmar(params)

        response = requests.get(f"{flow_base_url}/payment/getStatus", params=params)
        if response.status_code == 200:
            datos = response.json()
            commerceOrder = datos.get("commerceOrder")
            status = "SUCCESS" if datos.get("status") == 2 else "FAILED"
        else:
            return f"<h1>⚠️ No se pudo obtener información del pago (token={token}).</h1>"

    if status == "SUCCESS" and commerceOrder:
        pedido = db.query(Pedido).filter_by(id=commerceOrder).first()
        if pedido:
            pedido.estado = "pagado"
            db.commit()
            logger.info(f"✅ [Flow Return] Pedido #{commerceOrder} marcado como PAGADO en la BD.")
        return f"<h1>✅ Gracias por tu compra. Pedido #{commerceOrder} pagado correctamente.</h1>"

    return f"<h1>⚠️ El pago del pedido #{commerceOrder} fue cancelado o falló.</h1>"


"""*********************Webhook de Facebook Messenger******************************"""

@app.get("/facebook-webhook", response_class=PlainTextResponse)
def verify_facebook_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
    hub_verify_token: str = Query(None, alias="hub.verify_token")
):
    logger.info("🔎 Facebook está intentando verificar el webhook...")
    logger.info(f"➡️ hub.mode={hub_mode}, hub.challenge={hub_challenge}, hub.verify_token={hub_verify_token}")
    logger.info(f"➡️ VERIFY_TOKEN esperado={VERIFY_TOKEN}")

    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        logger.info("✅ Token válido. Enviando challenge de Facebook...")
        return hub_challenge

    logger.warning("❌ Token inválido. No coincide con VERIFY_TOKEN.")
    return "Token de verificación inválido"


@app.post("/facebook-webhook")
async def receive_facebook_webhook(request: Request, db: Session = Depends(get_db)):
    logger.info("📥 Facebook intentó enviar un evento a /facebook-webhook")

    headers = dict(request.headers)
    logger.info(f"📋 Headers recibidos: {headers}")

    try:
        data = await request.json()
        logger.info(f"📩 [Facebook] Datos recibidos: {data}")
    except Exception as e:
        body = await request.body()
        logger.error(f"❌ Error leyendo el cuerpo de la petición: {e}")
        logger.error(f"🔎 Cuerpo sin procesar: {body}")
        return {"status": "error", "message": "No se pudo leer el JSON"}

    # 👇 Nueva validación para eventos de prueba
    if "field" in data and "value" in data:
        logger.info(f"🧪 Evento de PRUEBA recibido: {data}")
        return {"status": "test_event"}

    if "entry" not in data:
        logger.warning("⚠️ El JSON recibido no tiene 'entry'. Es posible que sea un test o petición inválida.")
        return {"status": "no_entry"}

    for entry in data.get("entry", []):
        for messaging_event in entry.get("messaging", []):
            sender_id = messaging_event.get("sender", {}).get("id")
            logger.info(f"🔹 Evento recibido: {messaging_event}")

            if not sender_id:
                logger.warning(f"⚠️ No se encontró sender_id en: {messaging_event}")
                continue

            if "message" in messaging_event:
                texto = messaging_event["message"].get("text", "")
                logger.info(f"🗨️ Mensaje recibido de {sender_id}: {texto}")

                respuesta = procesar_mensaje(db, sender_id, texto)
                enviar_mensaje_messenger(sender_id, respuesta)
                logger.info(f"📤 Respuesta enviada a {sender_id}: {respuesta}")
            else:
                logger.info(f"⚠️ Evento diferente a 'message': {messaging_event}")

    return {"status": "ok"}



def enviar_mensaje_messenger(user_id: str, texto: str):
    url = f"https://graph.facebook.com/v17.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {
        "recipient": {"id": user_id},
        "message": {"text": texto}
    }
    response = requests.post(url, json=payload)
    logger.info(f"➡️ [Facebook] Respuesta: {response.status_code} - {response.text}")
