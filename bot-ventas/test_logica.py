import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base
from models.producto import Producto
from services.chat_service import procesar_mensaje

# --- Cargar el .env ---
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)

# Verificación de la API Key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError(f"❌ No se encontró OPENAI_API_KEY en {dotenv_path}")
print(f"🔑 OPENAI_API_KEY cargada: {api_key[:10]}...")

# --- Conexión a la BD local ---
engine = create_engine("sqlite:///./whatsapp_bot.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

db = SessionLocal()

telefono = "56912345678"

print("=== MENU INICIAL ===")
print(procesar_mensaje(db, telefono, "hola"))

print("\n=== PEDIDO DIRECTO ===")
print(procesar_mensaje(db, telefono, "quiero 2 panes y una bebida"))

print("\n=== CONFIRMACION ===")
print(procesar_mensaje(db, telefono, "si"))
