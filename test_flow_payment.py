#!/usr/bin/env python3
"""
Test complete flow with payment integration
"""
import sys
import os

# Add the whatsapp-bot-fastapi directory to Python path
bot_path = os.path.join(os.path.dirname(__file__), 'whatsapp-bot-fastapi')
sys.path.insert(0, bot_path)

# Now import from services
from services.chat_service import procesar_mensaje, get_db_session, conversaciones_activas

def test_complete_flow_payment():
    """Test complete purchase flow with payment generation"""
    print("=== TESTING COMPLETE FLOW WITH PAYMENT ===\n")
    
    # Get database session
    try:
        db = get_db_session()
        print("[OK] Database connection successful")
    except Exception as e:
        print(f"[ERROR] Database connection failed: {e}")
        return
    
    telefono = "+5556667777"  # Fresh conversation
    
    # Limpiar conversación previa
    if telefono in conversaciones_activas:
        del conversaciones_activas[telefono]
    
    print("** FLUJO COMPLETO: Busqueda -> Cantidad -> Confirmacion -> Pago **\n")
    
    # Paso 1: Usuario busca teléfono
    mensaje1 = "quiero comprar un telefono"
    print(f"1. Usuario: {mensaje1}")
    respuesta1 = procesar_mensaje(db, telefono, mensaje1)
    print(f"   Bot: {respuesta1}")
    print("-" * 60)
    
    # Paso 2: Usuario confirma el producto
    mensaje2 = "si"
    print(f"2. Usuario: {mensaje2}")
    respuesta2 = procesar_mensaje(db, telefono, mensaje2)
    print(f"   Bot: {respuesta2}")
    print("-" * 60)
    
    # Paso 3: Usuario especifica cantidad
    mensaje3 = "quiero 2"
    print(f"3. Usuario: {mensaje3}")
    respuesta3 = procesar_mensaje(db, telefono, mensaje3)
    print(f"   Bot: {respuesta3}")
    print("-" * 60)
    
    # Paso 4: Usuario confirma la compra
    mensaje4 = "si, confirmo"
    print(f"4. Usuario: {mensaje4}")
    respuesta4 = procesar_mensaje(db, telefono, mensaje4)
    print(f"   Bot: {respuesta4}")
    
    # Verificar que se generó enlace de pago
    if "enlace de pago" in respuesta4.lower() or "flow" in respuesta4.lower():
        print("\n[EXITO] Flujo completo con enlace de pago generado")
    else:
        print("\n[ERROR] No se genero enlace de pago")
    
    print("-" * 60)
    
    # Close database
    if db:
        db.close()
    
    print("\n=== TEST COMPLETED ===")

if __name__ == "__main__":
    test_complete_flow_payment()