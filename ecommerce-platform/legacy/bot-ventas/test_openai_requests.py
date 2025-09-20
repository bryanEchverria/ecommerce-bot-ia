import requests

import os
from dotenv import load_dotenv

# 🔑 Cargar API Key desde variables de entorno
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

print(f"🔑 Probando con API Key directa: {api_key[:12]}...")

url = "https://api.openai.com/v1/models"
headers = {
    "Authorization": f"Bearer {api_key}"
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    print("✅ Conexión exitosa, modelos disponibles:")
    print(response.json())
else:
    print(f"⚠️ Error ({response.status_code}): {response.json()}")
