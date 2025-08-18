#!/usr/bin/env python3
"""
Test conversational flow with memory to fix the quantity confirmation issue
"""
import sys
import os

# Add the whatsapp-bot-fastapi directory to Python path
bot_path = os.path.join(os.path.dirname(__file__), 'whatsapp-bot-fastapi')
sys.path.insert(0, bot_path)

# Now import from services
from services.chat_service import procesar_mensaje, get_db_session

def test_conversational_memory():
    """Test conversational memory with product purchase flow"""
    print("=== TESTING CONVERSATIONAL MEMORY ===\n")
    
    # Get database session
    try:
        db = get_db_session()
        print("[OK] Database connection successful")
    except Exception as e:
        print(f"[ERROR] Database connection failed: {e}")
        return
    
    # Simulate the problematic conversation flow
    telefono = "+1234567890"
    
    print("** Conversación de prueba: producto + cantidad **\n")
    
    # Mensaje 1: Usuario quiere comprar un producto específico
    mensaje1 = "quiero comprar anal y vaginal"
    print(f"Usuario: {mensaje1}")
    respuesta1 = procesar_mensaje(db, telefono, mensaje1)
    print(f"Bot: {respuesta1}")
    print("-" * 60)
    
    # Mensaje 2: Usuario especifica cantidad (aquí estaba el problema)
    mensaje2 = "quiero comprar 4"
    print(f"Usuario: {mensaje2}")
    respuesta2 = procesar_mensaje(db, telefono, mensaje2)
    print(f"Bot: {respuesta2}")
    print("-" * 60)
    
    # Mensaje 3: Usuario confirma compra
    mensaje3 = "sí, confirmo"
    print(f"Usuario: {mensaje3}")
    respuesta3 = procesar_mensaje(db, telefono, mensaje3)
    print(f"Bot: {respuesta3}")
    print("-" * 60)
    
    # Test adicional con otro teléfono (nueva conversación)
    telefono2 = "+9876543210"
    print("\n** Nueva conversación con otro usuario **\n")
    
    mensaje_nuevo = "quiero 3 unidades"
    print(f"Usuario nuevo: {mensaje_nuevo}")
    respuesta_nueva = procesar_mensaje(db, telefono2, mensaje_nuevo)
    print(f"Bot: {respuesta_nueva}")
    
    # Close database
    if db:
        db.close()
    
    print("\n=== TEST COMPLETED ===")

if __name__ == "__main__":
    test_conversational_memory()