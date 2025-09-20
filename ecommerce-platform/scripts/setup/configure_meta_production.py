#!/usr/bin/env python3
"""
Script para configurar Meta WhatsApp con los datos de producción
Basado en la configuración de Meta Business API
"""
import os

def create_env_file():
    """Crea el archivo .env con la configuración de Meta"""
    
    print("🔧 Configurando Meta WhatsApp con datos de producción...")
    
    # Datos de tu configuración Meta
    meta_config = {
        'WHATSAPP_TOKEN': 'EAAKlRZBfhpIIBPR9kSYQ7Jyk8ZBPZAkDyAYo4LCs5YxO9yUOYHLbveiUvnNF4hnpNvcldgTtMZAMGpoXuX1vkXZBGLDbZAZA32cZAt6rSwBvfD2O19fKuyvhltlME2MMKuYphJZAUHPXRjsrzpFGImVax4dEjcPj7INwGs2wX5jiSmqxslw7ZBDFYWHECW9SxOA92r1basoqOE46YFV87vTKJ9UDSddCQAIBDksFKaN3wLixAmig4ZD',
        'WHATSAPP_PHONE_NUMBER_ID': '728170437054141',
        'WHATSAPP_BUSINESS_ACCOUNT_ID': '1499532764576536',
        'GRAPH_API_VERSION': 'v21.0',
        'WA_PROVIDER': 'meta'
    }
    
    # Variables adicionales necesarias
    additional_config = {
        'WHATSAPP_VERIFY_TOKEN': 'tu_verify_token_seguro_123',
        'WHATSAPP_WEBHOOK_SECRET': '',  # Opcional para verificación de firma
        'BASE_URL': 'https://webhook.sintestesia.cl',
        'BACKEND_URL': 'http://localhost:8002',
        'OPENAI_API_KEY': 'tu_openai_key_aqui',
        'FLOW_API_KEY': 'tu_flow_key_aqui',
        'FLOW_SECRET_KEY': 'tu_flow_secret_aqui',
        'FLOW_BASE_URL': 'https://sandbox.flow.cl/api'
    }
    
    # Combinar configuraciones
    full_config = {**meta_config, **additional_config}
    
    # Crear contenido del archivo .env
    env_content = "# Meta WhatsApp Configuration - Production\n"
    env_content += "# Generated automatically from Meta Business API setup\n\n"
    
    for key, value in full_config.items():
        env_content += f"{key}={value}\n"
    
    # Escribir archivo en el directorio del bot
    bot_env_path = "/root/ecommerce-bot-ia/whatsapp-bot-fastapi/.env"
    
    try:
        with open(bot_env_path, 'w') as f:
            f.write(env_content)
        print(f"✅ Archivo .env creado en: {bot_env_path}")
        return True
    except Exception as e:
        print(f"❌ Error creando archivo .env: {str(e)}")
        return False

def test_meta_configuration():
    """Prueba la configuración de Meta"""
    import requests
    import json
    
    print("🧪 Probando configuración de Meta...")
    
    # Configuración de prueba
    token = 'EAAKlRZBfhpIIBPR9kSYQ7Jyk8ZBPZAkDyAYo4LCs5YxO9yUOYHLbveiUvnNF4hnpNvcldgTtMZAMGpoXuX1vkXZBGLDbZAZA32cZAt6rSwBvfD2O19fKuyvhltlME2MMKuYphJZAUHPXRjsrzpFGImVax4dEjcPj7INwGs2wX5jiSmqxslw7ZBDFYWHECW9SxOA92r1basoqOE46YFV87vTKJ9UDSddCQAIBDksFKaN3wLixAmig4ZD'
    phone_number_id = '728170437054141'
    
    try:
        # Probar acceso al Phone Number ID
        url = f"https://graph.facebook.com/v21.0/{phone_number_id}"
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Conexión con Meta API exitosa")
            print(f"📱 Número verificado: {data.get('display_phone_number', 'N/A')}")
            print(f"🏢 WABA ID: {data.get('whatsapp_business_account_id', 'N/A')}")
            print(f"✅ Status: {data.get('verified_name', 'Verificado')}")
            return True
        else:
            print(f"❌ Error conectando con Meta API: {response.status_code}")
            print(f"📋 Respuesta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error probando configuración: {str(e)}")
        return False

def setup_webhook_url():
    """Muestra las instrucciones para configurar el webhook en Meta"""
    print("\n🔗 Configuración del Webhook en Meta Business:")
    print("=" * 50)
    print("1. Ve a https://developers.facebook.com/")
    print("2. Selecciona tu aplicación")
    print("3. Ve a WhatsApp > Configuration > Webhook")
    print("4. Configura los siguientes valores:")
    print()
    print("   📋 Callback URL: https://webhook.sintestesia.cl/webhook/meta")
    print("   🔑 Verify Token: tu_verify_token_seguro_123")
    print("   📝 Webhook fields: messages")
    print()
    print("5. Haz clic en 'Verify and Save'")
    print()
    print("🧪 Para probar tu webhook:")
    print("   GET https://webhook.sintestesia.cl/webhook/meta/test")

def show_test_message_curl():
    """Muestra el comando curl para enviar mensaje de prueba"""
    print("\n📱 Comando para enviar mensaje de prueba:")
    print("=" * 50)
    
    curl_command = '''curl -X POST "https://graph.facebook.com/v21.0/728170437054141/messages" \\
-H "Authorization: Bearer EAAKlRZBfhpIIBPR9kSYQ7Jyk8ZBPZAkDyAYo4LCs5YxO9yUOYHLbveiUvnNF4hnpNvcldgTtMZAMGpoXuX1vkXZBGLDbZAZA32cZAt6rSwBvfD2O19fKuyvhltlME2MMKuYphJZAUHPXRjsrzpFGImVax4dEjcPj7INwGs2wX5jiSmqxslw7ZBDFYWHECW9SxOA92r1basoqOE46YFV87vTKJ9UDSddCQAIBDksFKaN3wLixAmig4ZD" \\
-H "Content-Type: application/json" \\
-d '{
  "messaging_product": "whatsapp",
  "to": "+56912345678",
  "type": "text",
  "text": {
    "body": "¡Hola! Soy tu asistente de e-commerce. ¿En qué puedo ayudarte hoy?"
  }
}'
'''
    
    print(curl_command)
    print("\n📝 Nota: Reemplaza '+56912345678' con tu número de teléfono")

def main():
    """Función principal"""
    print("🚀 Configurador Meta WhatsApp - Producción")
    print("=" * 50)
    
    # 1. Crear archivo .env
    if create_env_file():
        print("✅ Configuración guardada exitosamente")
    else:
        print("❌ Error en la configuración")
        return
    
    # 2. Probar conexión con Meta
    print("\n" + "=" * 30)
    if test_meta_configuration():
        print("✅ Meta API funcionando correctamente")
    else:
        print("⚠️  Revisa tu token de acceso")
    
    # 3. Mostrar instrucciones del webhook
    print("\n" + "=" * 30)
    setup_webhook_url()
    
    # 4. Mostrar comando de prueba
    print("\n" + "=" * 30)
    show_test_message_curl()
    
    print("\n✅ Configuración completada!")
    print("\n📋 Próximos pasos:")
    print("1. Configura el webhook en Meta Business (instrucciones arriba)")
    print("2. Ejecuta: docker-compose up whatsapp-bot -d")
    print("3. Prueba con: python test_meta_bot.py")
    print("4. Envía un mensaje WhatsApp al número: +1 555 181 7191")

if __name__ == "__main__":
    main()