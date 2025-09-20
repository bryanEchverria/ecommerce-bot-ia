#!/usr/bin/env python3
"""
Test de pedido completo end-to-end
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

def test_pedido_completo():
    print('=== TEST PEDIDO COMPLETO END-TO-END ===')

    db = SessionLocal()
    try:
        print('\n🛒 Iniciando proceso de compra completo...')
        
        # 1. Consulta específica de producto
        print('\n1️⃣ Consulta producto específico')
        respuesta = procesar_mensaje_flow(db, '+56950915617', 'quiero northern lights')
        print(f'   📝 Respuesta: {respuesta[:100]}...')
        tiene_precio = '$' in respuesta
        print(f'   ✅ Muestra precio: {tiene_precio}')
        
        # 2. Confirmar compra 
        print('\n2️⃣ Confirmar compra')
        respuesta = procesar_mensaje_flow(db, '+56950915617', 'sí')
        print(f'   📝 Respuesta: {respuesta[:100]}...')
        
        # 3. Especificar cantidad
        print('\n3️⃣ Especificar cantidad')
        respuesta = procesar_mensaje_flow(db, '+56950915617', '1')
        crea_pedido = 'Pedido confirmado' in respuesta or 'flow.cl' in respuesta
        print(f'   ✅ Crea pedido: {crea_pedido}')
        if crea_pedido:
            print(f'   📝 Contiene link de pago: {"flow.cl" in respuesta}')
        
        # 4. Verificar pedido en BD
        print('\n4️⃣ Verificación en Base de Datos')
        result = db.execute(text("SELECT id, estado, total, tenant_id FROM flow_pedidos WHERE telefono = '+56950915617' ORDER BY created_at DESC LIMIT 1;"))
        pedido = result.fetchone()
        
        if pedido:
            print(f'   ✅ Pedido creado: ID={pedido.id}')
            print(f'   💰 Total: ${pedido.total}')
            print(f'   📊 Estado: {pedido.estado}')
            print(f'   🏢 Tenant: {pedido.tenant_id}')
            print(f'   ✅ Multi-tenant correcto: {pedido.tenant_id == "acme-cannabis-2024"}')
            
            # Verificar productos del pedido
            result = db.execute(text("SELECT producto_id, cantidad, precio_unitario FROM flow_producto_pedidos WHERE pedido_id = :pedido_id;"), {'pedido_id': pedido.id})
            productos_pedido = result.fetchall()
            
            print(f'   📦 Productos en pedido: {len(productos_pedido)}')
            for prod in productos_pedido:
                print(f'      - Producto: {prod.producto_id}, Cantidad: {prod.cantidad}, Precio: ${prod.precio_unitario}')
        else:
            print('   ⚠️ No se encontró pedido creado')
            
    finally:
        db.close()

if __name__ == "__main__":
    test_pedido_completo()