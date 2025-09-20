#!/usr/bin/env python3
"""
Simulación de webhook para probar que el bot ahora funciona correctamente
"""
import requests
import json

def test_webhook_messages():
    print("🧪 SIMULANDO CONVERSACIÓN VÍA WEBHOOK")
    print("="*45)
    
    # URL del webhook (puerto 9001 donde corre el bot actualizado)
    webhook_url = "http://localhost:9001/webhook"
    
    # Número ACME Cannabis
    phone_number = "+56950915617"  # ACME client
    
    # Mensajes a probar
    test_messages = [
        "Hola",
        "Que productos tienes", 
        "Dame el catalogo",
        "Quiero Northern Lights"
    ]
    
    print(f"📱 Cliente: {phone_number} (ACME Cannabis)")
    print(f"🔗 Webhook: {webhook_url}")
    print(f"")
    
    for i, message in enumerate(test_messages, 1):
        print(f"{i}. 👤 Enviando: '{message}'")
        
        # Simular payload de webhook de WhatsApp
        payload = {
            "telefono": phone_number,
            "mensaje": message
        }
        
        try:
            response = requests.post(
                webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                response_data = response.json()
                bot_message = response_data.get("respuesta", "No respuesta returned")
                print(f"   🤖 Bot responde: {bot_message[:100]}...")
                
                # Verificar que no sea respuesta genérica
                if "Green House - Catálogo disponible" in bot_message:
                    print(f"   ✅ ÉXITO: Bot muestra catálogo real!")
                elif "Northern Lights" in bot_message and "$" in bot_message:
                    print(f"   ✅ ÉXITO: Bot muestra productos con precios!")
                elif "¡Hola! Bienvenido a Green House" in bot_message:
                    print(f"   ✅ ÉXITO: Bot saluda correctamente!")
                elif "¡Hola! Tenemos una variedad" in bot_message:
                    print(f"   ❌ PROBLEMA: Respuesta genérica de OpenAI")
                else:
                    print(f"   ⚠️ REVISAR: Respuesta no esperada")
            else:
                print(f"   ❌ Error HTTP {response.status_code}: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Error de conexión: {e}")
        
        print("")
    
    print(f"🎯 RESULTADO ESPERADO:")
    print(f"   ✅ 'Que productos tienes' → Catálogo con Northern Lights, OG Kush, etc.")
    print(f"   ✅ 'Dame el catalogo' → Mismo catálogo (keywords arregladas)")
    print(f"   ✅ Precios reales: $25,000, $28,000, $45,000")
    print(f"   ✅ Stock real: ✅ Disponible (15), ✅ Disponible (12)")

if __name__ == "__main__":
    test_webhook_messages()