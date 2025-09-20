import os
from dotenv import load_dotenv
from openai import OpenAI

print("🔄 Cargando .env...")
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    print("❌ No se encontró la variable OPENAI_API_KEY en el .env")
    exit()

print(f"🔑 Key cargada: {api_key[:10]}...")

try:
    client = OpenAI(api_key=api_key)
    models = client.models.list()
    print("✅ Conexión exitosa. Modelos disponibles:")
    for m in models.data[:5]:
        print(" -", m.id)
except Exception as e:
    print(f"⚠️ Error: {e}")
