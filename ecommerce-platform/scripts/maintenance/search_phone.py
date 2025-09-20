#!/usr/bin/env python3

import sys
import os
sys.path.append('/app')

from database import get_db
from models import Order, TwilioAccount
from auth_models import TenantClient
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://ecommerce_user:ecommerce123@postgres:5432/ecommerce_multi_tenant')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

try:
    with SessionLocal() as db:
        # Search for orders with this phone number
        phone_searches = [
            '+56950915617',
            '950915617', 
            '56950915617',
            '+950915617'
        ]
        
        print('🔍 Buscando órdenes con número 950915617...')
        
        found_any = False
        for phone_variant in phone_searches:
            orders = db.query(Order).filter(
                Order.customer_phone.contains(phone_variant)
            ).order_by(Order.created_at.desc()).limit(5).all()
            
            if orders:
                found_any = True
                print(f'\n📱 Órdenes encontradas con {phone_variant}:')
                for order in orders:
                    print(f'   ID: {order.id}')
                    print(f'   Número: {order.order_number}')
                    print(f'   Cliente: {order.customer_name}')
                    print(f'   Teléfono: {order.customer_phone}')
                    print(f'   Total: ${order.total}')
                    print(f'   Estado: {order.status}')
                    print(f'   Fecha: {order.created_at}')
                    print(f'   Tenant: {order.client_id}')
                    print('   ---')
        
        if not found_any:
            print('❌ No se encontraron órdenes con el número 950915617')
            
        # Check recent orders from all tenants
        print('\n📋 Últimas 10 órdenes de todos los tenants:')
        recent_orders = db.query(Order).order_by(Order.created_at.desc()).limit(10).all()
        for order in recent_orders:
            tenant = db.query(TenantClient).filter(TenantClient.id == order.client_id).first()
            tenant_name = tenant.slug if tenant else 'Unknown'
            print(f'   {tenant_name}: {order.customer_phone} - {order.customer_name} - ${order.total}')

except Exception as e:
    print(f'❌ Error: {e}')