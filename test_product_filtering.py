#!/usr/bin/env python3
"""
Test product filtering to ensure PlayStation doesn't appear when searching for phones
"""
import sys
import os

# Add the whatsapp-bot-fastapi directory to Python path
bot_path = os.path.join(os.path.dirname(__file__), 'whatsapp-bot-fastapi')
sys.path.insert(0, bot_path)

# Now import from services
from services.chat_service import procesar_mensaje, get_db_session

def test_product_filtering():
    """Test intelligent product filtering"""
    print("=== TESTING PRODUCT FILTERING ===\n")
    
    # Get database session
    try:
        db = get_db_session()
        print("[OK] Database connection successful")
    except Exception as e:
        print(f"[ERROR] Database connection failed: {e}")
        return
    
    # Test cases for different product searches
    test_cases = [
        ("Búsqueda teléfono", "quiero comprar un teléfono", "Debería mostrar solo iPhone"),
        ("Búsqueda celular", "necesito un celular", "Debería mostrar solo iPhone"),
        ("Búsqueda consola", "quiero una consola", "Debería mostrar solo PlayStation"),
        ("Búsqueda laptop", "necesito una laptop", "Debería mostrar solo MacBook"),
        ("Búsqueda iPhone específico", "quiero comprar un iPhone", "Debería mostrar solo iPhone"),
    ]
    
    telefono_base = "+1111111111"
    
    for i, (titulo, mensaje, esperado) in enumerate(test_cases):
        telefono = f"{telefono_base[:-1]}{i}"  # Different phone for each test
        
        print(f"** {titulo} **")
        print(f"Usuario: {mensaje}")
        print(f"Esperado: {esperado}")
        
        try:
            respuesta = procesar_mensaje(db, telefono, mensaje)
            print(f"Bot: {respuesta}")
            
            # Quick analysis
            if "teléfono" in mensaje.lower() or "celular" in mensaje.lower():
                if "PlayStation" in respuesta:
                    print("❌ ERROR: PlayStation aparece en búsqueda de teléfono")
                elif "iPhone" in respuesta:
                    print("✅ CORRECTO: Solo muestra teléfonos")
                else:
                    print("⚠️  REVISAR: No se encontró iPhone")
            
        except Exception as e:
            print(f"[ERROR] {e}")
        
        print("-" * 70)
    
    # Close database
    if db:
        db.close()
    
    print("\n=== TEST COMPLETED ===")

if __name__ == "__main__":
    test_product_filtering()