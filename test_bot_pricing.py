#!/usr/bin/env python3
"""
Test script para verificar que el bot use precios reales de la BD
"""
import requests
import json

def test_whatsapp_message(telefono, mensaje):
    """Simula mensaje de WhatsApp via webhook"""
    webhook_url = "http://localhost:9001/webhook"
    
    payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "test_entry",
                "changes": [
                    {
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {
                                "display_phone_number": "+14155238886",
                                "phone_number_id": "test_phone_id"
                            },
                            "messages": [
                                {
                                    "from": telefono,
                                    "id": f"msg_{telefono}_{hash(mensaje)}",
                                    "timestamp": "1234567890",
                                    "text": {
                                        "body": mensaje
                                    },
                                    "type": "text"
                                }
                            ]
                        },
                        "field": "messages"
                    }
                ]
            }
        ]
    }
    
    try:
        response = requests.post(webhook_url, json=payload, timeout=30)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 TESTING BOT PRICING WITH REAL BD DATA")
    print("=" * 50)
    
    # Test 1: White Widow (precio en BD: $40,000)
    print("\n1️⃣ Testing White Widow price:")
    test_whatsapp_message("+56950915617", "precio white widow")
    
    # Test 2: Northern Lights (precio en BD: $25,000) 
    print("\n2️⃣ Testing Northern Lights price:")
    test_whatsapp_message("+56950915617", "cuanto cuesta northern lights")
    
    # Test 3: Producto general (múltiples resultados)
    print("\n3️⃣ Testing general product query:")
    test_whatsapp_message("+56950915617", "quiero semillas indicas")