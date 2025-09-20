#!/usr/bin/env python3
"""
Script para configurar automáticamente el webhook de Meta WhatsApp Cloud API
"""
import os
import requests
import json
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración desde variables de entorno
WHATSAPP_TOKEN = os.getenv('WHATSAPP_TOKEN')
WHATSAPP_PHONE_NUMBER_ID = os.getenv('WHATSAPP_PHONE_NUMBER_ID')
GRAPH_API_VERSION = os.getenv('GRAPH_API_VERSION', 'v21.0')
WEBHOOK_VERIFY_TOKEN = os.getenv('WHATSAPP_VERIFY_TOKEN')

# URLs
WEBHOOK_URL = 'https://webhook.sintestesia.cl/webhook/meta'
BASE_URL = 'https://webhook.sintestesia.cl'

def verify_configuration():
    """Verifica que todas las variables necesarias están configuradas"""
    missing_vars = []
    
    if not WHATSAPP_TOKEN:
        missing_vars.append('WHATSAPP_TOKEN')
    if not WHATSAPP_PHONE_NUMBER_ID:
        missing_vars.append('WHATSAPP_PHONE_NUMBER_ID')
    if not WEBHOOK_VERIFY_TOKEN:
        missing_vars.append('WHATSAPP_VERIFY_TOKEN')
    
    if missing_vars:
        print("❌ Faltan las siguientes variables de entorno:")
        for var in missing_vars:
            print(f"   - {var}")
        return False
    
    print("✅ Todas las variables de entorno están configuradas")
    return True

def get_whatsapp_business_account_id():
    """Obtiene el ID de la cuenta de WhatsApp Business"""
    try:
        url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{WHATSAPP_PHONE_NUMBER_ID}"
        headers = {
            "Authorization": f"Bearer {WHATSAPP_TOKEN}"
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            waba_id = data.get('whatsapp_business_account_id')
            print(f"📱 WhatsApp Business Account ID: {waba_id}")
            return waba_id
        else:
            print(f"❌ Error obteniendo WABA ID: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

def configure_webhook(waba_id):
    """Configura el webhook en Meta"""
    try:
        print("🔧 Configurando webhook de Meta WhatsApp...")
        print(f"📱 WABA ID: {waba_id}")
        print(f"🔗 Webhook URL: {WEBHOOK_URL}")
        
        url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{waba_id}/subscriptions"
        headers = {
            "Authorization": f"Bearer {WHATSAPP_TOKEN}",
            "Content-Type": "application/json"
        }
        
        # Configurar webhook
        webhook_data = {
            "object": "whatsapp_business_account",
            "callback_url": WEBHOOK_URL,
            "verify_token": WEBHOOK_VERIFY_TOKEN,
            "fields": "messages,message_deliveries,message_reads,message_echoes"
        }
        
        response = requests.post(url, headers=headers, json=webhook_data)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Webhook configurado exitosamente")
            print(f"📋 Respuesta: {json.dumps(result, indent=2)}")
            return True
        else:
            print(f"❌ Error configurando webhook: {response.status_code}")
            print(f"📋 Respuesta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error configurando webhook: {str(e)}")
        return False

def test_webhook():
    """Prueba el webhook configurado"""
    try:
        print("🧪 Probando webhook...")
        
        test_url = f"{BASE_URL}/webhook/meta/test"
        response = requests.get(test_url)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Webhook de prueba exitoso")
            print(f"📋 Respuesta: {json.dumps(result, indent=2)}")
            return True
        else:
            print(f"❌ Error en prueba de webhook: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error probando webhook: {str(e)}")
        return False

def get_webhook_status(waba_id):
    """Obtiene el estado actual del webhook"""
    try:
        print("📊 Verificando estado del webhook...")
        
        url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{waba_id}/subscriptions"
        headers = {
            "Authorization": f"Bearer {WHATSAPP_TOKEN}"
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            print("📋 Estado actual del webhook:")
            print(json.dumps(result, indent=2))
            return result
        else:
            print(f"❌ Error obteniendo estado del webhook: {response.status_code}")
            print(f"📋 Respuesta: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error obteniendo estado del webhook: {str(e)}")
        return None

def main():
    """Función principal"""
    print("🚀 Configurador de Webhook Meta WhatsApp Cloud API")
    print("=" * 50)
    
    # 1. Verificar configuración
    if not verify_configuration():
        print("❌ Configuración incompleta. Configura las variables de entorno necesarias.")
        return
    
    # 2. Obtener WABA ID
    waba_id = get_whatsapp_business_account_id()
    if not waba_id:
        print("❌ No se pudo obtener el WhatsApp Business Account ID")
        return
    
    # 3. Obtener estado actual
    print("\n" + "=" * 30)
    current_status = get_webhook_status(waba_id)
    
    # 4. Configurar webhook
    print("\n" + "=" * 30)
    success = configure_webhook(waba_id)
    
    if success:
        # 5. Probar webhook
        print("\n" + "=" * 30)
        test_webhook()
        
        print("\n✅ Configuración completada!")
        print("\n📋 Próximos pasos:")
        print("1. Verifica que tu servidor esté ejecutándose en:")
        print(f"   {BASE_URL}")
        print("2. Envía un mensaje de prueba a tu número de WhatsApp Business")
        print("3. Revisa los logs del servidor para confirmar que los mensajes se reciben")
    else:
        print("❌ La configuración falló. Revisa los errores anteriores.")

if __name__ == "__main__":
    main()