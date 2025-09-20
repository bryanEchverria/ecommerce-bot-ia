"""
Integración del bot de WhatsApp con la base de datos del backoffice
Multi-tenant compatible - consulta productos reales en tiempo real
"""
from sqlalchemy.orm import Session
from sqlalchemy import text
import os

# URL de la base de datos del backoffice (mismo que usa el backend)
# Por defecto usa PostgreSQL para mantener compatibilidad con el backoffice existente
BACKEND_DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://ecommerce_user:ecommerce123@localhost/ecommerce_multi_tenant")

def get_tenant_from_phone(phone: str, db: Session = None) -> str:
    """
    Obtiene el tenant_id basado en el número de teléfono de forma COMPLETAMENTE DINÁMICA
    Consulta la tabla phone_tenant_mapping en tiempo real
    Escalable para cualquier cantidad de tenants y teléfonos
    """
    if db:
        try:
            # Consulta dinámica a la tabla de mapeo
            query = text("""
                SELECT tenant_id 
                FROM phone_tenant_mapping 
                WHERE phone = :phone
            """)
            result = db.execute(query, {"phone": phone}).first()
            
            if result:
                return result.tenant_id
            
            # Si no está mapeado, obtener el primer tenant disponible
            query = text("""
                SELECT id 
                FROM tenant_clients 
                ORDER BY created_at ASC 
                LIMIT 1
            """)
            result = db.execute(query).first()
            
            if result:
                return result.id
                
        except Exception as e:
            print(f"Error consultando mapeo teléfono-tenant: {e}")
    
    # Fallback extremo (solo si no hay BD)
    return "default-tenant"

def get_real_products_from_backoffice(db: Session, tenant_id: str):
    """
    Consulta los productos reales del backoffice en tiempo real
    Filtra por tenant_id para multi-tenant
    """
    try:
        # Query directo a la tabla products del backoffice
        query = text("""
            SELECT id, name, description, price, stock, status, client_id, category
            FROM products 
            WHERE client_id = :tenant_id 
            AND status = 'Active' 
            AND stock > 0
            ORDER BY name ASC
        """)
        
        result = db.execute(query, {"tenant_id": tenant_id})
        products = []
        
        for row in result:
            products.append({
                "id": row.id,
                "name": row.name,
                "description": row.description or "Sin descripción",
                "price": float(row.price),
                "stock": int(row.stock),
                "status": row.status,
                "client_id": row.client_id,
                "category": row.category or "General"
            })
        
        return products
    except Exception as e:
        print(f"Error consultando productos del backoffice: {e}")
        return []

def update_product_stock(db: Session, product_id: str, quantity: int, tenant_id: str) -> bool:
    """
    Actualiza el stock de un producto en tiempo real en el backoffice
    Incluye validación de tenant para seguridad
    """
    try:
        # Verificar que el producto pertenece al tenant correcto
        query = text("""
            UPDATE products 
            SET stock = stock - :quantity, 
                updated_at = NOW()
            WHERE id = :product_id 
            AND client_id = :tenant_id 
            AND stock >= :quantity
        """)
        
        result = db.execute(query, {
            "quantity": quantity,
            "product_id": product_id,
            "tenant_id": tenant_id
        })
        
        db.commit()
        return result.rowcount > 0
        
    except Exception as e:
        print(f"Error actualizando stock: {e}")
        db.rollback()
        return False

def get_product_by_name_fuzzy(db: Session, product_name: str, tenant_id: str):
    """
    Busca un producto por nombre usando coincidencia fuzzy
    Para mejorar la detección cuando el cliente escribe parcialmente
    """
    try:
        # Buscar coincidencia exacta primero
        query = text("""
            SELECT id, name, description, price, stock
            FROM products 
            WHERE client_id = :tenant_id 
            AND status = 'Active' 
            AND stock > 0
            AND LOWER(name) LIKE LOWER(:exact_name)
            LIMIT 1
        """)
        
        result = db.execute(query, {
            "tenant_id": tenant_id,
            "exact_name": f"%{product_name}%"
        })
        
        row = result.first()
        if row:
            return {
                "id": row.id,
                "name": row.name, 
                "description": row.description or "Sin descripción",
                "price": float(row.price),
                "stock": int(row.stock)
            }
        
        # Si no hay coincidencia exacta, buscar por palabras clave
        words = product_name.lower().split()
        if words:
            word_conditions = " OR ".join([f"LOWER(name) LIKE LOWER('%{word}%')" for word in words])
            query = text(f"""
                SELECT id, name, description, price, stock
                FROM products 
                WHERE client_id = :tenant_id 
                AND status = 'Active' 
                AND stock > 0
                AND ({word_conditions})
                ORDER BY 
                    CASE WHEN LOWER(name) LIKE LOWER(:first_word) THEN 1 ELSE 2 END,
                    name
                LIMIT 1
            """)
            
            result = db.execute(query, {
                "tenant_id": tenant_id,
                "first_word": f"%{words[0]}%"
            })
            
            row = result.first()
            if row:
                return {
                    "id": row.id,
                    "name": row.name,
                    "description": row.description or "Sin descripción", 
                    "price": float(row.price),
                    "stock": int(row.stock)
                }
        
        return None
        
    except Exception as e:
        print(f"Error buscando producto: {e}")
        return None

def get_tenant_info(tenant_id: str, db: Session = None) -> dict:
    """
    Obtiene información del tenant de forma COMPLETAMENTE DINÁMICA
    Solo usa datos reales de la base de datos, sin hardcodear nada
    """
    if db:
        try:
            # Consultar información del tenant
            query = text("""
                SELECT name, slug, created_at
                FROM tenant_clients 
                WHERE id = :tenant_id
            """)
            result = db.execute(query, {"tenant_id": tenant_id}).first()
            
            if result:
                return {
                    "name": result.name,
                    "type": "dynamic",  # Siempre dinámico
                    "greeting": f"¡Hola! Bienvenido a {result.name}. Soy tu asistente de ventas inteligente. ¿En qué puedo ayudarte?",
                    "currency": "CLP",
                    "tenant_id": tenant_id,
                    "slug": result.slug
                }
        except Exception as e:
            print(f"Error consultando tenant info: {e}")
    
    # Fallback genérico si no se encuentra el tenant
    return {
        "name": "Nuestra Tienda",
        "type": "dynamic", 
        "greeting": "¡Hola! Bienvenido. Soy tu asistente de ventas inteligente. ¿En qué puedo ayudarte?",
        "currency": "CLP",
        "tenant_id": tenant_id
    }

def get_tenant_from_slug(db: Session, slug: str) -> dict:
    """
    Obtiene información del tenant usando el slug - SISTEMA COMPLETAMENTE DINÁMICO
    Para sistema multi-tenant escalable que soporta cualquier cantidad de tenants
    
    Ejemplos:
    - "acme" → busca tenant con slug="acme" o id que contenga "acme"
    - "bravo" → busca tenant con slug="bravo" o id que contenga "bravo" 
    - "nueva-tienda" → busca tenant con slug="nueva-tienda"
    - cualquier slug nuevo → busca automáticamente en base de datos
    """
    try:
        # 1. Buscar por slug directo (método preferido)
        query = text("""
            SELECT id, name, slug, created_at
            FROM tenant_clients 
            WHERE slug = :slug
        """)
        result = db.execute(query, {"slug": slug}).first()
        
        if result:
            return {
                "id": result.id,
                "slug": result.slug,
                "name": result.name,
                "type": "dynamic",
                "greeting": f"¡Hola! Bienvenido a {result.name}. ¿En qué puedo ayudarte?",
                "currency": "CLP"
            }
        
        # 2. Buscar por patrón en ID (compatibilidad con tenants existentes)
        query = text("""
            SELECT id, name, slug, created_at
            FROM tenant_clients 
            WHERE id LIKE :pattern
            ORDER BY created_at ASC
            LIMIT 1
        """)
        result = db.execute(query, {"pattern": f"{slug}-%"}).first()
        
        if result:
            return {
                "id": result.id,
                "slug": slug,  # Usar el slug proporcionado
                "name": result.name,
                "type": "dynamic", 
                "greeting": f"¡Hola! Bienvenido a {result.name}. ¿En qué puedo ayudarte?",
                "currency": "CLP"
            }
        
        # 3. Buscar por nombre similar (fuzzy matching)
        query = text("""
            SELECT id, name, slug, created_at
            FROM tenant_clients 
            WHERE LOWER(name) LIKE LOWER(:name_pattern)
            ORDER BY created_at ASC
            LIMIT 1
        """)
        result = db.execute(query, {"name_pattern": f"%{slug}%"}).first()
        
        if result:
            return {
                "id": result.id,
                "slug": slug,
                "name": result.name,
                "type": "dynamic",
                "greeting": f"¡Hola! Bienvenido a {result.name}. ¿En qué puedo ayudarte?",
                "currency": "CLP"
            }
        
        print(f"Tenant no encontrado para slug: {slug}")
        return None
        
    except Exception as e:
        print(f"Error obteniendo tenant desde slug {slug}: {e}")
        return None

def format_price(price: float, currency: str = "CLP") -> str:
    """Formatea el precio según la moneda del tenant"""
    if currency == "CLP":
        return f"${price:,.0f}"
    else:
        return f"${price:.2f}"