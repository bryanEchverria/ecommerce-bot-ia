#!/usr/bin/env python3
"""
Script para probar la detección de categorías en contexto de compra
"""

import sys
import os
sys.path.append('/root/ecommerce-bot-ia/whatsapp-bot-fastapi')

from services.backoffice_integration import get_real_products_from_backoffice, get_tenant_from_phone, get_tenant_info
from services.smart_flows import ejecutar_consulta_categoria
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Configuración de base de datos
import os
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://ecommerce_user:ecommerce123@postgres:5432/ecommerce_multi_tenant")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def test_categoria_detection():
    """Prueba la detección de categorías para ambos clientes"""
    
    # Test cases
    test_cases = [
        {
            "phone": "+56950915617",  # ACME Cannabis
            "client": "ACME Cannabis", 
            "queries": [
                "quiero flores",
                "necesito aceites", 
                "quiero semillas",
                "dame accesorios"
            ]
        },
        {
            "phone": "+1234567890",   # Bravo Gaming
            "client": "Bravo Gaming",
            "queries": [
                "quiero GPU",
                "necesito CPU", 
                "dame consolas",
                "quiero periféricos"
            ]
        }
    ]
    
    db = SessionLocal()
    
    try:
        for case in test_cases:
            print(f"\n{'='*60}")
            print(f"🧪 TESTING {case['client']} ({case['phone']})")
            print(f"{'='*60}")
            
            # Obtener productos del cliente
            tenant_id = get_tenant_from_phone(case['phone'])
            tenant_info = get_tenant_info(tenant_id)
            productos = get_real_products_from_backoffice(db, tenant_id)
            
            print(f"📊 Tenant ID: {tenant_id}")
            print(f"🏪 Tienda: {tenant_info['name']}")
            print(f"📦 Productos encontrados: {len(productos)}")
            
            # Extraer categorías disponibles
            categorias_disponibles = set()
            for prod in productos:
                categoria = prod.get('category', '').lower()
                if categoria and categoria != '':
                    categorias_disponibles.add(categoria)
            
            print(f"🏷️ Categorías disponibles: {sorted(categorias_disponibles)}")
            
            # Probar cada consulta
            for query in case['queries']:
                print(f"\n🔍 Testing: '{query}'")
                
                # Simular detección de categoría (lógica del flow_chat_service.py)
                mensaje_lower = query.lower()
                purchase_intent_words = ["quiero", "necesito", "comprar", "llevar", "dame", "vendeme"]
                has_purchase_intent = any(word in mensaje_lower for word in purchase_intent_words)
                
                if has_purchase_intent:
                    # Extraer alias dinámicos
                    alias_categorias = {}
                    for prod in productos:
                        categoria = prod.get('category', '').lower()
                        if categoria and categoria != '':
                            if categoria not in alias_categorias:
                                alias_categorias[categoria] = set([categoria])
                            
                            # Extraer palabras del nombre para crear alias
                            nombre_lower = prod['name'].lower()
                            palabras_producto = nombre_lower.split()
                            for palabra in palabras_producto:
                                if len(palabra) > 3:  # Solo palabras significativas
                                    alias_categorias[categoria].add(palabra)
                    
                    # Buscar categoría detectada
                    mensaje_words = mensaje_lower.split()
                    categoria_detectada = None
                    
                    for categoria, aliases in alias_categorias.items():
                        if any(alias in mensaje_words for alias in aliases):
                            categoria_detectada = categoria
                            break
                    
                    if categoria_detectada:
                        print(f"✅ Categoría detectada: '{categoria_detectada}'")
                        print(f"🎯 Alias disponibles para '{categoria_detectada}': {list(alias_categorias[categoria_detectada])}")
                        
                        # Ejecutar consulta de categoría
                        respuesta = ejecutar_consulta_categoria(categoria_detectada, productos, tenant_info)
                        print(f"📝 Respuesta:")
                        print("-" * 40)
                        print(respuesta)
                        print("-" * 40)
                    else:
                        print(f"❌ No se detectó categoría específica")
                        print(f"🔧 Alias disponibles: {alias_categorias}")
                else:
                    print(f"❌ No se detectó intención de compra")
                
                print()
            
    finally:
        db.close()

if __name__ == "__main__":
    test_categoria_detection()