import os
import requests
import hashlib
import hmac
from dotenv import load_dotenv

# Cargar variables del .env
load_dotenv()

FLOW_API_KEY = os.getenv("FLOW_API_KEY")
FLOW_SECRET_KEY = os.getenv("FLOW_SECRET_KEY")

def _firmar(parametros: dict) -> str:
    """
    Genera la firma HMAC-SHA256 usando el FLOW_SECRET_KEY
    """
    keys = sorted(parametros.keys())
    cadena = "&".join([f"{k}={parametros[k]}" for k in keys])
    firma = hmac.new(FLOW_SECRET_KEY.encode(), cadena.encode(), hashlib.sha256).hexdigest()
    print(f"🖊️ Firma generada para cadena: {cadena}")
    print(f"➡️ Firma: {firma}")
    return firma


def enviar_callback(order_id: str, amount: str, status: str):
    """
    Envía el callback al endpoint del bot.
    status: "2" = pagado, cualquier otro = pendiente/fallido
    """
    data = {
        "apiKey": FLOW_API_KEY,
        "commerceOrder": order_id,
        "amount": amount,
        "status": status  # 2 = pagado
    }
    
    # Generar firma
    data["s"] = _firmar(data)

    print("\n📩 Payload a enviar al endpoint /flow/confirm:")
    for k, v in data.items():
        print(f"   - {k}: {v}")

    url = "http://127.0.0.1:8000/flow/confirm"
    print(f"\n🌐 Enviando POST a {url}...\n")

    r = requests.post(url, data=data)

    print("⬅️ Status HTTP:", r.status_code)
    print("⬅️ Respuesta del servidor:", r.text)


if __name__ == "__main__":
    print("=== TEST: PAGO CONFIRMADO (status=2) ===")
    enviar_callback(order_id="2", amount="3500", status="2")

    print("\n\n=== TEST: PAGO PENDIENTE/FALLIDO (status=1) ===")
    enviar_callback(order_id="2", amount="3500", status="1")
