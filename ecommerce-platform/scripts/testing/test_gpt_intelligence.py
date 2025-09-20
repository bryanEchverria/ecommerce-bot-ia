#!/usr/bin/env python3
"""
Script para probar la inteligencia de GPT en el bot de WhatsApp
Verifica detección de categorías, productos y respuestas inteligentes
"""

import sys
import os
sys.path.append('/root/ecommerce-bot-ia/whatsapp-bot-fastapi')

from services.backoffice_integration import get_real_products_from_backoffice, get_tenant_from_phone, get_tenant_info
from services.smart_flows import detectar_intencion_con_gpt, ejecutar_flujo_inteligente
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Configuración de base de datos
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://ecommerce_user:ecommerce123@postgres:5432/ecommerce_multi_tenant")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def test_gpt_intelligence():
    """Prueba la inteligencia de GPT con diferentes tipos de consultas"""
    
    # Test cases más complejos y variados
    test_cases = [
        {
            "phone": "+56950915617",  # ACME Cannabis
            "client": "ACME Cannabis", 
            "queries": [
                # Categorías directas
                "quiero flores",
                "necesito aceites",
                "dame semillas",
                "quiero accesorios",
                
                # Categorías con variaciones
                "quiero semillitas",
                "necesito floritas",
                "dame aceititos",
                
                # Productos específicos
                "quiero northern lights",
                "necesito og kush",
                "dame un vaporizador",
                "quiero brownies",
                
                # Consultas conversacionales
                "hola, qué tienes disponible?",
                "me puedes mostrar el catálogo?",
                "qué productos manejan?",
                
                # Consultas de compra específicas
                "quiero comprar flores premium",
                "necesito comprar un grinder",
                "dame 2 brownies para llevar",
                
                # Consultas ambiguas
                "qué recomiendas para relajarse?",
                "algo para el dolor?",
                "tienes algo fuerte?"
            ]
        },
        {
            "phone": "+1234567890",   # Bravo Gaming
            "client": "Bravo Gaming",
            "queries": [
                # Categorías gaming
                "quiero GPU",
                "necesito CPU",
                "dame consolas",
                "quiero periféricos",
                
                # Variaciones gaming
                "quiero una tarjeta gráfica",
                "necesito un procesador",
                "dame una consola",
                "quiero un mouse gamer",
                
                # Consultas específicas
                "quiero comprar un compu",
                "necesito una RTX",
                "dame una PlayStation",
                "quiero un teclado mecánico",
                
                # Consultas gaming conversacionales
                "qué tienes para gaming?",
                "qué recomiendas para jugar en 4K?",
                "algo para streaming?",
                
                # Consultas técnicas
                "quiero armar una PC gamer",
                "necesito componentes para gaming",
                "qué GPU recomiendas?",
                
                # Consultas ambiguas gaming
                "algo potente para juegos",
                "lo mejor que tengas",
                "quiero lo más rápido"
            ]
        }
    ]
    
    db = SessionLocal()
    
    try:
        for case in test_cases:
            print(f"\n{'='*80}")
            print(f"🧪 TESTING GPT INTELLIGENCE - {case['client']} ({case['phone']})")
            print(f"{'='*80}")
            
            # Obtener productos del cliente
            tenant_id = get_tenant_from_phone(case['phone'])
            tenant_info = get_tenant_info(tenant_id)
            productos = get_real_products_from_backoffice(db, tenant_id)
            
            print(f"📊 Tenant ID: {tenant_id}")
            print(f"🏪 Tienda: {tenant_info['name']}")
            print(f"📦 Productos encontrados: {len(productos)}")
            
            # Mostrar categorías disponibles
            categorias_disponibles = set()
            for prod in productos:
                categoria = prod.get('category', '').lower()
                if categoria and categoria != '':
                    categorias_disponibles.add(categoria)
            
            print(f"🏷️ Categorías disponibles: {sorted(categorias_disponibles)}")
            
            # Probar cada consulta con GPT
            for i, query in enumerate(case['queries'], 1):
                print(f"\n{'-'*60}")
                print(f"🔍 Test {i:2d}/{len(case['queries'])}: '{query}'")
                print(f"{'-'*60}")
                
                try:
                    # Usar GPT para detectar intención
                    deteccion = detectar_intencion_con_gpt(query, productos, tenant_info)
                    
                    print(f"🎯 GPT detectó:")
                    print(f"   📋 Intención: {deteccion.get('intencion', 'N/A')}")
                    print(f"   📦 Producto mencionado: {deteccion.get('producto_mencionado', 'N/A')}")
                    print(f"   💡 Producto sugerido: {deteccion.get('producto_sugerido', 'N/A')}")
                    print(f"   🏷️ Categoría: {deteccion.get('categoria', 'N/A')}")
                    print(f"   🔢 Cantidad: {deteccion.get('cantidad_mencionada', 'N/A')}")
                    print(f"   🔎 Términos búsqueda: {deteccion.get('terminos_busqueda', [])}")
                    
                    # Ejecutar flujo inteligente
                    respuesta = ejecutar_flujo_inteligente(deteccion, productos, tenant_info)
                    
                    print(f"\n💬 Respuesta del sistema:")
                    print(f"{'─'*50}")
                    # Mostrar solo las primeras 3 líneas para mantener output manejable
                    lineas_respuesta = respuesta.split('\n')[:3]
                    for linea in lineas_respuesta:
                        print(f"   {linea}")
                    if len(respuesta.split('\n')) > 3:
                        print(f"   ... (respuesta completa de {len(respuesta)} caracteres)")
                    print(f"{'─'*50}")
                    
                    # Analizar si la respuesta es inteligente
                    es_inteligente = analizar_inteligencia_respuesta(query, deteccion, respuesta, case['client'])
                    print(f"🧠 Análisis: {es_inteligente}")
                    
                except Exception as e:
                    print(f"❌ Error procesando query: {e}")
                
                print()
            
    finally:
        db.close()

def analizar_inteligencia_respuesta(query, deteccion, respuesta, cliente):
    """Analiza si la respuesta de GPT es inteligente y apropiada"""
    
    query_lower = query.lower()
    inteligencia_score = []
    
    # Verificar detección de intención apropiada
    if any(word in query_lower for word in ["quiero", "necesito", "dame", "comprar"]):
        if deteccion.get('intencion') in ['intencion_compra', 'consulta_producto', 'consulta_categoria']:
            inteligencia_score.append("✅ Intención de compra detectada correctamente")
        else:
            inteligencia_score.append("⚠️ Intención de compra no detectada")
    
    # Verificar detección de categorías específicas del cliente
    if cliente == "ACME Cannabis":
        categorias_cannabis = ["flores", "aceites", "semillas", "accesorios", "comestibles"]
        if any(cat in query_lower for cat in ["flores", "floritas", "semillas", "semillitas", "aceites", "aceititos"]):
            if deteccion.get('categoria') in categorias_cannabis:
                inteligencia_score.append("✅ Categoría cannabis detectada correctamente")
            else:
                inteligencia_score.append("⚠️ Categoría cannabis no detectada")
    
    elif cliente == "Bravo Gaming":
        categorias_gaming = ["gpu", "cpu", "consolas", "periféricos", "monitores", "ram", "storage"]
        if any(word in query_lower for word in ["gpu", "cpu", "consola", "compu", "gráfica", "procesador"]):
            if deteccion.get('categoria') in categorias_gaming:
                inteligencia_score.append("✅ Categoría gaming detectada correctamente")
            else:
                inteligencia_score.append("⚠️ Categoría gaming no detectada")
    
    # Verificar respuesta apropiada al contexto del cliente
    if cliente == "ACME Cannabis" and "Green House" in respuesta:
        inteligencia_score.append("✅ Branding correcto para cannabis")
    elif cliente == "Bravo Gaming" and "Bravo Gaming" in respuesta:
        inteligencia_score.append("✅ Branding correcto para gaming")
    
    # Verificar que la respuesta no sea genérica
    if len(respuesta) > 100 and ("$" in respuesta or "precio" in respuesta.lower()):
        inteligencia_score.append("✅ Respuesta detallada con precios")
    
    # Calcular score final
    if len(inteligencia_score) >= 2:
        return "🟢 INTELIGENTE - " + " | ".join(inteligencia_score)
    elif len(inteligencia_score) == 1:
        return "🟡 PARCIAL - " + " | ".join(inteligencia_score)
    else:
        return "🔴 BÁSICA - Respuesta genérica o incorrecta"

if __name__ == "__main__":
    test_gpt_intelligence()