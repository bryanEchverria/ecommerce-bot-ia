#!/usr/bin/env python3
"""
Script para enviar mensajes business-initiated via Twilio
Usa templates pre-aprobados para iniciar conversaciones
"""
import os
import requests
from requests.auth import HTTPBasicAuth
import json

# Configuración Twilio
ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
FROM_NUMBER = os.getenv('TWILIO_WHATSAPP_NUMBER', 'whatsapp:+14155238886')

def send_business_message(to_number, template_name=None, message_body=None):
    """
    Enviar mensaje business-initiated
    """
    url = f"https://api.twilio.com/2010-04-01/Accounts/{ACCOUNT_SID}/Messages.json"
    
    # Datos del mensaje
    data = {
        'From': FROM_NUMBER,
        'To': f'whatsapp:{to_number}',
    }
    
    # Si se especifica un template, usarlo
    if template_name:
        # Templates comunes de Twilio para sandbox
        templates = {
            'hello': 'Hello! This is a business-initiated message from Green House 🌿. Reply with any message to start chatting.',
            'welcome': 'Welcome to Green House! We specialize in premium cannabis products. How can we help you today?',
            'promo': '🔥 Special offer from Green House! Get 10% off your first order. Reply to learn more!',
            'reminder': 'Hi! This is a friendly reminder from Green House. We have new products available. Reply to see our catalog.'
        }
        
        data['Body'] = templates.get(template_name, templates['hello'])
    elif message_body:
        data['Body'] = message_body
    else:
        data['Body'] = "Hello from Green House 🌿! Reply to start chatting with our bot."
    
    print(f"📤 Enviando mensaje a: {to_number}")
    print(f"📝 Template: {template_name or 'custom'}")
    print(f"💬 Mensaje: {data['Body'][:50]}...")
    
    try:
        response = requests.post(
            url,
            auth=HTTPBasicAuth(ACCOUNT_SID, AUTH_TOKEN),
            data=data
        )
        
        if response.status_code == 201:
            result = response.json()
            print("✅ Mensaje enviado exitosamente!")
            print(f"📋 Message SID: {result['sid']}")
            print(f"📱 Status: {result['status']}")
            print(f"💰 Price: {result.get('price', 'N/A')}")
            return True
        else:
            print(f"❌ Error enviando mensaje: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def list_templates():
    """Mostrar templates disponibles"""
    templates = {
        'hello': 'Saludo básico de negocio',
        'welcome': 'Mensaje de bienvenida a Green House',
        'promo': 'Mensaje promocional con descuento',
        'reminder': 'Recordatorio de productos nuevos'
    }
    
    print("📋 Templates disponibles:")
    for key, desc in templates.items():
        print(f"  • {key}: {desc}")

if __name__ == "__main__":
    import sys
    
    print("📤 Twilio Business-Initiated Messages")
    print("=" * 40)
    
    # Mostrar templates
    list_templates()
    print()
    
    # Verificar argumentos
    if len(sys.argv) < 2:
        print("Uso:")
        print("  python3 send_whatsapp_message.py <numero> [template]")
        print("  python3 send_whatsapp_message.py +1234567890 welcome")
        print("  python3 send_whatsapp_message.py +1234567890 hello")
        exit(1)
    
    to_number = sys.argv[1]
    template = sys.argv[2] if len(sys.argv) > 2 else 'hello'
    
    # Enviar mensaje
    success = send_business_message(to_number, template)
    
    if success:
        print("\n🎉 ¡Mensaje enviado!")
        print("💡 Una vez que el usuario responda, tendrás 24h para enviar mensajes libres")
        print("🔍 Monitorea las respuestas con: /root/monitor_twilio.sh")
    else:
        print("\n❌ Error enviando mensaje")