#!/usr/bin/env python3
"""
Debug the specific failing flow
"""
import sys
import os

# Add the whatsapp-bot-fastapi directory to Python path
bot_path = os.path.join(os.path.dirname(__file__), 'whatsapp-bot-fastapi')
sys.path.insert(0, bot_path)

# Now import from services
from services.chat_service import procesar_mensaje, get_db_session, conversaciones_activas

def test_debug_flow():
    """Debug the specific failing flow"""
    print("=== DEBUG FAILING FLOW ===\n")
    
    # Get database session
    try:
        db = get_db_session()
        print("[OK] Database connection successful")
    except Exception as e:
        print(f"[ERROR] Database connection failed: {e}")
        return
    
    telefono = "+1111222333"  # Fresh number
    
    # Clear any previous conversation
    if telefono in conversaciones_activas:
        del conversaciones_activas[telefono]
    
    print("** REPRODUCIR PROBLEMA ESPECIFICO **\n")
    
    # Mensaje 1: "un iphone"
    mensaje1 = "un iphone"
    print(f"1. Usuario: {mensaje1}")
    respuesta1 = procesar_mensaje(db, telefono, mensaje1)
    print(f"   Bot: {respuesta1}")
    print(f"   Historial: {conversaciones_activas.get(telefono, [])}")
    print("-" * 60)
    
    # Mensaje 2: "si" (aquí está el problema)
    mensaje2 = "si"
    print(f"2. Usuario: {mensaje2}")
    respuesta2 = procesar_mensaje(db, telefono, mensaje2)
    print(f"   Bot: {respuesta2}")
    print(f"   Historial: {conversaciones_activas.get(telefono, [])}")
    
    # Analysis
    if "Hola!" in respuesta2:
        print("\n[PROBLEMA CONFIRMADO] El bot perdió contexto y respondió con saludo")
    elif "Cuántos" in respuesta2 or "cantidad" in respuesta2:
        print("\n[ÉXITO] El contexto se mantuvo correctamente")
    else:
        print(f"\n[REVISAR] Respuesta inesperada: {respuesta2[:50]}...")
    
    print("-" * 60)
    
    # Close database
    if db:
        db.close()
    
    print("\n=== DEBUG COMPLETED ===")

if __name__ == "__main__":
    test_debug_flow()