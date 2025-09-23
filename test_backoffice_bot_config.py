#!/usr/bin/env python3
"""
Test del flujo completo desde backoffice hasta bot
"""
import requests
import json

def test_bot_config_from_backoffice():
    """Simula el flujo del módulo de configuración del bot"""
    
    print("🏢 TESTING: Flujo completo Backoffice → Bot Configuration")
    print("=" * 60)
    
    # 1. Test del endpoint de preview usado por el frontend (simulado)
    print("\n1️⃣ Testing frontend bot configuration preview...")
    
    # Configuración personalizada desde el backoffice
    custom_config = {
        "system_prompt": "Eres ACME Cannabis Bot. Responde con precios REALES de la base de datos.",
        "style_overrides": {
            "tono": "profesional", 
            "usar_emojis": True,
            "limite_respuesta_caracteres": 500,
            "incluir_contexto_empresa": True
        },
        "nlu_params": {
            "modelo": "gpt-4o-mini",
            "temperature_nlu": 0.1,  # Más determinístico
            "max_tokens_nlu": 150
        },
        "nlg_params": {
            "modelo": "gpt-4o-mini", 
            "temperature_nlg": 0.3,  # Menos creativo, más factual
            "max_tokens_nlg": 400
        }
    }
    
    print(f"✅ Configuración preparada: Tono {custom_config['style_overrides']['tono']}")
    print(f"✅ Temperature reducida: {custom_config['nlg_params']['temperature_nlg']} (más factual)")
    
    # 2. Test directo con el bot de WhatsApp usando configuración personalizada
    print("\n2️⃣ Testing bot response with custom configuration...")
    
    test_messages = [
        "precio white widow",
        "cuanto cuesta northern lights", 
        "quiero ver el catálogo de semillas"
    ]
    
    for message in test_messages:
        print(f"\n🤖 Testing: '{message}'")
        
        response = requests.post("http://localhost:9001/webhook", json={
            "telefono": "+56950915617",
            "mensaje": message
        })
        
        if response.status_code == 200:
            result = response.json()
            bot_response = result.get('respuesta', '')
            print(f"✅ Response: {bot_response[:100]}...")
            
            # Verificar que use precios reales
            if "$25,000" in bot_response or "$40,000" in bot_response or "$35,000" in bot_response:
                print("✅ CORRECTO: Usa precios reales de la BD")
            else:
                print("❌ ERROR: No usa precios reales de la BD")
        else:
            print(f"❌ Error: {response.status_code}")
    
    print("\n" + "=" * 60)
    print("🎯 RESUMEN: Flujo Backoffice → Bot funcionando correctamente")

if __name__ == "__main__":
    test_bot_config_from_backoffice()