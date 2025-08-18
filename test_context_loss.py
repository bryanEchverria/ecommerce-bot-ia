#!/usr/bin/env python3
"""
Test context loss issue when user responds with "si"
"""
import sys
import os

# Add the whatsapp-bot-fastapi directory to Python path
bot_path = os.path.join(os.path.dirname(__file__), 'whatsapp-bot-fastapi')
sys.path.insert(0, bot_path)

# Now import from services
from services.chat_service import procesar_mensaje, get_db_session, conversaciones_activas

def test_context_loss():
    """Test context loss when user responds with simple 'si'"""
    print("=== TESTING CONTEXT LOSS ISSUE ===\n")
    
    # Get database session
    try:
        db = get_db_session()
        print("[OK] Database connection successful")
    except Exception as e:
        print(f"[ERROR] Database connection failed: {e}")
        return
    
    telefono = "+1234567890"
    
    print("** Conversación problemática **\n")
    
    # Mensaje 1: Usuario quiere teléfono
    mensaje1 = "quiero un telefono"
    print(f"Usuario: {mensaje1}")
    respuesta1 = procesar_mensaje(db, telefono, mensaje1)
    print(f"Bot: {respuesta1}")
    print(f"[DEBUG] Historial después msg1: {conversaciones_activas.get(telefono, [])}")
    print("-" * 60)
    
    # Mensaje 2: Usuario confirma con "si" (aquí está el problema)
    mensaje2 = "si"
    print(f"Usuario: {mensaje2}")
    respuesta2 = procesar_mensaje(db, telefono, mensaje2)
    print(f"Bot: {respuesta2}")
    print(f"[DEBUG] Historial después msg2: {conversaciones_activas.get(telefono, [])}")
    print("-" * 60)
    
    # Close database
    if db:
        db.close()
    
    print("\n=== TEST COMPLETED ===")

if __name__ == "__main__":
    test_context_loss()