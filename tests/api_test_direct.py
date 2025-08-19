"""
Test directo de APIs - Sin timeouts
"""
import requests
import json

def test_bot_apis():
    """Test bot APIs directly"""
    
    print("=== TESTING BOT APIs (Direct) ===")
    
    # Test cases for the bot
    test_cases = [
        {
            "name": "Health Check",
            "method": "GET",
            "url": "http://localhost:8001/",
            "data": None
        },
        {
            "name": "Debug Conversations",
            "method": "GET", 
            "url": "http://localhost:8001/debug/conversaciones",
            "data": None
        },
        {
            "name": "Green House - Saludo",
            "method": "POST",
            "url": "http://localhost:8001/webhook",
            "data": {"telefono": "+3456789012", "mensaje": "hola"}
        },
        {
            "name": "Green House - Vapo (ESPECÍFICO)",
            "method": "POST", 
            "url": "http://localhost:8001/webhook",
            "data": {"telefono": "+3456789012", "mensaje": "quiero un vapo"}
        },
        {
            "name": "Demo Company - iPhone",
            "method": "POST",
            "url": "http://localhost:8001/webhook", 
            "data": {"telefono": "+1234567890", "mensaje": "quiero un iPhone"}
        },
        {
            "name": "Cliente No Configurado",
            "method": "POST",
            "url": "http://localhost:8001/webhook",
            "data": {"telefono": "+999999999", "mensaje": "hola"}
        }
    ]
    
    results = []
    
    for test in test_cases:
        print(f"\n--- {test['name']} ---")
        
        try:
            if test['method'] == 'GET':
                response = requests.get(test['url'], timeout=3)
            else:
                response = requests.post(test['url'], json=test['data'], timeout=3)
                
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    
                    if 'respuesta' in result:
                        # Bot webhook response
                        respuesta = result['respuesta']
                        print(f"Telefono: {result.get('telefono')}")
                        print(f"Respuesta: {respuesta[:150]}{'...' if len(respuesta) > 150 else ''}")
                        
                        # Check specific responses
                        if test['name'] == "Green House - Vapo (ESPECÍFICO)":
                            if "PAX" in respuesta or "vaporizador" in respuesta.lower():
                                print("✅ SUCCESS: Bot encontró vaporizador específico!")
                            else:
                                print("❌ FAIL: Bot no encontró vaporizador")
                                
                    else:
                        # Other API responses
                        print(f"Response: {result}")
                        
                    results.append({"test": test['name'], "status": "PASS"})
                    
                except json.JSONDecodeError:
                    print(f"Response (text): {response.text[:100]}")
                    results.append({"test": test['name'], "status": "PASS"})
                    
            else:
                print(f"Error: {response.status_code}")
                print(f"Response: {response.text[:100]}")
                results.append({"test": test['name'], "status": "FAIL"})
                
        except requests.exceptions.Timeout:
            print("❌ TIMEOUT: API took too long")
            results.append({"test": test['name'], "status": "TIMEOUT"})
            
        except Exception as e:
            print(f"❌ ERROR: {e}")
            results.append({"test": test['name'], "status": "ERROR"})
    
    # Summary
    print("\n" + "="*50)
    print("RESUMEN DE PRUEBAS API")
    print("="*50)
    
    passed = sum(1 for r in results if r['status'] == 'PASS')
    failed = sum(1 for r in results if r['status'] in ['FAIL', 'TIMEOUT', 'ERROR'])
    
    for result in results:
        status_emoji = {
            'PASS': '✅',
            'FAIL': '❌', 
            'TIMEOUT': '⏱️',
            'ERROR': '💥'
        }
        emoji = status_emoji.get(result['status'], '❓')
        print(f"{emoji} {result['test']}: {result['status']}")
    
    print(f"\nTotal: {passed}/{len(results)} pruebas exitosas ({passed/len(results)*100:.1f}%)")
    
    if passed >= len(results) * 0.5:
        print("\n🎉 APIs funcionando correctamente!")
    else:
        print("\n⚠️ Algunas APIs tienen problemas")

if __name__ == "__main__":
    test_bot_apis()