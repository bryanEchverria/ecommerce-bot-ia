#!/usr/bin/env python3
"""
Test directo de la detección GPT para depurar el sistema
"""
import sys
import os
sys.path.append('/root/ecommerce-platform/ecommerce-bot-ia/whatsapp-bot-fastapi')

from services.backoffice_integration import get_real_products_from_backoffice, get_tenant_info
from services.smart_flows import detectar_intencion_con_gpt, _extraer_categorias_dinamicamente_con_gpt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Configuración de base de datos
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://ecommerce_user:ecommerce123@localhost:5432/ecommerce_multi_tenant")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def test_direct_gpt_detection():
    """Prueba directa de detección GPT"""
    db = SessionLocal()
    
    try:
        # Obtener productos de ACME Cannabis
        tenant_id = "acme-cannabis-2024"
        productos = get_real_products_from_backoffice(db, tenant_id)
        tenant_info = get_tenant_info(tenant_id, db)
        
        print(f"🏪 Tenant: {tenant_info['name']}")
        print(f"📦 Total productos: {len(productos)}")
        
        # Test 1: Extraer categorías dinámicamente
        print("\n" + "="*60)
        print("🧠 TEST 1: EXTRACCIÓN DE CATEGORÍAS")
        print("="*60)
        
        categorias = _extraer_categorias_dinamicamente_con_gpt(productos)
        print(f"✅ Categorías detectadas: {categorias}")
        
        # Test 2: Consultas específicas
        test_queries = [
            "qué semillas tienes",
            "tienes flores",
            "quiero aceites",
            "mostrame accesorios",
            "hola"
        ]
        
        print("\n" + "="*60)
        print("🔍 TEST 2: DETECCIÓN DE INTENCIONES")
        print("="*60)
        
        for query in test_queries:
            print(f"\n📝 Query: '{query}'")
            deteccion = detectar_intencion_con_gpt(query, productos, tenant_info)
            print(f"   🎯 Intención: {deteccion.get('intencion')}")
            print(f"   🏷️ Categoría: {deteccion.get('categoria')}")
            print(f"   📦 Producto: {deteccion.get('producto_mencionado')}")
            print(f"   🔍 Términos: {deteccion.get('terminos_busqueda')}")
        
        # Test 3: Verificar productos por categoría
        print("\n" + "="*60)
        print("🔎 TEST 3: PRODUCTOS POR CATEGORÍA")
        print("="*60)
        
        for categoria in categorias:
            productos_categoria = []
            for prod in productos:
                if categoria.lower() in prod['name'].lower() or categoria.lower() in prod.get('description', '').lower():
                    productos_categoria.append(prod['name'])
            
            print(f"\n🏷️ {categoria.title()}: {len(productos_categoria)} productos")
            for prod_name in productos_categoria[:3]:  # Mostrar solo los primeros 3
                print(f"   • {prod_name}")
            if len(productos_categoria) > 3:
                print(f"   • ... y {len(productos_categoria)-3} más")
        
    finally:
        db.close()

if __name__ == "__main__":
    test_direct_gpt_detection()