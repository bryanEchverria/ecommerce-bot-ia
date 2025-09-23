#!/usr/bin/env python3
"""
Simulación del preview usando el bot que SÍ funciona
"""
import requests
import json

def test_preview_simulation():
    """Simula el preview usando el endpoint del bot que funciona"""
    
    print("🔧 SIMULACIÓN: Preview usando bot que funciona")
    print("=" * 60)
    
    # Test exactamente lo que hace el preview del backoffice
    test_message = "que semillas sativas tienes"
    
    print(f"📝 Mensaje de prueba: '{test_message}'")
    print("🤖 Respuesta del bot (que debería ser igual al preview):")
    
    # Llamar al bot que SÍ funciona
    response = requests.post("http://localhost:9001/webhook", json={
        "telefono": "+56950915617",
        "mensaje": test_message
    })
    
    if response.status_code == 200:
        result = response.json()
        bot_response = result.get('respuesta', '')
        
        print(f"✅ Respuesta recibida ({len(bot_response)} caracteres):")
        print("─" * 40)
        print(bot_response)
        print("─" * 40)
        
        # Verificar que usa productos reales
        productos_reales = [
            "Mix Semillas Sativas",
            "Semillas CBD Medicinales", 
            "Semillas Northern Lights Auto",
            "Semillas White Widow Feminizadas",
            "$55,000", "$45,000", "$40,000", "$25,000"
        ]
        
        productos_inventados = [
            "Super Lemon Haze",
            "Durban Poison", 
            "Jack Herer",
            "$10-$15"
        ]
        
        print("\n🔍 VERIFICACIÓN:")
        tiene_reales = any(prod in bot_response for prod in productos_reales)
        tiene_inventados = any(prod in bot_response for prod in productos_inventados)
        
        if tiene_reales and not tiene_inventados:
            print("✅ CORRECTO: Usa productos reales de BD")
            print("✅ NO inventa productos inexistentes")
        elif tiene_inventados:
            print("❌ ERROR: Sigue inventando productos")
            for prod in productos_inventados:
                if prod in bot_response:
                    print(f"   🚫 Menciona: {prod}")
        else:
            print("⚠️  Respuesta inesperada")
        
        print(f"\n🎯 CONCLUSIÓN:")
        if tiene_reales and not tiene_inventados:
            print("El BOT funciona correctamente con datos reales.")
            print("El PREVIEW debe dar la misma respuesta.")
            print("Si el preview da respuesta diferente, hay inconsistencia.")
        else:
            print("Hay problemas en el bot base que deben corregirse.")
            
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"Response: {response.text}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_preview_simulation()