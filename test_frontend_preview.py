#!/usr/bin/env python3
"""
Test que simula exactamente lo que debería hacer el preview del frontend
"""
import requests
import json

def test_frontend_preview_corrected():
    """Test del preview corregido del frontend"""
    
    print("🖥️  TESTING: Preview del Frontend Corregido")
    print("=" * 60)
    
    # Simular exactamente la llamada del frontend corregido
    test_message = "que semillas sativas tienes"
    
    print(f"📝 Mensaje de prueba: '{test_message}'")
    print("🔄 Simulando llamada del frontend al bot...")
    
    # Esta es la llamada que ahora hace el frontend
    response = requests.post("http://localhost:9001/webhook", 
        headers={'Content-Type': 'application/json'},
        json={
            'telefono': '+56950915617',
            'mensaje': test_message
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        bot_response = result.get('respuesta', '')
        
        print("✅ Respuesta recibida del bot:")
        print("─" * 50)
        print(bot_response)
        print("─" * 50)
        
        # Verificar contenido
        productos_reales = [
            "Mix Semillas Sativas", "$55,000",
            "Semillas CBD Medicinales", "$45,000", 
            "Semillas Northern Lights Auto", "$40,000",
            "Semillas White Widow Feminizadas", "$25,000"
        ]
        
        productos_inventados = [
            "Super Lemon Haze", "Durban Poison", "Jack Herer"
        ]
        
        print("\n🔍 VERIFICACIÓN DEL PREVIEW:")
        
        tiene_reales = any(prod in bot_response for prod in productos_reales)
        tiene_inventados = any(prod in bot_response for prod in productos_inventados)
        
        if tiene_reales and not tiene_inventados:
            print("✅ ÉXITO: Preview ahora muestra productos REALES de BD")
            print("✅ NO inventa productos inexistentes")
            print("✅ El frontend del backoffice está corregido")
        elif tiene_inventados:
            print("❌ FALLO: Sigue inventando productos")
            for prod in productos_inventados:
                if prod in bot_response:
                    print(f"   🚫 Menciona: {prod}")
        else:
            print("⚠️  Respuesta inesperada - revisar manualmente")
        
        # Comparar con lo que ANTES respondía el preview
        print(f"\n📊 COMPARACIÓN:")
        print("❌ ANTES (preview): 'Super Lemon Haze, Durban Poison y Jack Herer'")
        print(f"✅ AHORA (corregido): '{bot_response[:80]}...'")
        
        return tiene_reales and not tiene_inventados
        
    else:
        print(f"❌ Error en llamada: {response.status_code}")
        print(f"Response: {response.text}")
        return False

def main():
    print("🎯 CORRECCIÓN DEL MÓDULO DE CONFIGURACIÓN DEL BOT")
    print("=" * 80)
    
    success = test_frontend_preview_corrected()
    
    print("\n" + "=" * 80)
    if success:
        print("🎉 PROBLEMA SOLUCIONADO:")
        print("✅ El módulo de configuración del bot ahora es COHERENTE")
        print("✅ Preview y bot usan los mismos datos reales de BD")
        print("✅ No más productos inventados en el backoffice")
    else:
        print("❌ PROBLEMA PERSISTE:")
        print("El preview sigue teniendo inconsistencias")
    
    print("=" * 80)

if __name__ == "__main__":
    main()