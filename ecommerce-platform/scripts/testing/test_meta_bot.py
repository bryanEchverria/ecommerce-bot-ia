#!/usr/bin/env python3
"""
Script para probar la integración de Meta WhatsApp Cloud API
"""
import os
import asyncio
import requests
import json
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración
WHATSAPP_TOKEN = os.getenv('WHATSAPP_TOKEN')
WHATSAPP_PHONE_NUMBER_ID = os.getenv('WHATSAPP_PHONE_NUMBER_ID')
GRAPH_API_VERSION = os.getenv('GRAPH_API_VERSION', 'v21.0')
BASE_URL = os.getenv('BASE_URL', 'http://localhost:9001')

def test_webhook_verification():
    """Prueba la verificación del webhook"""
    print("🔍 Probando verificación del webhook...")
    
    try:
        url = f"{BASE_URL}/webhook/meta"
        params = {
            'hub.mode': 'subscribe',
            'hub.verify_token': os.getenv('WHATSAPP_VERIFY_TOKEN', 'test_token'),
            'hub.challenge': 'test_challenge_123'
        }
        
        response = requests.get(url, params=params)
        
        if response.status_code == 200 and response.text == 'test_challenge_123':
            print("✅ Verificación del webhook exitosa")
            return True
        else:
            print(f"❌ Error en verificación: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error probando webhook: {str(e)}")
        return False

def test_webhook_endpoint():
    """Prueba el endpoint de test del webhook"""
    print("🧪 Probando endpoint de test...")
    
    try:
        url = f"{BASE_URL}/webhook/meta/test"
        response = requests.get(url)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Endpoint de test exitoso")
            print(f"📋 Respuesta: {json.dumps(result, indent=2)}")
            return True
        else:
            print(f"❌ Error en endpoint de test: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error probando endpoint: {str(e)}")
        return False

def test_status_endpoint():
    """Prueba el endpoint de status"""
    print("📊 Probando endpoint de status...")
    
    try:
        url = f"{BASE_URL}/status"
        response = requests.get(url)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Status endpoint exitoso")
            print(f"📋 Providers: {json.dumps(result.get('providers', {}), indent=2)}")
            return True
        else:
            print(f"❌ Error en status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error probando status: {str(e)}")
        return False

def send_test_message():
    """Envía un mensaje de prueba usando Meta API directamente"""
    print("📱 Enviando mensaje de prueba...")
    
    if not WHATSAPP_TOKEN or not WHATSAPP_PHONE_NUMBER_ID:
        print("❌ Faltan WHATSAPP_TOKEN o WHATSAPP_PHONE_NUMBER_ID")
        return False
    
    # Número de prueba (reemplazar con un número real para pruebas)
    test_number = input("Ingresa el número de WhatsApp para la prueba (+56912345678): ").strip()
    if not test_number:
        print("❌ Número requerido para la prueba")
        return False
    
    try:
        url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{WHATSAPP_PHONE_NUMBER_ID}/messages"
        headers = {
            "Authorization": f"Bearer {WHATSAPP_TOKEN}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "to": test_number,
            "type": "text",
            "text": {
                "body": "🤖 ¡Hola! Este es un mensaje de prueba desde el bot de e-commerce Meta WhatsApp. ¿Cómo puedo ayudarte hoy?"
            }
        }
        
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            message_id = result.get('messages', [{}])[0].get('id')
            print(f"✅ Mensaje enviado exitosamente")
            print(f"📨 Message ID: {message_id}")
            return True
        else:
            print(f"❌ Error enviando mensaje: {response.status_code}")
            print(f"📋 Respuesta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error enviando mensaje: {str(e)}")
        return False

def send_test_template():
    """Envía un template de prueba"""
    print("📋 Enviando template de prueba...")
    
    if not WHATSAPP_TOKEN or not WHATSAPP_PHONE_NUMBER_ID:
        print("❌ Faltan credenciales de Meta")
        return False
    
    test_number = input("Ingresa el número para el template (+56912345678): ").strip()
    if not test_number:
        print("❌ Número requerido para la prueba")
        return False
    
    try:
        url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{WHATSAPP_PHONE_NUMBER_ID}/messages"
        headers = {
            "Authorization": f"Bearer {WHATSAPP_TOKEN}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "to": test_number,
            "type": "template",
            "template": {
                "name": "hello_world",
                "language": {
                    "code": "en_US"
                }
            }
        }
        
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Template enviado exitosamente")
            print(f"📋 Respuesta: {json.dumps(result, indent=2)}")
            return True
        else:
            print(f"❌ Error enviando template: {response.status_code}")
            print(f"📋 Respuesta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error enviando template: {str(e)}")
        return False

def test_interactive_buttons():
    """Envía botones interactivos de prueba"""
    print("🔘 Enviando botones interactivos de prueba...")
    
    if not WHATSAPP_TOKEN or not WHATSAPP_PHONE_NUMBER_ID:
        print("❌ Faltan credenciales de Meta")
        return False
    
    test_number = input("Ingresa el número para botones (+56912345678): ").strip()
    if not test_number:
        print("❌ Número requerido para la prueba")
        return False
    
    try:
        url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{WHATSAPP_PHONE_NUMBER_ID}/messages"
        headers = {
            "Authorization": f"Bearer {WHATSAPP_TOKEN}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "to": test_number,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "header": {
                    "type": "text",
                    "text": "🛍️ Bot de E-commerce"
                },
                "body": {
                    "text": "¡Hola! ¿En qué puedo ayudarte hoy?"
                },
                "footer": {
                    "text": "Selecciona una opción"
                },
                "action": {
                    "buttons": [
                        {
                            "type": "reply",
                            "reply": {
                                "id": "productos",
                                "title": "Ver Productos"
                            }
                        },
                        {
                            "type": "reply",
                            "reply": {
                                "id": "pedidos",
                                "title": "Mis Pedidos"
                            }
                        },
                        {
                            "type": "reply",
                            "reply": {
                                "id": "ayuda",
                                "title": "Ayuda"
                            }
                        }
                    ]
                }
            }
        }
        
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Botones interactivos enviados exitosamente")
            print(f"📋 Respuesta: {json.dumps(result, indent=2)}")
            return True
        else:
            print(f"❌ Error enviando botones: {response.status_code}")
            print(f"📋 Respuesta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error enviando botones: {str(e)}")
        return False

def main():
    """Función principal"""
    print("🧪 Probador Meta WhatsApp Cloud API")
    print("=" * 40)
    
    tests = [
        ("Webhook Verification", test_webhook_verification),
        ("Webhook Test Endpoint", test_webhook_endpoint),
        ("Status Endpoint", test_status_endpoint),
    ]
    
    # Ejecutar pruebas básicas
    passed = 0
    for name, test_func in tests:
        print(f"\n🔍 Ejecutando: {name}")
        if test_func():
            passed += 1
        print("-" * 40)
    
    print(f"\n📊 Pruebas básicas: {passed}/{len(tests)} exitosas")
    
    # Pruebas opcionales que requieren interacción
    print("\n🎯 Pruebas opcionales (requieren número de teléfono):")
    
    while True:
        print("\nOpciones:")
        print("1. Enviar mensaje de texto")
        print("2. Enviar template hello_world")
        print("3. Enviar botones interactivos")
        print("4. Salir")
        
        choice = input("\nSelecciona una opción (1-4): ").strip()
        
        if choice == "1":
            send_test_message()
        elif choice == "2":
            send_test_template()
        elif choice == "3":
            test_interactive_buttons()
        elif choice == "4":
            break
        else:
            print("❌ Opción inválida")

if __name__ == "__main__":
    main()