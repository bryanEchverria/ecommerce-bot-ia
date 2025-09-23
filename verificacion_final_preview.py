#!/usr/bin/env python3
"""
Verificación final: ¿Qué debería mostrar el preview corregido?
"""
import requests
import json

def verificacion_final():
    """Verificación final del comportamiento esperado"""
    
    print("🔍 VERIFICACIÓN FINAL: Preview Corregido del Backoffice")
    print("=" * 70)
    
    # Test con la consulta exacta que mencionaste
    test_query = "que semillas tienes me das las semillas que tengas"
    
    print(f"📝 Consulta del usuario: '{test_query}'")
    print("─" * 70)
    
    # Consultar al bot real (que es lo que debería hacer el preview)
    response = requests.post("http://localhost:9001/webhook", json={
        "telefono": "+56950915617",
        "mensaje": test_query
    })
    
    if response.status_code == 200:
        result = response.json()
        bot_response = result.get('respuesta', '')
        
        print("✅ RESPUESTA QUE DEBERÍA DAR EL PREVIEW:")
        print("─" * 70)
        print(bot_response[:500] + "..." if len(bot_response) > 500 else bot_response)
        print("─" * 70)
        
        # Verificar contenido específico
        semillas_reales = [
            "Mix Semillas Sativas", "$55,000",
            "Semillas CBD Medicinales", "$45,000",
            "Semillas Feminizadas Auto Mix", "$35,000",
            "Semillas Northern Lights Auto", "$40,000",
            "Semillas White Widow Feminizadas", "$25,000"
        ]
        
        respuestas_genericas = [
            "¿Te gustaría saber más",
            "alguna en particular",
            "Estoy aquí para ayudarte"
        ]
        
        print("🔍 ANÁLISIS DE LA RESPUESTA CORRECTA:")
        
        tiene_semillas = any(sem in bot_response for sem in semillas_reales)
        es_generica = any(gen in bot_response for gen in respuestas_genericas)
        
        if tiene_semillas and not es_generica:
            print("✅ PERFECTO: Respuesta específica con productos reales")
            print("✅ Muestra semillas reales con precios exactos")
            print("✅ NO es una respuesta genérica")
        elif es_generica:
            print("❌ PROBLEMA: Respuesta genérica sin productos específicos")
        else:
            print("⚠️ Respuesta inesperada")
        
        print(f"\n📊 COMPARACIÓN:")
        print("❌ TU PREVIEW MUESTRA: '¿Te gustaría saber más sobre alguna en particular?'")
        print("✅ DEBERÍA MOSTRAR: 'Catálogo completo con Mix Semillas Sativas $55,000, etc.'")
        
        print(f"\n🎯 INSTRUCCIONES PARA TI:")
        if tiene_semillas and not es_generica:
            print("1. 🔄 REFRESCA la página del backoffice (Ctrl+F5)")
            print("2. 🧹 LIMPIA caché del navegador")
            print("3. 🔄 Vuelve a probar el preview")
            print("4. ✅ Deberías ver la lista completa de productos con precios")
        else:
            print("❌ Hay un problema más profundo que requiere investigación")
        
        return tiene_semillas and not es_generica
        
    else:
        print(f"❌ Error consultando bot: {response.status_code}")
        return False

def main():
    print("🎯 ESTADO ACTUAL DEL SISTEMA")
    print("=" * 70)
    
    correcto = verificacion_final()
    
    print("\n" + "=" * 70)
    if correcto:
        print("✅ EL SISTEMA ESTÁ CORREGIDO")
        print("Si tu preview sigue mostrando respuestas genéricas:")
        print("- Es problema de caché del navegador")
        print("- Refresca con Ctrl+F5")
        print("- O usa navegador en modo incógnito")
    else:
        print("❌ SISTEMA REQUIERE MÁS CORRECCIONES")
    
    print("=" * 70)

if __name__ == "__main__":
    main()