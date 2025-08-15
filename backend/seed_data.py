import requests
import json
from datetime import datetime, timedelta
import random

BASE_URL = "http://127.0.0.1:8000/api"

# Datos de ejemplo para productos
products_data = [
    {
        "name": "iPhone 15 Pro",
        "category": "Electronics",
        "price": 999.99,
        "sale_price": 899.99,
        "stock": 50,
        "image_url": "https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=300&h=300&fit=crop",
        "status": "Active"
    },
    {
        "name": "MacBook Pro M3",
        "category": "Electronics",
        "price": 1999.99,
        "stock": 25,
        "image_url": "https://images.unsplash.com/photo-1541807084-5c52b6b3adef?w=300&h=300&fit=crop",
        "status": "Active"
    },
    {
        "name": "Nike Air Max 90",
        "category": "Fashion",
        "price": 120.00,
        "stock": 75,
        "image_url": "https://images.unsplash.com/photo-1549298916-b41d501d3772?w=300&h=300&fit=crop",
        "status": "Active"
    },
    {
        "name": "Levi's 501 Jeans",
        "category": "Fashion",
        "price": 69.99,
        "sale_price": 49.99,
        "stock": 100,
        "image_url": "https://images.unsplash.com/photo-1541099649105-f69ad21f3246?w=300&h=300&fit=crop",
        "status": "Active"
    },
    {
        "name": "KitchenAid Mixer",
        "category": "Home",
        "price": 299.99,
        "stock": 30,
        "image_url": "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=300&h=300&fit=crop",
        "status": "Active"
    },
    {
        "name": "Dyson V11 Vacuum",
        "category": "Home",
        "price": 499.99,
        "stock": 15,
        "image_url": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=300&h=300&fit=crop",
        "status": "Active"
    },
    {
        "name": "PlayStation 5",
        "category": "Electronics",
        "price": 499.99,
        "stock": 5,
        "image_url": "https://images.unsplash.com/photo-1607853202273-797f1c22a38e?w=300&h=300&fit=crop",
        "status": "Active"
    },
    {
        "name": "Adidas Ultraboost",
        "category": "Fashion",
        "price": 180.00,
        "stock": 0,
        "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=300&h=300&fit=crop",
        "status": "Out of Stock"
    }
]

# Datos de ejemplo para clientes
clients_data = [
    {
        "name": "Ana García",
        "email": "ana.garcia@email.com",
        "phone": "+1-555-0101",
        "join_date": (datetime.now() - timedelta(days=30)).isoformat(),
        "total_spent": 1250.50,
        "avatar_url": "https://images.unsplash.com/photo-1494790108755-2616b612b47c?w=100&h=100&fit=crop&crop=face"
    },
    {
        "name": "Carlos López",
        "email": "carlos.lopez@email.com",
        "phone": "+1-555-0102",
        "join_date": (datetime.now() - timedelta(days=45)).isoformat(),
        "total_spent": 890.25,
        "avatar_url": "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=100&h=100&fit=crop&crop=face"
    },
    {
        "name": "María Rodríguez",
        "email": "maria.rodriguez@email.com",
        "phone": "+1-555-0103",
        "join_date": (datetime.now() - timedelta(days=60)).isoformat(),
        "total_spent": 2340.75,
        "avatar_url": "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=100&h=100&fit=crop&crop=face"
    },
    {
        "name": "José Martínez",
        "email": "jose.martinez@email.com",
        "phone": "+1-555-0104",
        "join_date": (datetime.now() - timedelta(days=15)).isoformat(),
        "total_spent": 456.80,
        "avatar_url": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=100&h=100&fit=crop&crop=face"
    },
    {
        "name": "Laura Sánchez",
        "email": "laura.sanchez@email.com",
        "phone": "+1-555-0105",
        "join_date": (datetime.now() - timedelta(days=90)).isoformat(),
        "total_spent": 1875.30,
        "avatar_url": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100&h=100&fit=crop&crop=face"
    }
]

def create_products():
    print("Creando productos...")
    for product in products_data:
        try:
            response = requests.post(f"{BASE_URL}/products", json=product)
            if response.status_code == 200:
                print(f"✓ Producto creado: {product['name']}")
            else:
                print(f"✗ Error creando producto {product['name']}: {response.text}")
        except Exception as e:
            print(f"✗ Error: {e}")

def create_clients():
    print("\nCreando clientes...")
    client_ids = []
    for client in clients_data:
        try:
            response = requests.post(f"{BASE_URL}/clients", json=client)
            if response.status_code == 200:
                client_data = response.json()
                client_ids.append(client_data['id'])
                print(f"✓ Cliente creado: {client['name']}")
            else:
                print(f"✗ Error creando cliente {client['name']}: {response.text}")
        except Exception as e:
            print(f"✗ Error: {e}")
    return client_ids

def create_orders(client_ids):
    print("\nCreando pedidos...")
    order_statuses = ["Pending", "Shipped", "Delivered", "Cancelled"]
    
    # Obtener productos para las órdenes
    try:
        products_response = requests.get(f"{BASE_URL}/products")
        products = products_response.json() if products_response.status_code == 200 else []
    except:
        products = []
    
    for i in range(20):  # Crear 20 órdenes
        days_ago = random.randint(1, 90)
        order_date = datetime.now() - timedelta(days=days_ago)
        
        order_data = {
            "customer_name": random.choice(clients_data)["name"],
            "client_id": random.choice(client_ids) if client_ids else None,
            "date": order_date.isoformat(),
            "total": round(random.uniform(50, 2000), 2),
            "status": random.choice(order_statuses),
            "items": random.randint(1, 5)
        }
        
        try:
            response = requests.post(f"{BASE_URL}/orders", json=order_data)
            if response.status_code == 200:
                print(f"✓ Pedido creado: {order_data['customer_name']} - ${order_data['total']}")
            else:
                print(f"✗ Error creando pedido: {response.text}")
        except Exception as e:
            print(f"✗ Error: {e}")

def create_campaigns():
    print("\nCreando campañas...")
    
    # Obtener productos para las campañas
    try:
        products_response = requests.get(f"{BASE_URL}/products")
        products = products_response.json() if products_response.status_code == 200 else []
        product_ids = [p['id'] for p in products[:3]]  # Tomar los primeros 3 productos
    except:
        product_ids = []
    
    campaigns_data = [
        {
            "name": "Black Friday 2024",
            "start_date": (datetime.now() - timedelta(days=10)).isoformat(),
            "end_date": (datetime.now() + timedelta(days=20)).isoformat(),
            "status": "Active",
            "budget": 5000.00,
            "clicks": 1250,
            "conversions": 85,
            "image_url": "https://images.unsplash.com/photo-1607083206968-13611e3d76db?w=300&h=200&fit=crop",
            "product_ids": product_ids[:2] if product_ids else []
        },
        {
            "name": "Summer Sale",
            "start_date": (datetime.now() - timedelta(days=30)).isoformat(),
            "end_date": (datetime.now() - timedelta(days=5)).isoformat(),
            "status": "Completed",
            "budget": 3000.00,
            "clicks": 890,
            "conversions": 45,
            "image_url": "https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=300&h=200&fit=crop",
            "product_ids": product_ids[1:3] if len(product_ids) > 1 else []
        },
        {
            "name": "New Year Campaign",
            "start_date": (datetime.now() + timedelta(days=30)).isoformat(),
            "end_date": (datetime.now() + timedelta(days=60)).isoformat(),
            "status": "Paused",
            "budget": 2500.00,
            "clicks": 0,
            "conversions": 0,
            "image_url": "https://images.unsplash.com/photo-1467810563316-b5476525c0f9?w=300&h=200&fit=crop",
            "product_ids": product_ids if product_ids else []
        }
    ]
    
    for campaign in campaigns_data:
        try:
            response = requests.post(f"{BASE_URL}/campaigns", json=campaign)
            if response.status_code == 200:
                print(f"✓ Campaña creada: {campaign['name']}")
            else:
                print(f"✗ Error creando campaña {campaign['name']}: {response.text}")
        except Exception as e:
            print(f"✗ Error: {e}")

def create_discounts():
    print("\nCreando descuentos...")
    
    discounts_data = [
        {
            "name": "Electronics 15% Off",
            "type": "Percentage",
            "value": 15.0,
            "target": "Category",
            "category": "Electronics",
            "is_active": True
        },
        {
            "name": "First Time Buyer",
            "type": "Fixed Amount",
            "value": 50.0,
            "target": "All",
            "is_active": True
        },
        {
            "name": "Fashion Week Special",
            "type": "Percentage",
            "value": 25.0,
            "target": "Category",
            "category": "Fashion",
            "is_active": False
        },
        {
            "name": "VIP Customer Discount",
            "type": "Percentage",
            "value": 10.0,
            "target": "All",
            "is_active": True
        }
    ]
    
    for discount in discounts_data:
        try:
            response = requests.post(f"{BASE_URL}/discounts", json=discount)
            if response.status_code == 200:
                print(f"✓ Descuento creado: {discount['name']}")
            else:
                print(f"✗ Error creando descuento {discount['name']}: {response.text}")
        except Exception as e:
            print(f"✗ Error: {e}")

def main():
    print("🚀 Iniciando carga de datos de ejemplo...")
    print("=" * 50)
    
    # Crear datos en orden
    create_products()
    client_ids = create_clients()
    create_orders(client_ids)
    create_campaigns()
    create_discounts()
    
    print("\n" + "=" * 50)
    print("✅ ¡Datos de ejemplo cargados exitosamente!")
    print("\n📊 Ve a http://localhost:3000 para ver la aplicación con datos")
    print("📚 Documentación de API: http://127.0.0.1:8000/docs")

if __name__ == "__main__":
    main()