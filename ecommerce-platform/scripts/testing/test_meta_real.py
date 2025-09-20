#!/usr/bin/env python3
"""
Script de prueba con el formato exacto del ejemplo cURL proporcionado
"""
import requests
import json

# Configuración exacta del ejemplo
META_CONFIG = {
    'token': 'EAAKlRZBfhpIIBPR9kSYQ7Jyk8ZBPZAkDyAYo4LCs5YxO9yUOYHLbveiUvnNF4hnpNvcldgTtMZAMGpoXuX1vkXZBGLDbZAZA32cZAt6rSwBvfD2O19fKuyvhltlME2MMKuYphJZAUHPXRjsrzpFGImVax4dEjcPj7INwGs2wX5jiSmqxslw7ZBDFYWHECW9SxOA92r1basoqOE46YFV87vTKJ9UDSddCQAIBDksFKaN3wLixAmig4ZD',
    'phone_number_id': '728170437054141',
    'api_version': 'v22.0',  # Usando v22.0 como en tu ejemplo
    'test_number': '56950915617'  # Tu número de prueba
}

def send_hello_world_template():
    """Envía el template hello_world usando el formato exacto del ejemplo"""
    print("📋 Enviando template hello_world (formato exacto del ejemplo)...")
    
    try:
        url = f"https://graph.facebook.com/{META_CONFIG['api_version']}/{META_CONFIG['phone_number_id']}/messages"
        headers = {
            "Authorization": f"Bearer {META_CONFIG['token']}",
            "Content-Type": "application/json"
        }
        
        # Payload exacto del ejemplo
        payload = {
            "messaging_product": "whatsapp",
            "to": META_CONFIG['test_number'],
            "type": "template",
            "template": {
                "name": "hello_world",
                "language": {
                    "code": "en_US"
                }
            }
        }
        
        print(f"📤 Enviando a: +{META_CONFIG['test_number']}")
        print(f"🔗 URL: {url}")
        print(f"📦 Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(url, headers=headers, json=payload)
        
        print(f"\n📡 Status Code: {response.status_code}")
        print(f"📋 Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Template enviado exitosamente")
            print(f"📨 Respuesta: {json.dumps(result, indent=2)}")
            return True
        else:
            print(f"❌ Error enviando template: {response.status_code}")
            print(f"📋 Respuesta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def send_text_message():
    """Envía un mensaje de texto usando el mismo formato"""
    print("💬 Enviando mensaje de texto...")
    
    try:
        url = f"https://graph.facebook.com/{META_CONFIG['api_version']}/{META_CONFIG['phone_number_id']}/messages"
        headers = {
            "Authorization": f"Bearer {META_CONFIG['token']}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "to": META_CONFIG['test_number'],
            "type": "text",
            "text": {
                "body": "🤖 Hola! Soy el bot de Sintestesia. Este es un mensaje de prueba usando la API v22.0"
            }
        }
        
        print(f"📤 Enviando a: +{META_CONFIG['test_number']}")
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Mensaje enviado exitosamente")
            print(f"📨 Respuesta: {json.dumps(result, indent=2)}")
            return True
        else:
            print(f"❌ Error enviando mensaje: {response.status_code}")
            print(f"📋 Respuesta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_with_custom_number():
    """Permite probar con un número personalizado"""
    print("📱 Enviar a número personalizado...")
    
    custom_number = input("Ingresa el número (formato: 56912345678): ").strip()
    if not custom_number:
        print("❌ Número requerido")
        return False
    
    # Usar el número personalizado
    original_number = META_CONFIG['test_number']
    META_CONFIG['test_number'] = custom_number
    
    print("\nSelecciona el tipo de mensaje:")
    print("1. Mensaje de texto")
    print("2. Template hello_world")
    
    choice = input("Opción (1-2): ").strip()
    
    success = False
    if choice == "1":
        success = send_text_message()
    elif choice == "2":
        success = send_hello_world_template()
    else:
        print("❌ Opción inválida")
    
    # Restaurar número original
    META_CONFIG['test_number'] = original_number
    return success

def show_exact_curl():
    """Muestra el comando cURL exacto del ejemplo"""
    print("\n📝 Comando cURL exacto del ejemplo:")
    print("=" * 50)
    
    curl_command = f'''curl -i -X POST \\
  https://graph.facebook.com/{META_CONFIG['api_version']}/{META_CONFIG['phone_number_id']}/messages \\
  -H 'Authorization: Bearer {META_CONFIG['token']}' \\
  -H 'Content-Type: application/json' \\
  -d '{{
    "messaging_product": "whatsapp",
    "to": "{META_CONFIG['test_number']}",
    "type": "template",
    "template": {{
      "name": "hello_world",
      "language": {{
        "code": "en_US"
      }}
    }}
  }}'
'''
    
    print(curl_command)

def verify_api_access():
    """Verifica el acceso a la API usando v22.0"""
    print("🔍 Verificando acceso a Meta API v22.0...")
    
    try:
        url = f"https://graph.facebook.com/{META_CONFIG['api_version']}/{META_CONFIG['phone_number_id']}"
        headers = {
            "Authorization": f"Bearer {META_CONFIG['token']}"
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Acceso exitoso a Meta API v22.0")
            print(f"📱 Número: {data.get('display_phone_number', 'N/A')}")
            print(f"📝 Nombre: {data.get('verified_name', 'N/A')}")
            print(f"🏢 WABA ID: {data.get('whatsapp_business_account_id', 'N/A')}")
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"📋 Respuesta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def main():
    """Función principal"""
    print("🧪 Prueba Meta WhatsApp - Formato Exacto")
    print("=" * 45)
    print(f"📱 Número destino: +{META_CONFIG['test_number']}")
    print(f"🔗 API Version: {META_CONFIG['api_version']}")
    print(f"🆔 Phone ID: {META_CONFIG['phone_number_id']}")
    
    # Verificar acceso básico
    print("\n" + "=" * 30)
    if not verify_api_access():
        print("❌ No se pudo verificar el acceso a la API")
        return
    
    # Menú de opciones
    while True:
        print("\n🎯 Opciones:")
        print("1. Enviar template hello_world (ejemplo exacto)")
        print("2. Enviar mensaje de texto")
        print("3. Probar con número personalizado")
        print("4. Mostrar comando cURL exacto")
        print("5. Verificar acceso API")
        print("6. Salir")
        
        choice = input("\nSelecciona (1-6): ").strip()
        
        if choice == "1":
            send_hello_world_template()
        elif choice == "2":
            send_text_message()
        elif choice == "3":
            test_with_custom_number()
        elif choice == "4":
            show_exact_curl()
        elif choice == "5":
            verify_api_access()
        elif choice == "6":
            print("👋 ¡Hasta luego!")
            break
        else:
            print("❌ Opción inválida")

if __name__ == "__main__":
    main()