#!/usr/bin/env python3
"""
Test final bot functionality with the fixes implemented
"""
import sys
import os

# Add the whatsapp-bot-fastapi directory to Python path
bot_path = os.path.join(os.path.dirname(__file__), 'whatsapp-bot-fastapi')
sys.path.insert(0, bot_path)

# Now import from services
from services.chat_service import procesar_mensaje, get_db_session

def test_bot_scenarios():
    """Test various bot scenarios"""
    print("=== TESTING BOT FINAL FUNCTIONALITY ===\n")
    
    # Get database session
    try:
        db = get_db_session()
        print("[OK] Database connection successful")
    except Exception as e:
        print(f"[ERROR] Database connection failed: {e}")
        return
    
    # Test scenarios
    scenarios = [
        ("Búsqueda de celular", "hola, busco un celular"),
        ("Búsqueda específica iPhone", "me interesa un iPhone"),
        ("Solicitud de compra", "quiero comprar el iPhone 15 Pro"),
        ("Confirmación cantidad", "quiero 2 unidades"),
        ("Consulta de precio", "cuánto cuesta el iPhone?"),
        ("Ver catálogo", "quiero ver el catálogo"),
    ]
    
    for titulo, mensaje in scenarios:
        print(f"** {titulo} **")
        print(f"Usuario: {mensaje}")
        
        try:
            respuesta = procesar_mensaje(db, "+1234567890", mensaje)
            print(f"Bot: {respuesta}")
        except Exception as e:
            print(f"[ERROR] {e}")
        
        print("-" * 60)
    
    # Close database
    if db:
        db.close()
    
    print("\n=== TEST COMPLETED ===")

if __name__ == "__main__":
    test_bot_scenarios()