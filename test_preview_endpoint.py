#!/usr/bin/env python3
"""
Test directo del endpoint de preview corregido
"""
import requests
import json
import subprocess

def test_preview_endpoint_direct():
    """Test directo del endpoint preview usando el mismo método que el frontend"""
    
    print("🔧 TESTING: Endpoint de Preview Corregido")
    print("=" * 60)
    
    # Simulamos exactamente la llamada del frontend con debug
    test_config = {
        "prompt_config": {
            "system_prompt": "Eres ACME Cannabis Assistant. Usa datos reales de BD.",
            "style_overrides": {
                "tono": "profesional",
                "usar_emojis": True,
                "limite_respuesta_caracteres": 400,
                "incluir_contexto_empresa": True
            },
            "nlu_params": {
                "modelo": "gpt-4o-mini",
                "temperature_nlu": 0.3,
                "max_tokens_nlu": 150
            },
            "nlg_params": {
                "modelo": "gpt-4o-mini",
                "temperature_nlg": 0.7,
                "max_tokens_nlg": 300
            }
        },
        "test_message": "debug que semillas sativas tienes",
        "include_products": True
    }
    
    # Test 1: Debug mode para ver qué está pasando
    print("\n1️⃣ Testing con debug mode...")
    
    # Usar curl para evitar problemas de middleware
    curl_cmd = [
        'curl', '-X', 'POST',
        'http://localhost:8002/acme-cannabis-2024/prompt/preview',
        '-H', 'Content-Type: application/json',
        '-H', 'X-Tenant-Id: acme-cannabis-2024',
        '-d', json.dumps(test_config)
    ]
    
    try:
        result = subprocess.run(curl_cmd, capture_output=True, text=True, timeout=30)
        print(f"Status Code: {result.returncode}")
        print(f"Response: {result.stdout}")
        
        if result.stderr:
            print(f"Error: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        print("❌ Timeout - endpoint muy lento")
    except Exception as e:
        print(f"❌ Error ejecutando curl: {e}")
    
    # Test 2: Sin debug para ver respuesta normal
    print("\n2️⃣ Testing sin debug...")
    
    test_config["test_message"] = "que semillas sativas tienes"
    
    curl_cmd[-1] = json.dumps(test_config)
    
    try:
        result = subprocess.run(curl_cmd, capture_output=True, text=True, timeout=30)
        print(f"Response: {result.stdout}")
        
        if result.stdout and "Super Lemon Haze" in result.stdout:
            print("❌ SIGUE INVENTANDO: Menciona productos que no existen")
        elif result.stdout and ("Mix Semillas Sativas" in result.stdout or "$55,000" in result.stdout):
            print("✅ CORRECTO: Usa productos reales de BD")
        else:
            print("⚠️  Respuesta inesperada")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_preview_endpoint_direct()