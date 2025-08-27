import os
import requests
from dotenv import load_dotenv
import hashlib
import hmac
from sqlalchemy.orm import Session
from models.pedido import Pedido
from core.config import settings

load_dotenv()

# Credenciales de Flow
FLOW_API_KEY = settings.FLOW_API_KEY
FLOW_SECRET_KEY = settings.FLOW_SECRET_KEY
FLOW_BASE_URL = settings.FLOW_BASE_URL
BASE_URL = settings.BASE_URL


def _firmar(parametros: dict) -> str:
    """
    Genera firma HMAC-SHA256 para los parámetros en Flow
    """
    keys = sorted(parametros.keys())
    cadena = "&".join([f"{k}={parametros[k]}" for k in keys])
    firma = hmac.new(FLOW_SECRET_KEY.encode(), cadena.encode(), hashlib.sha256).hexdigest()
    print(f"\n🖊️ Firma generada para cadena:\n   {cadena}\n➡️ Firma: {firma}\n")
    return firma


def validar_firma(params: dict) -> bool:
    """
    Valida la firma enviada por Flow en callbacks (Flow/confirm).
    """
    firma_recibida = params.pop("s", None)
    if not firma_recibida:
        print("⚠️ [Flow/confirm] No se recibió firma en el callback")
        return False

    firma_calculada = _firmar(params)
    valido = firma_recibida == firma_calculada
    print(f"🔎 [Flow/confirm] Firma recibida:   {firma_recibida}")
    print(f"🔎 [Flow/confirm] Firma calculada: {firma_calculada}")
    print(f"➡️ [Flow/confirm] ¿Firma válida? {valido}\n")
    return valido


def crear_orden_flow(order_id: str, monto: int, descripcion: str, db: Session) -> str:
    """
    Crea una orden de pago en Flow y devuelve el link de pago completo con el token.
    """
    url = f"{FLOW_BASE_URL}/payment/create"
    params = {
        "apiKey": FLOW_API_KEY,
        "commerceOrder": order_id,
        "subject": descripcion.replace("#", "").replace(" ", "_"),
        "amount": int(monto),
        "email": "cliente@correo.com",
        "urlConfirmation": f"{BASE_URL}/flow/confirm",
        "urlReturn": f"{BASE_URL}/flow/return"
    }

    params["s"] = _firmar(params)
    print(f"➡️ [Flow/create] Payload enviado a Flow:\n{params}")

    response = requests.post(url, data=params)
    print(f"➡️ [Flow/create] Respuesta Flow: {response.status_code} - {response.text}")

    if response.status_code == 200:
        data = response.json()
        token = data.get("token")
        if not token:
            print("⚠️ [Flow/create] No se recibió token en la respuesta\n")
            return "Error al generar link de pago"

        # Guardar token en la BD
        pedido = db.query(Pedido).filter_by(id=order_id).first()
        if pedido:
            pedido.token = token
            db.commit()

        # URL de pago - cambiar según ambiente
        if "sandbox" in FLOW_BASE_URL:
            url_pago = f"https://sandbox.flow.cl/app/web/pay.php?token={token}"
        else:
            url_pago = f"https://www.flow.cl/app/web/pay.php?token={token}"
        print(f"💰 Pedido #{order_id} creado (total ${monto}). URL de pago: {url_pago}\n")
        return url_pago
    else:
        print("❌ [Flow/create] Error al generar link de pago\n")
        return "Error al generar link de pago"


def verificar_pago_flow(order_id: str, db: Session) -> bool:
    """
    Verifica en Flow si un pago fue realizado exitosamente usando el token.
    """
    pedido = db.query(Pedido).filter_by(id=order_id).first()
    if not pedido or not pedido.token:
        print(f"⚠️ [Flow/getStatus] No se encontró token para el pedido {order_id}")
        return False

    url = f"{FLOW_BASE_URL}/payment/getStatus"
    params = {
        "apiKey": FLOW_API_KEY,
        "token": pedido.token  # Usamos el token, no commerceOrder
    }
    params["s"] = _firmar(params)

    print(f"➡️ [Flow/getStatus] Verificando pago con params:\n{params}")
    response = requests.get(url, params=params)
    print(f"➡️ [Flow/getStatus] Respuesta Flow: {response.status_code} - {response.text}")

    if response.status_code == 200:
        data = response.json()
        estado = data.get("status")
        print(f"🔎 [Flow/getStatus] Estado recibido: {estado}\n")
        return estado == 2
    else:
        print("❌ [Flow/getStatus] Error al consultar estado de pago\n")
        return False
