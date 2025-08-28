#!/usr/bin/env python3
"""
Script para probar Meta WhatsApp con la configuración de Sintestesia
Usa los datos reales de tu configuración Meta Business
"""
import requests
import json

# Tu configuración Meta Business
META_CONFIG = {
    'token': 'EAAKlRZBfhpIIBPR9kSYQ7Jyk8ZBPZAkDyAYo4LCs5YxO9yUOYHLbveiUvnNF4hnpNvcldgTtMZAMGpoXuX1vkXZBGLDbZAZA32cZAt6rSwBvfD2O19fKuyvhltlME2MMKuYphJZAUHPXRjsrzpFGImVax4dEjcPj7INwGs2wX5jiSmqxslw7ZBDFYWHECW9SxOA92r1basoqOE46YFV87vTKJ9UDSddCQAIBDksFKaN3wLixAmig4ZD',
    'phone_number_id': '728170437054141',
    'business_account_id': '1499532764576536',
    'test_number': '+1 555 181 7191',  # Tu número de prueba Meta
    'api_version': 'v21.0'
}

def verify_meta_connection():
    """Verifica la conexión con Meta API"""
    print("🔍 Verificando conexión con Meta WhatsApp API...")
    
    try:
        url = f"https://graph.facebook.com/{META_CONFIG['api_version']}/{META_CONFIG['phone_number_id']}"
        headers = {
            "Authorization": f"Bearer {META_CONFIG['token']}"
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Conexión exitosa con Meta API")
            print(f"📱 Número: {data.get('display_phone_number', 'N/A')}")
            print(f"📝 Nombre verificado: {data.get('verified_name', 'N/A')}")
            print(f"🏢 WABA ID: {data.get('whatsapp_business_account_id', 'N/A')}")
            print(f"✅ Estado: {data.get('code_verification_status', 'N/A')}")
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"📋 Respuesta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error verificando conexión: {str(e)}")
        return False

def send_test_message():
    """Envía un mensaje de prueba"""
    print("\n📱 Enviando mensaje de prueba...")
    
    # Solicitar número destino
    to_number = input("Ingresa el número destino (ej: +56912345678): ").strip()
    if not to_number:
        print("❌ Número requerido")
        return False
    
    try:
        url = f"https://graph.facebook.com/{META_CONFIG['api_version']}/{META_CONFIG['phone_number_id']}/messages"
        headers = {
            "Authorization": f"Bearer {META_CONFIG['token']}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "to": to_number,
            "type": "text",
            "text": {
                "body": "🤖 ¡Hola! Soy tu asistente de e-commerce de Sintestesia.\n\n¿En qué puedo ayudarte hoy?\n\n• Ver productos\n• Consultar pedidos\n• Soporte técnico"
            }
        }
        
        print(f"📤 Enviando a: {to_number}")
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            message_id = result.get('messages', [{}])[0].get('id', 'N/A')
            print("✅ Mensaje enviado exitosamente")
            print(f"📨 ID del mensaje: {message_id}")
            print(f"📋 Respuesta completa: {json.dumps(result, indent=2)}")
            return True
        else:
            print(f"❌ Error enviando mensaje: {response.status_code}")
            print(f"📋 Respuesta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def send_template_message():
    """Envía un template de mensaje (hello_world)"""
    print("\n📋 Enviando template hello_world...")
    
    to_number = input("Ingresa el número destino (ej: +56912345678): ").strip()
    if not to_number:
        print("❌ Número requerido")
        return False
    
    try:
        url = f"https://graph.facebook.com/{META_CONFIG['api_version']}/{META_CONFIG['phone_number_id']}/messages"
        headers = {
            "Authorization": f"Bearer {META_CONFIG['token']}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "to": to_number,
            "type": "template",
            "template": {
                "name": "hello_world",
                "language": {
                    "code": "en_US"
                }
            }
        }
        
        print(f"📤 Enviando template a: {to_number}")
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
        print(f"❌ Error: {str(e)}")
        return False

def test_webhook_verification():
    """Prueba la verificación del webhook del servidor"""
    print("\n🔗 Probando webhook del servidor...")
    
    webhook_url = "https://webhook.sintestesia.cl/webhook/meta"
    verify_token = "sintestesia_verify_token_2024"
    test_challenge = "test_challenge_12345"
    
    try:
        params = {
            'hub.mode': 'subscribe',
            'hub.verify_token': verify_token,
            'hub.challenge': test_challenge
        }
        
        print(f"🔗 Probando: {webhook_url}")
        response = requests.get(webhook_url, params=params, timeout=10)
        
        if response.status_code == 200 and response.text == test_challenge:
            print("✅ Webhook verification exitosa")
            print(f"📋 Challenge devuelto correctamente: {response.text}")
            return True
        else:
            print(f"❌ Error en webhook verification: {response.status_code}")
            print(f"📋 Respuesta: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("⏰ Timeout - El servidor puede no estar ejecutándose")
        return False
    except Exception as e:
        print(f"❌ Error probando webhook: {str(e)}")
        return False

def show_meta_configuration():
    """Muestra la configuración actual de Meta"""
    print("\n📋 Configuración Meta WhatsApp:")
    print("=" * 40)
    print(f"📱 Número de prueba: {META_CONFIG['test_number']}")
    print(f"🆔 Phone Number ID: {META_CONFIG['phone_number_id']}")
    print(f"🏢 Business Account ID: {META_CONFIG['business_account_id']}")
    print(f"🔗 API Version: {META_CONFIG['api_version']}")
    print(f"🔑 Token: {META_CONFIG['token'][:20]}...")
    print()
    print("🔗 Webhook URL: https://webhook.sintestesia.cl/webhook/meta")
    print("🔑 Verify Token: sintestesia_verify_token_2024")

def show_curl_commands():
    """Muestra comandos curl para referencia"""
    print("\n📝 Comandos cURL de referencia:")
    print("=" * 40)
    
    # Comando para mensaje de texto
    text_curl = f'''
# Enviar mensaje de texto:
curl -X POST "https://graph.facebook.com/{META_CONFIG['api_version']}/{META_CONFIG['phone_number_id']}/messages" \\
  -H "Authorization: Bearer {META_CONFIG['token']}" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "messaging_product": "whatsapp",
    "to": "+56912345678",
    "type": "text",
    "text": {{
      "body": "¡Hola! Mensaje de prueba desde Sintestesia"
    }}
  }}'
'''
    
    # Comando para template
    template_curl = f'''
# Enviar template hello_world:
curl -X POST "https://graph.facebook.com/{META_CONFIG['api_version']}/{META_CONFIG['phone_number_id']}/messages" \\
  -H "Authorization: Bearer {META_CONFIG['token']}" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "messaging_product": "whatsapp",
    "to": "+56912345678",
    "type": "template",
    "template": {{
      "name": "hello_world",
      "language": {{
        "code": "en_US"
      }}
    }}
  }}'
'''
    
    print(text_curl)
    print(template_curl)

def main():
    """Función principal"""
    print("🧪 Probador Meta WhatsApp - Sintestesia")
    print("=" * 45)
    
    # Mostrar configuración
    show_meta_configuration()
    
    # Verificar conexión básica
    print("\n" + "=" * 30)
    if not verify_meta_connection():
        print("❌ No se pudo conectar con Meta API. Verifica tu token.")
        return
    
    # Probar webhook del servidor
    print("\n" + "=" * 30)
    test_webhook_verification()
    
    # Menú interactivo
    while True:
        print("\n🎯 Opciones de prueba:")
        print("1. Enviar mensaje de texto")
        print("2. Enviar template hello_world")
        print("3. Verificar conexión Meta API")
        print("4. Probar webhook del servidor")
        print("5. Mostrar comandos cURL")
        print("6. Salir")
        
        choice = input("\nSelecciona una opción (1-6): ").strip()
        
        if choice == "1":
            send_test_message()
        elif choice == "2":
            send_template_message()
        elif choice == "3":
            verify_meta_connection()
        elif choice == "4":
            test_webhook_verification()
        elif choice == "5":
            show_curl_commands()
        elif choice == "6":
            print("👋 ¡Hasta luego!")
            break
        else:
            print("❌ Opción inválida")

if __name__ == "__main__":
    main()