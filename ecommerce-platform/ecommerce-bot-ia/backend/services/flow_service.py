"""
Servicio de integración con Flow para pagos
Multi-tenant compatible
"""
import os
import requests
import hashlib
import hmac
from sqlalchemy.orm import Session
from models import FlowPedido

# Configuración de Flow
FLOW_API_KEY = os.getenv("FLOW_API_KEY", "749C736F-E427-482B-8400-7630D11L7766")
FLOW_SECRET_KEY = os.getenv("FLOW_SECRET_KEY", "30f3d774a49a886cb28502ddf26864b69b4589be")
FLOW_BASE_URL = os.getenv("FLOW_BASE_URL", "https://sandbox.flow.cl/api")
BASE_URL = os.getenv("BASE_URL", "https://webhook.sintestesia.cl")

def _firmar(parametros: dict) -> str:
    """
    Genera firma HMAC-SHA256 para los parámetros en Flow
    """
    keys = sorted(parametros.keys())
    cadena = "&".join([f"{k}={parametros[k]}" for k in keys])
    firma = hmac.new(FLOW_SECRET_KEY.encode(), cadena.encode(), hashlib.sha256).hexdigest()
    print(f"🖊️ [Flow] Firma generada para: {cadena}")
    print(f"➡️ [Flow] Firma: {firma}")
    return firma

def validar_firma(params: dict) -> bool:
    """
    Valida la firma enviada por Flow en callbacks
    """
    firma_recibida = params.pop("s", None)
    if not firma_recibida:
        print("⚠️ [Flow] No se recibió firma en el callback")
        return False

    firma_calculada = _firmar(params)
    valido = firma_recibida == firma_calculada
    print(f"🔎 [Flow] Firma recibida: {firma_recibida}")
    print(f"🔎 [Flow] Firma calculada: {firma_calculada}")
    print(f"➡️ [Flow] ¿Firma válida? {valido}")
    return valido

def crear_orden_flow(order_id: str, monto: int, descripcion: str, db: Session, tenant_id: str = None) -> str:
    """
    Crea una orden de pago en Flow y devuelve el link de pago
    Sistema simplificado sin multi-tenant
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
    print(f"➡️ [Flow] Payload enviado a Flow: {params}")

    response = requests.post(url, data=params)
    print(f"➡️ [Flow] Respuesta Flow: {response.status_code} - {response.text}")

    if response.status_code == 200:
        data = response.json()
        token = data.get("token")
        if not token:
            print("⚠️ [Flow] No se recibió token en la respuesta")
            return "Error al generar link de pago"

        # Guardar token en la BD
        if tenant_id:
            pedido = db.query(FlowPedido).filter_by(id=order_id, tenant_id=tenant_id).first()
        else:
            pedido = db.query(FlowPedido).filter_by(id=order_id).first()
        if pedido:
            pedido.token = token
            db.commit()
            print(f"💾 [Flow] Token guardado para pedido {order_id}")

        # URL de pago según ambiente
        if "sandbox" in FLOW_BASE_URL:
            url_pago = f"https://sandbox.flow.cl/app/web/pay.php?token={token}"
        else:
            url_pago = f"https://www.flow.cl/app/web/pay.php?token={token}"
        
        print(f"💰 [Flow] Pedido #{order_id} creado (${monto}). URL: {url_pago}")
        return url_pago
    else:
        print("❌ [Flow] Error al generar link de pago")
        return "Error al generar link de pago"

def verificar_pago_flow(order_id: str, db: Session, tenant_id: str = None) -> bool:
    """
    Verifica en Flow si un pago fue realizado exitosamente usando el token
    """
    if tenant_id:
        pedido = db.query(FlowPedido).filter_by(id=order_id, tenant_id=tenant_id).first()
    else:
        pedido = db.query(FlowPedido).filter_by(id=order_id).first()
    if not pedido or not pedido.token:
        print(f"⚠️ [Flow] No se encontró token para el pedido {order_id}")
        return False

    url = f"{FLOW_BASE_URL}/payment/getStatus"
    params = {
        "apiKey": FLOW_API_KEY,
        "token": pedido.token
    }
    params["s"] = _firmar(params)

    print(f"➡️ [Flow] Verificando pago con params: {params}")
    response = requests.get(url, params=params)
    print(f"➡️ [Flow] Respuesta Flow: {response.status_code} - {response.text}")

    if response.status_code == 200:
        data = response.json()
        estado = data.get("status")
        print(f"🔎 [Flow] Estado recibido: {estado}")
        return estado == 2  # 2 = pagado exitoso
    else:
        print("❌ [Flow] Error al consultar estado de pago")
        return False

# Función get_client_id_for_phone removida - ya no se usa multi-tenant