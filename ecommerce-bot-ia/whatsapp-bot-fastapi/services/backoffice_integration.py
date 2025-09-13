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

# Mapeo de números de WhatsApp a tenant_id
PHONE_TO_TENANT_MAP = {
    "+3456789012": "acme-cannabis-2024",
    "+56950915617": "acme-cannabis-2024", 
    "+1234567890": "bravo-gaming-2024",
    "+5678901234": "mundo-canino-2024",  # Pendiente de crear
    "+9876543210": "test-store-2024"     # Pendiente de crear
}

def get_tenant_from_phone(phone: str) -> str:
    """Obtiene el tenant_id basado en el número de teléfono"""
    return PHONE_TO_TENANT_MAP.get(phone, "acme-cannabis-2024")  # Default

def get_real_products_from_backoffice(db: Session, tenant_id: str):
    """
    Consulta los productos reales del backoffice en tiempo real
    Filtra por tenant_id para multi-tenant
    """
    try:
        # Query directo a la tabla products del backoffice
        query = text("""
            SELECT id, name, description, price, stock, status, client_id
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
                "client_id": row.client_id
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

def get_tenant_info(tenant_id: str) -> dict:
    """Obtiene información del tenant para personalizar respuestas"""
    tenant_config = {
        "acme-cannabis-2024": {
            "name": "Green House",
            "type": "cannabis", 
            "greeting": "🌿 ¡Hola! Bienvenido a Green House\nEspecialistas en productos canábicos premium.",
            "currency": "CLP"
        },
        "bravo-gaming-2024": {
            "name": "Bravo Gaming",
            "type": "gaming",
            "greeting": "🎮 ¡Hola! Bienvenido a Bravo Gaming\nTu tienda de gaming y tecnología.",
            "currency": "CLP"
        }
    }
    
    return tenant_config.get(tenant_id, {
        "name": "Tienda",
        "type": "general", 
        "greeting": "¡Hola! Bienvenido a nuestra tienda.",
        "currency": "CLP"
    })

def format_price(price: float, currency: str = "CLP") -> str:
    """Formatea el precio según la moneda del tenant"""
    if currency == "CLP":
        return f"${price:,.0f}"
    else:
        return f"${price:.2f}"