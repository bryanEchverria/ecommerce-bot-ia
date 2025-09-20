import requests
import os

PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")  # generado en Facebook

def enviar_mensaje_messenger(user_id: str, texto: str):
    url = f"https://graph.facebook.com/v17.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {
        "recipient": {"id": user_id},
        "message": {"text": texto}
    }
    response = requests.post(url, json=payload)
    print(f"➡️ [Facebook] Enviado a {user_id}: {response.status_code} - {response.text}")
