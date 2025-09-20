#!/usr/bin/env python3
"""
Script para configurar automáticamente el webhook de Twilio
"""
import os
import requests
from requests.auth import HTTPBasicAuth
import json

# Configuración desde variables de entorno
ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
WEBHOOK_URL = 'https://webhook.sintestesia.cl/twilio/webhook'
STATUS_CALLBACK_URL = 'https://webhook.sintestesia.cl/twilio/status'

def configure_webhook():
    """Configurar webhook en Twilio"""
    print("🔧 Configurando webhook de Twilio...")
    print(f"📱 Account SID: {ACCOUNT_SID[:8]}...")
    print(f"🔗 Webhook URL: {WEBHOOK_URL}")
    
    # URL para configurar WhatsApp Sandbox
    url = f"https://api.twilio.com/2010-04-01/Accounts/{ACCOUNT_SID}/IncomingPhoneNumbers.json"
    
    # Headers
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    # Datos para actualizar
    data = {
        'SmsUrl': WEBHOOK_URL,
        'SmsMethod': 'POST',
        'StatusCallback': STATUS_CALLBACK_URL,
        'StatusCallbackMethod': 'POST'
    }
    
    try:
        # Hacer request a Twilio API
        response = requests.post(
            url,
            auth=HTTPBasicAuth(ACCOUNT_SID, AUTH_TOKEN),
            headers=headers,
            data=data
        )
        
        if response.status_code == 200:
            print("✅ Webhook configurado exitosamente!")
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error configurando webhook: {str(e)}")
        return False

def test_webhook():
    """Probar que el webhook responde"""
    print("\n🧪 Probando webhook...")
    
    test_data = {
        'From': 'whatsapp:+3456789012',
        'To': 'whatsapp:+12233886885',
        'Body': 'test',
        'MessageSid': 'SM_test_123456'
    }
    
    try:
        response = requests.post(
            WEBHOOK_URL,
            data=test_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        
        if response.status_code == 200:
            print("✅ Webhook responde correctamente!")
            print(f"Response: {response.text[:100]}...")
            return True
        else:
            print(f"❌ Webhook error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error probando webhook: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Configurando Twilio + WhatsApp...")
    print("=" * 50)
    
    # Verificar variables
    if not ACCOUNT_SID or not AUTH_TOKEN:
        print("❌ Variables de entorno faltantes:")
        print("   TWILIO_ACCOUNT_SID")
        print("   TWILIO_AUTH_TOKEN")
        exit(1)
    
    # Configurar webhook
    webhook_ok = configure_webhook()
    
    # Probar webhook
    test_ok = test_webhook()
    
    print("\n" + "=" * 50)
    if webhook_ok and test_ok:
        print("🎉 ¡Configuración completada!")
        print("\n📋 Próximos pasos:")
        print("1. Ve a Twilio Console > WhatsApp Sandbox")
        print("2. Agrega +1 415 523-8886 a WhatsApp")  
        print("3. Envía: 'join worried-cat'")
        print("4. Prueba enviando un mensaje")
        print(f"\n🔍 Monitor: /root/monitor_twilio.sh")
    else:
        print("❌ Configuración incompleta")
        print("Revisa manualmente en Twilio Console")