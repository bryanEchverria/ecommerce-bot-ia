#!/usr/bin/env python3
"""
Test del flujo completo Bot → Backoffice
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

def test_flujo_completo():
    print('=== FLUJO COMPLETO BOT → BACKOFFICE (ACME) ===')

    db = SessionLocal()
    try:
        # Limpiar sesiones previas
        print('🧹 Limpiando sesiones previas...')
        db.execute(text("DELETE FROM flow_sesiones WHERE telefono = '+56950915617';"))
        db.execute(text("DELETE FROM flow_pedidos WHERE telefono = '+56950915617' AND estado IN ('pendiente_pago', 'cancelado');"))
        db.commit()
        
        # Test 1: Saludo inicial
        print('\n1️⃣ Test: Saludo inicial')
        respuesta = procesar_mensaje_flow(db, '+56950915617', 'hola')
        print(f'   Respuesta: {respuesta[:100]}...')
        
        # Test 2: Consulta de categoría (flores)
        print('\n2️⃣ Test: Consulta categoría - quiero flores')
        respuesta = procesar_mensaje_flow(db, '+56950915617', 'quiero flores')
        detecta_categoria = "🏪 **Flores en Green House:**" in respuesta
        print(f'   Detecta categoría: {detecta_categoria}')
        print(f'   Respuesta: {respuesta[:150]}...')
        
        # Test 3: Compra específica
        print('\n3️⃣ Test: Compra específica - quiero northern lights')
        respuesta = procesar_mensaje_flow(db, '+56950915617', 'quiero northern lights')
        crea_pedido = "Pedido confirmado" in respuesta or "¿Cuántas unidades" in respuesta
        print(f'   Crea pedido: {crea_pedido}')
        print(f'   Respuesta: {respuesta[:150]}...')
        
        # Test 4: Verificar en BD del backoffice
        print('\n4️⃣ Verificación en BD del backoffice:')
        
        # Verificar pedidos
        result = db.execute(text("SELECT id, telefono, tenant_id, estado, total FROM flow_pedidos WHERE telefono = '+56950915617' ORDER BY created_at DESC LIMIT 3;"))
        pedidos = result.fetchall()
        
        print(f'   📋 Pedidos encontrados: {len(pedidos)}')
        for pedido in pedidos:
            print(f'      - ID: {pedido.id}, Estado: {pedido.estado}, Total: ${pedido.total}, Tenant: {pedido.tenant_id}')
        
        # Verificar sesiones
        result = db.execute(text("SELECT telefono, tenant_id, estado FROM flow_sesiones WHERE telefono = '+56950915617';"))
        sesiones = result.fetchall()
        
        print(f'   📱 Sesiones activas: {len(sesiones)}')
        for sesion in sesiones:
            print(f'      - Teléfono: {sesion.telefono}, Estado: {sesion.estado}, Tenant: {sesion.tenant_id}')
            
    finally:
        db.close()

def test_integracion_backoffice():
    """Test de integración con API del backoffice"""
    print('\n=== INTEGRACIÓN CON API BACKOFFICE ===')
    
    import requests
    
    try:
        # Test 1: Health check del backoffice
        print('🏥 Test: Health check backoffice')
        response = requests.get('http://localhost:8002/health', timeout=5)
        print(f'   Status: {response.status_code}')
        if response.status_code == 200:
            print(f'   Response: {response.json()}')
        
        # Test 2: Consultar productos por tenant via API
        print('\n📦 Test: API productos ACME Cannabis')
        response = requests.get('http://localhost:8002/products?client_id=acme-cannabis-2024', timeout=5)
        print(f'   Status: {response.status_code}')
        if response.status_code == 200:
            productos = response.json()
            print(f'   Productos encontrados: {len(productos)}')
            if productos:
                print(f'   Primer producto: {productos[0].get("name", "N/A")}')
        
        # Test 3: Consultar órdenes Flow via API
        print('\n🛒 Test: API órdenes Flow ACME')
        response = requests.get('http://localhost:8002/flow/orders?tenant_id=acme-cannabis-2024', timeout=5)
        print(f'   Status: {response.status_code}')
        if response.status_code == 200:
            orders = response.json()
            print(f'   Órdenes encontradas: {orders.get("total", 0)}')
            
    except requests.exceptions.RequestException as e:
        print(f'   ❌ Error conectando al backoffice: {e}')

if __name__ == "__main__":
    test_flujo_completo()
    test_integracion_backoffice()