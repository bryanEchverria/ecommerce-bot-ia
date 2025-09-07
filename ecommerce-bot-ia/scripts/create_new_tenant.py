#!/usr/bin/env python3
"""
Script para crear un nuevo tenant con todos los datos necesarios.
Evita problemas futuros automatizando la creación completa.
"""

import uuid
import bcrypt
import psycopg2
from datetime import datetime
import sys
import re

def validate_slug(slug):
    """Valida que el slug sea seguro para usar como subdominio"""
    if not re.match(r'^[a-z0-9-]{2,20}$', slug):
        raise ValueError("El slug debe contener solo letras minúsculas, números y guiones (2-20 caracteres)")
    if slug.startswith('-') or slug.endswith('-'):
        raise ValueError("El slug no puede empezar o terminar con guión")
    return True

def generate_secure_password_hash(password):
    """Genera un hash bcrypt seguro para la contraseña"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def create_tenant(company_name, slug, admin_email, admin_password="admin123"):
    """Crea un tenant completo con datos de ejemplo"""
    
    # Validaciones
    validate_slug(slug)
    
    # Conexión a la base de datos
    conn = psycopg2.connect(
        host="localhost",
        port="5432", 
        database="ecommerce_multi_tenant",
        user="ecommerce_user",
        password="ecommerce123"
    )
    
    try:
        cur = conn.cursor()
        
        # 1. Crear tenant client
        tenant_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO tenant_clients (id, name, slug, created_at) 
            VALUES (%s, %s, %s, %s)
        """, (tenant_id, company_name, slug, datetime.now()))
        
        print(f"✅ Tenant creado: {company_name} (ID: {tenant_id})")
        
        # 2. Crear usuarios por defecto
        users = [
            (f"admin@{slug}.com" if "@" not in admin_email else admin_email, admin_password, "admin"),
            (f"sales@{slug}.com", "sales123", "user"),
            (f"support@{slug}.com", "support123", "user")
        ]
        
        for email, password, role in users:
            user_id = f"user-{slug}-{role}-001"
            password_hash = generate_secure_password_hash(password)
            
            cur.execute("""
                INSERT INTO tenant_users (id, client_id, email, password_hash, role, is_active, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (user_id, tenant_id, email, password_hash, role, True, datetime.now()))
            
            print(f"✅ Usuario creado: {email} / {password} (rol: {role})")
        
        # 3. Crear productos de ejemplo
        products = [
            (f"Producto Premium {company_name}", f"Producto estrella de {company_name}", 999.99, 899.99, 50),
            (f"Producto Estándar {company_name}", f"Producto básico de {company_name}", 299.99, None, 100),
            (f"Accesorio {company_name}", f"Complemento ideal para {company_name}", 49.99, 39.99, 200)
        ]
        
        for i, (name, desc, price, sale_price, stock) in enumerate(products, 1):
            product_id = f"prod-{slug}-{i:03d}"
            cur.execute("""
                INSERT INTO products (id, name, description, price, sale_price, stock, category, status, client_id, image_url, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (product_id, name, desc, price, sale_price, stock, "General", "active", tenant_id, "", datetime.now(), datetime.now()))
            
            print(f"✅ Producto creado: {name} (${price})")
        
        # 4. Crear descuentos de ejemplo
        discounts = [
            (f"Bienvenida {company_name}", "percentage", 15.0, "category"),
            (f"Oferta Especial {company_name}", "percentage", 25.0, "category"),
            (f"Descuento Premium", "fixed", 100.0, "product")
        ]
        
        for i, (name, dtype, value, target) in enumerate(discounts, 1):
            discount_id = f"disc-{slug}-{i:03d}"
            product_id = f"prod-{slug}-001" if target == "product" else None
            
            cur.execute("""
                INSERT INTO discounts (id, name, type, value, target, category, product_id, is_active, client_id, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (discount_id, name, dtype, value, target, "General" if target == "category" else None, product_id, True, tenant_id, datetime.now(), datetime.now()))
            
            print(f"✅ Descuento creado: {name} ({value}{'%' if dtype == 'percentage' else '$'})")
        
        conn.commit()
        
        # 5. Mostrar información del tenant creado
        print(f"\n🎉 TENANT CREADO EXITOSAMENTE")
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"Empresa: {company_name}")
        print(f"Slug: {slug}")
        print(f"ID: {tenant_id}")
        print(f"\n📱 URLs del tenant:")
        print(f"• Backoffice: https://{slug}.sintestesia.cl/")
        print(f"• API: https://{slug}.sintestesia.cl/api/")
        print(f"• Webhook Twilio: https://{slug}.sintestesia.cl/bot/twilio/webhook")
        print(f"• Webhook Meta: https://{slug}.sintestesia.cl/bot/meta/webhook")
        print(f"\n👥 Usuarios creados:")
        for email, password, role in users:
            print(f"• {email} / {password} (rol: {role})")
        print(f"\n📦 Se crearon 3 productos y 3 descuentos de ejemplo")
        
        return tenant_id
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error creando tenant: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python3 create_new_tenant.py <nombre_empresa> <slug> [email_admin]")
        print("Ejemplo: python3 create_new_tenant.py 'Delta Corp' delta admin@delta.com")
        sys.exit(1)
    
    company_name = sys.argv[1]
    slug = sys.argv[2] 
    admin_email = sys.argv[3] if len(sys.argv) > 3 else f"admin@{slug}.com"
    
    try:
        create_tenant(company_name, slug, admin_email)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)