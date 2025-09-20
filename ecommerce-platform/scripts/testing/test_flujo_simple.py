#!/usr/bin/env python3
"""
Test simplificado del flujo completo Bot → Backoffice
"""

import sys
import os
sys.path.append('/root/ecommerce-bot-ia/whatsapp-bot-fastapi')

from services.flow_chat_service import procesar_mensaje_flow
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://ecommerce_user:ecommerce123@postgres:5432/ecommerce_multi_tenant')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def test_flujo_acme():
    print('=== FLUJO COMPLETO BOT → BACKOFFICE (ACME) ===')

    db = SessionLocal()
    try:
        # Test 1: Saludo inicial
        print('\n1️⃣ Test: Saludo inicial')
        respuesta = procesar_mensaje_flow(db, '+56950915617', 'hola')
        success = len(respuesta) > 0 and "Green House" in respuesta
        print(f'   ✅ Respuesta recibida: {success}')
        print(f'   📝 Contiene "Green House": {"Green House" in respuesta}')
        print(f'   📄 Primer línea: {respuesta.split(chr(10))[0][:100]}...')
        
        # Test 2: Consulta de categoría inteligente
        print('\n2️⃣ Test: Detección inteligente de categorías')
        respuesta = procesar_mensaje_flow(db, '+56950915617', 'quiero flores')
        detecta_categoria = "🏪" in respuesta and "Flores" in respuesta
        print(f'   ✅ Detecta categoría flores: {detecta_categoria}')
        print(f'   📝 Respuesta contiene productos: {"Northern Lights" in respuesta or "OG Kush" in respuesta}')
        print(f'   📄 Tipo de respuesta: {"Categoría" if detecta_categoria else "Otro"}')
        
        # Test 3: Compra específica con GPT
        print('\n3️⃣ Test: Compra específica con inteligencia')
        respuesta = procesar_mensaje_flow(db, '+56950915617', 'quiero northern lights')
        es_compra = "¿Cuántas unidades" in respuesta or "Pedido confirmado" in respuesta or "confirmar" in respuesta.lower()
        print(f'   ✅ Inicia proceso de compra: {es_compra}')
        print(f'   📝 Menciona "Northern Lights": {"Northern Lights" in respuesta}')
        print(f'   📄 Tipo de respuesta: {"Compra" if es_compra else "Consulta"}')
        
        # Test 4: Verificar persistencia en BD
        print('\n4️⃣ Test: Verificación en Base de Datos')
        
        # Verificar sesiones
        result = db.execute(text("SELECT COUNT(*) as total FROM flow_sesiones WHERE telefono = '+56950915617';"))
        sesiones_count = result.scalar()
        print(f'   📱 Sesiones creadas: {sesiones_count}')
        
        # Verificar tenant_id en sesiones
        if sesiones_count > 0:
            result = db.execute(text("SELECT tenant_id FROM flow_sesiones WHERE telefono = '+56950915617' LIMIT 1;"))
            tenant_id = result.scalar()
            print(f'   🏢 Tenant ID asignado: {tenant_id}')
            print(f'   ✅ Multi-tenant funciona: {tenant_id == "acme-cannabis-2024"}')
        
        # Verificar pedidos si existen
        result = db.execute(text("SELECT COUNT(*) as total FROM flow_pedidos WHERE telefono = '+56950915617';"))
        pedidos_count = result.scalar()
        print(f'   🛒 Pedidos creados: {pedidos_count}')
        
        if pedidos_count > 0:
            result = db.execute(text("SELECT id, estado, total, tenant_id FROM flow_pedidos WHERE telefono = '+56950915617' ORDER BY created_at DESC LIMIT 1;"))
            pedido = result.fetchone()
            print(f'   📋 Último pedido: ID={pedido.id}, Estado={pedido.estado}, Total=${pedido.total}')
            print(f'   🏢 Pedido tenant: {pedido.tenant_id}')
            
    except Exception as e:
        print(f'   ❌ Error durante test: {e}')
        
    finally:
        db.close()

def test_backoffice_api():
    """Test de integración con API del backoffice"""
    print('\n=== INTEGRACIÓN API BACKOFFICE ===')
    
    try:
        import requests
        
        # Test 1: Health check
        print('\n🏥 Test: Health del backoffice')
        response = requests.get('http://localhost:8002/health', timeout=3)
        print(f'   Status: {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            print(f'   ✅ Backoffice activo: {data.get("status") == "healthy"}')
        
        # Test 2: Productos ACME
        print('\n📦 Test: Productos ACME via API')
        response = requests.get('http://localhost:8002/flow/orders?tenant_id=acme-cannabis-2024', timeout=3)
        print(f'   Status: {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            print(f'   ✅ API flow orders funciona: {isinstance(data, dict)}')
            print(f'   📊 Total órdenes: {data.get("total", "N/A")}')
            
    except ImportError:
        print('   ⚠️ Requests no disponible, saltando tests de API')
    except Exception as e:
        print(f'   ❌ Error API: {e}')

if __name__ == "__main__":
    test_flujo_acme()
    test_backoffice_api()