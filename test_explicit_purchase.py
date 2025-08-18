import requests
import json

def test_explicit_purchase():
    webhook_url = "http://localhost:8003/webhook"
    
    # Test explicit purchase confirmation with keyword
    print("Testing explicit purchase confirmation...")
    
    # Step 1: Ask about product
    response = requests.post(webhook_url, json={
        "telefono": "56912345679", 
        "mensaje": "hola, quiero comprar un iPhone 15"
    })
    print(f"1. Product inquiry: {response.json()['respuesta'][:100]}...")
    
    # Step 2: Specify quantity
    response = requests.post(webhook_url, json={
        "telefono": "56912345679", 
        "mensaje": "quiero 2 unidades"
    })
    print(f"2. Quantity: {response.json()['respuesta'][:100]}...")
    
    # Step 3: Explicit confirmation using keywords that should trigger payment
    test_confirmations = [
        "confirmo compra",
        "proceder con el pago", 
        "si, confirmo",
        "quiero pagar"
    ]
    
    for confirmation in test_confirmations:
        print(f"\nTesting confirmation: '{confirmation}'")
        response = requests.post(webhook_url, json={
            "telefono": "56912345679", 
            "mensaje": confirmation
        })
        
        if response.status_code == 200:
            resp_text = response.json()['respuesta']
            print(f"Response: {resp_text[:150]}...")
            
            if "flow.cl" in resp_text:
                print("✓ Payment link generated successfully!")
                break
            elif "pago" in resp_text.lower():
                print("Payment process mentioned but no link yet")
            else:
                print("No payment process triggered")
        else:
            print(f"Error: {response.status_code}")

if __name__ == "__main__":
    test_explicit_purchase()