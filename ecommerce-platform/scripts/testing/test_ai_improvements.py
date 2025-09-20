#!/usr/bin/env python3
"""
🧪 SCRIPT DE PRUEBA - MEJORAS DE IA
Prueba las nuevas funcionalidades de IA implementadas
"""
import requests
import json
import time
from datetime import datetime

# Configuración
BOT_URL = "http://localhost:9001/webhook"
BACKEND_URL = "http://localhost:8000/api"
TEST_PHONE = "+56950915617"

def test_bot_response(mensaje, description=""):
    """Prueba una respuesta del bot y mide el tiempo"""
    print(f"\n{'='*60}")
    print(f"🧪 PRUEBA: {description}")
    print(f"📱 Enviando: '{mensaje}'")
    print(f"{'='*60}")
    
    start_time = time.time()
    
    try:
        response = requests.post(BOT_URL, json={
            "telefono": TEST_PHONE,
            "mensaje": mensaje
        }, timeout=30)
        
        end_time = time.time()
        response_time = round((end_time - start_time) * 1000)
        
        if response.status_code == 200:
            bot_response = response.text
            print(f"✅ Respuesta ({response_time}ms):")
            print(f"🤖 {bot_response}")
            return {"success": True, "response": bot_response, "time_ms": response_time}
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            return {"success": False, "error": response.text}
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return {"success": False, "error": str(e)}

def test_ai_analytics():
    """Prueba los endpoints de analytics de IA"""
    print(f"\n{'='*60}")
    print(f"📊 PROBANDO ANALYTICS DE IA")
    print(f"{'='*60}")
    
    # Nota: Necesitaríamos un token de autenticación real para esto
    # Por ahora solo mostramos los endpoints disponibles
    
    endpoints = [
        "/ai-analytics/conversation-stats",
        "/ai-analytics/intent-analysis", 
        "/ai-analytics/product-performance",
        "/ai-analytics/conversation-flow",
        "/ai-analytics/user-behavior",
        "/ai-analytics/training-data"
    ]
    
    print("📋 Endpoints de Analytics disponibles:")
    for endpoint in endpoints:
        print(f"   • GET {BACKEND_URL}{endpoint}")
    
    print("\n💡 Para probar estos endpoints necesitas:")
    print("   1. Autenticarte en el backoffice")
    print("   2. Obtener un Bearer token")
    print("   3. Hacer requests con el header Authorization")

def run_comprehensive_tests():
    """Ejecuta una suite completa de pruebas"""
    print("🚀 INICIANDO PRUEBAS COMPLETAS DE IA MEJORADA")
    print("=" * 80)
    
    tests = [
        # Pruebas de detección de intención mejorada
        ("hola", "Saludo personalizado con contexto"),
        ("que vaporizador tienes", "Consulta específica de producto"),
        ("tienes northern lights?", "Búsqueda específica por nombre"),
        ("que aceites tienes", "Consulta por categoría"),
        ("quiero comprar semillas", "Intención de compra detectada"),
        ("ver catalogo completo", "Solicitud de catálogo organizado"),
        ("cuanto cuesta el aceite cbd", "Consulta de precio específico"),
        ("necesito algo para dormir", "Consulta por efecto/uso"),
        ("gracias", "Despedida/agradecimiento"),
        ("no me gustó la respuesta", "Feedback negativo")
    ]
    
    results = []
    
    for mensaje, description in tests:
        result = test_bot_response(mensaje, description)
        results.append({
            "test": description,
            "message": mensaje,
            "result": result
        })
        time.sleep(2)  # Esperar entre pruebas
    
    # Resumen de resultados
    print(f"\n{'='*80}")
    print("📊 RESUMEN DE PRUEBAS")
    print(f"{'='*80}")
    
    successful_tests = sum(1 for r in results if r["result"]["success"])
    total_tests = len(results)
    avg_response_time = sum(r["result"].get("time_ms", 0) for r in results if r["result"]["success"]) / successful_tests if successful_tests > 0 else 0
    
    print(f"✅ Pruebas exitosas: {successful_tests}/{total_tests}")
    print(f"⏱️  Tiempo promedio de respuesta: {avg_response_time:.0f}ms")
    
    if successful_tests == total_tests:
        print("🎉 ¡TODAS LAS PRUEBAS PASARON!")
    else:
        print("⚠️  Algunas pruebas fallaron, revisar logs arriba")
    
    # Mostrar pruebas de analytics
    test_ai_analytics()
    
    return results

def test_specific_ai_features():
    """Prueba características específicas de IA"""
    print(f"\n{'='*60}")
    print("🤖 PROBANDO CARACTERÍSTICAS ESPECÍFICAS DE IA")
    print(f"{'='*60}")
    
    # Test 1: Contexto de conversación
    print("\n1️⃣ PRUEBA DE CONTEXTO:")
    test_bot_response("hola", "Primera interacción")
    time.sleep(1)
    test_bot_response("que productos tienes", "Segunda interacción (debería recordar contexto)")
    time.sleep(1)
    test_bot_response("quiero el primero", "Referencia contextual")
    
    # Test 2: Detección mejorada de intenciones
    print("\n2️⃣ PRUEBA DE DETECCIÓN AVANZADA:")
    test_bot_response("ando buscando algo para relajarme", "Consulta indirecta")
    time.sleep(1)
    test_bot_response("me duele la cabeza", "Consulta por síntoma")
    time.sleep(1)
    test_bot_response("es para mi mamá que no puede dormir", "Consulta para terceros")
    
    # Test 3: Respuestas personalizadas
    print("\n3️⃣ PRUEBA DE PERSONALIZACIÓN:")
    test_bot_response("ya compré antes aquí", "Cliente recurrente")
    time.sleep(1)
    test_bot_response("soy nuevo aquí", "Cliente nuevo")

if __name__ == "__main__":
    print("🤖 SISTEMA DE PRUEBAS - MEJORAS DE IA")
    print("====================================")
    print(f"🕐 Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Verificar conectividad
    try:
        response = requests.get("http://localhost:9001/health", timeout=5)
        if response.status_code == 200:
            print("✅ Bot WhatsApp está funcionando")
        else:
            print("❌ Bot WhatsApp no responde correctamente")
            exit(1)
    except:
        print("❌ No se puede conectar al bot WhatsApp")
        print("💡 Asegúrate de que el contenedor esté corriendo:")
        print("   docker-compose up whatsapp-bot")
        exit(1)
    
    # Ejecutar pruebas
    print("\n" + "="*80)
    print("EJECUTANDO SUITE DE PRUEBAS COMPLETA")
    print("="*80)
    
    # Pruebas principales
    results = run_comprehensive_tests()
    
    # Pruebas específicas de IA
    test_specific_ai_features()
    
    print(f"\n🕐 Fin: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎯 Pruebas completadas!")
    
    # Instrucciones para ver analytics
    print(f"\n{'='*80}")
    print("📊 PRÓXIMOS PASOS - ANALYTICS")
    print(f"{'='*80}")
    print("1. Inicia el backend: cd backend && python main.py")
    print("2. Ve a: http://localhost:8000/docs")
    print("3. Busca la sección 'ai-analytics'")
    print("4. Autentica con tu usuario del backoffice")
    print("5. Prueba los endpoints de analytics")
    print("6. Revisa las métricas de conversaciones y mejoras de IA")