#!/usr/bin/env python3
"""
Test context fix with fallback system
"""
import sys
import os

# Add the whatsapp-bot-fastapi directory to Python path
bot_path = os.path.join(os.path.dirname(__file__), 'whatsapp-bot-fastapi')
sys.path.insert(0, bot_path)

# Now import from services
from services.chat_service import procesar_mensaje, get_db_session, conversaciones_activas, openai_client

def test_context_fix():
    """Test context preservation in fallback system"""
    print("=== TESTING CONTEXT FIX ===\n")
    
    # Get database session
    try:
        db = get_db_session()
        print("[OK] Database connection successful")
        print(f"[INFO] OpenAI disponible: {openai_client is not None}")
    except Exception as e:
        print(f"[ERROR] Database connection failed: {e}")
        return
    
    telefono = "+9999999999"  # Fresh conversation
    
    print("** Test: Teléfono + Confirmación **\n")
    
    # Limpiar conversación previa
    if telefono in conversaciones_activas:
        del conversaciones_activas[telefono]
    
    # Mensaje 1: Usuario quiere teléfono
    mensaje1 = "quiero un telefono"
    print(f"Usuario: {mensaje1}")
    respuesta1 = procesar_mensaje(db, telefono, mensaje1)
    print(f"Bot: {respuesta1}")
    print(f"[DEBUG] Historial: {conversaciones_activas.get(telefono, [])}")
    print("-" * 60)
    
    # Mensaje 2: Usuario confirma con "si"
    mensaje2 = "si"
    print(f"Usuario: {mensaje2}")
    respuesta2 = procesar_mensaje(db, telefono, mensaje2)
    print(f"Bot: {respuesta2}")
    print(f"[DEBUG] Historial: {conversaciones_activas.get(telefono, [])}")
    
    # Verificar que no sea un saludo genérico
    if "¡Hola!" in respuesta2 and "En qué puedo ayudarte" in respuesta2:
        print("❌ ERROR: Se perdió el contexto - respuesta genérica")
    elif "Perfecto" in respuesta2 or "Cuántos" in respuesta2:
        print("✅ ÉXITO: Contexto mantenido correctamente")
    else:
        print("⚠️  REVISAR: Respuesta inesperada")
    
    print("-" * 60)
    
    # Close database
    if db:
        db.close()
    
    print("\n=== TEST COMPLETED ===")

if __name__ == "__main__":
    test_context_fix()