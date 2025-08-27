"""
Script para crear dos cuentas especializadas con productos específicos:
1. Mundo Canino - Tienda de productos para mascotas
2. Green House - Tienda de productos canábicos
"""
import requests
import json

def crear_cuentas_especializadas():
    print("CREANDO CUENTAS ESPECIALIZADAS")
    print("=" * 50)
    
    # Configuración de las nuevas cuentas
    cuentas = [
        {
            "email": "admin@mundocanino.com",
            "password": "canino123",
            "client_name": "Mundo Canino",
            "telefono": "+5678901234",
            "descripcion": "Tienda especializada en productos para mascotas y perros"
        },
        {
            "email": "admin@greenhouse.com", 
            "password": "green123",
            "client_name": "Green House",
            "telefono": "+3456789012",
            "descripcion": "Tienda especializada en productos canábicos y wellness"
        }
    ]
    
    tokens = {}
    
    # Crear las cuentas
    for cuenta in cuentas:
        print(f"\nCreando cuenta: {cuenta['client_name']}")
        
        # Registrar usuario
        register_data = {
            "email": cuenta["email"],
            "password": cuenta["password"],
            "client_name": cuenta["client_name"]
        }
        
        response = requests.post('http://localhost:8002/auth/register', json=register_data)
        
        if response.status_code == 200:
            auth_data = response.json()
            token = auth_data["access_token"]
            tokens[cuenta["client_name"]] = {
                "token": token,
                "telefono": cuenta["telefono"],
                "client_id": auth_data["client"]["id"]
            }
            print(f"OK Cuenta creada: {cuenta['email']}")
            print(f"   Client ID: {auth_data['client']['id']}")
        else:
            print(f"ERROR creando cuenta: {response.status_code} - {response.text}")
            continue
    
    # Crear categorías y productos para Mundo Canino
    if "Mundo Canino" in tokens:
        print(f"\n🐕 CONFIGURANDO MUNDO CANINO")
        token = tokens["Mundo Canino"]["token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Categorías para tienda canina
        categorias_caninas = [
            {"name": "Alimento", "description": "Alimentos premium para perros y gatos"},
            {"name": "Juguetes", "description": "Juguetes resistentes y seguros para mascotas"},
            {"name": "Accesorios", "description": "Collares, correas y accesorios para paseo"},
            {"name": "Higiene", "description": "Productos de aseo y cuidado para mascotas"},
            {"name": "Camas", "description": "Camas cómodas y resistentes para descanso"}
        ]
        
        categoria_ids = {}
        for categoria in categorias_caninas:
            response = requests.post('http://localhost:8002/api/categories', json=categoria, headers=headers)
            if response.status_code in [200, 201]:
                cat_data = response.json()
                categoria_ids[categoria["name"]] = cat_data["id"]
                print(f"   📂 Categoría creada: {categoria['name']}")
        
        # Productos para Mundo Canino
        productos_caninos = [
            {
                "name": "Royal Canin Adulto 15kg",
                "description": "Alimento premium para perros adultos, nutrición completa y balanceada",
                "price": 89990,
                "stock": 25,
                "category_id": categoria_ids.get("Alimento")
            },
            {
                "name": "Pelota Kong Resistente",
                "description": "Juguete resistente e indestructible para perros de todas las razas",
                "price": 12990,
                "stock": 40,
                "category_id": categoria_ids.get("Juguetes")
            },
            {
                "name": "Collar Antipulgas Seresto",
                "description": "Collar antipulgas y garrapatas de larga duración (8 meses)",
                "price": 45990,
                "stock": 18,
                "category_id": categoria_ids.get("Accesorios")
            },
            {
                "name": "Shampoo Hipoalergénico",
                "description": "Shampoo suave para pieles sensibles, libre de químicos agresivos",
                "price": 8990,
                "stock": 30,
                "category_id": categoria_ids.get("Higiene")
            },
            {
                "name": "Cama Ortopédica Memory Foam",
                "description": "Cama ergonómica con memory foam para perros de edad avanzada",
                "price": 65990,
                "stock": 12,
                "category_id": categoria_ids.get("Camas")
            },
            {
                "name": "Snacks Dentales Pedigree",
                "description": "Snacks que ayudan a la higiene dental y reducen el sarro",
                "price": 5990,
                "stock": 50,
                "category_id": categoria_ids.get("Alimento")
            },
            {
                "name": "Correa Retráctil Flexi",
                "description": "Correa extensible de 5 metros para paseos cómodos y seguros",
                "price": 28990,
                "stock": 22,
                "category_id": categoria_ids.get("Accesorios")
            }
        ]
        
        for producto in productos_caninos:
            if producto["category_id"]:
                response = requests.post('http://localhost:8002/api/products', json=producto, headers=headers)
                if response.status_code in [200, 201]:
                    print(f"   🛍️ Producto creado: {producto['name']} - ${producto['price']:,}")
    
    # Crear categorías y productos para Green House
    if "Green House" in tokens:
        print(f"\n🌿 CONFIGURANDO GREEN HOUSE")
        token = tokens["Green House"]["token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Categorías para tienda canábica
        categorias_cannabis = [
            {"name": "Flores", "description": "Flores de cannabis premium de alta calidad"},
            {"name": "Concentrados", "description": "Extracciones y concentrados de cannabis"},
            {"name": "Comestibles", "description": "Productos comestibles con THC y CBD"},
            {"name": "Accesorios", "description": "Pipas, vaporizadores y accesorios para consumo"},
            {"name": "CBD", "description": "Productos con CBD para bienestar y relajación"},
            {"name": "Semillas", "description": "Semillas certificadas para cultivo personal"}
        ]
        
        categoria_ids = {}
        for categoria in categorias_cannabis:
            response = requests.post('http://localhost:8002/api/categories', json=categoria, headers=headers)
            if response.status_code in [200, 201]:
                cat_data = response.json()
                categoria_ids[categoria["name"]] = cat_data["id"]
                print(f"   📂 Categoría creada: {categoria['name']}")
        
        # Productos para Green House
        productos_cannabis = [
            {
                "name": "OG Kush Premium 3.5g",
                "description": "Flor híbrida de alta calidad con 22% THC, ideal para relajación",
                "price": 25990,
                "stock": 15,
                "category_id": categoria_ids.get("Flores")
            },
            {
                "name": "Shatter Golden Goat 1g",
                "description": "Concentrado de alta pureza con 85% THC, sabor cítrico intenso",
                "price": 35990,
                "stock": 8,
                "category_id": categoria_ids.get("Concentrados")
            },
            {
                "name": "Brownies THC 100mg",
                "description": "Brownies artesanales con 100mg THC, efecto duradero",
                "price": 15990,
                "stock": 20,
                "category_id": categoria_ids.get("Comestibles")
            },
            {
                "name": "Vaporizador Pax 3",
                "description": "Vaporizador portátil premium con control de temperatura preciso",
                "price": 189990,
                "stock": 6,
                "category_id": categoria_ids.get("Accesorios")
            },
            {
                "name": "Aceite CBD 30ml (1000mg)",
                "description": "Aceite de CBD de espectro completo para bienestar diario",
                "price": 45990,
                "stock": 12,
                "category_id": categoria_ids.get("CBD")
            },
            {
                "name": "Semillas Blue Dream x5",
                "description": "Pack de 5 semillas feminizadas Blue Dream, genética estable",
                "price": 89990,
                "stock": 10,
                "category_id": categoria_ids.get("Semillas")
            },
            {
                "name": "Gummies CBD 300mg",
                "description": "Gomitas con CBD sin THC, ideales para ansiedad y estrés",
                "price": 19990,
                "stock": 25,
                "category_id": categoria_ids.get("CBD")
            },
            {
                "name": "Grinder Metálico 4 Piezas",
                "description": "Picador profesional de aluminio con compartimento para kief",
                "price": 12990,
                "stock": 18,
                "category_id": categoria_ids.get("Accesorios")
            }
        ]
        
        for producto in productos_cannabis:
            if producto["category_id"]:
                response = requests.post('http://localhost:8002/api/products', json=producto, headers=headers)
                if response.status_code in [200, 201]:
                    print(f"   🌿 Producto creado: {producto['name']} - ${producto['price']:,}")
    
    # Actualizar configuración del bot
    print(f"\n🤖 ACTUALIZANDO CONFIGURACIÓN DEL BOT")
    
    config_update = f"""
# Agregar estas configuraciones al tenant_service.py:

TENANT_CONFIG.update({{
    # Mundo Canino - Tienda de productos para mascotas
    "+5678901234": {{
        "client_email": "admin@mundocanino.com",
        "client_password": "canino123",
        "client_name": "Mundo Canino",
        "business_description": "Tienda especializada en productos para mascotas y perros",
        "token": None,
        "token_expires": None
    }},
    # Green House - Tienda de productos canábicos  
    "+3456789012": {{
        "client_email": "admin@greenhouse.com",
        "client_password": "green123", 
        "client_name": "Green House",
        "business_description": "Tienda especializada en productos canábicos y wellness",
        "token": None,
        "token_expires": None
    }}
}})
"""
    
    with open("config_bot_update.txt", "w", encoding="utf-8") as f:
        f.write(config_update)
    
    print("✅ Configuración del bot guardada en 'config_bot_update.txt'")
    
    # Resumen final
    print(f"\n📋 RESUMEN DE CUENTAS CREADAS")
    print("=" * 50)
    print("🐕 MUNDO CANINO:")
    print("   📧 Email: admin@mundocanino.com")
    print("   🔐 Password: canino123")
    print("   📱 WhatsApp: +5678901234")
    print("   🛍️ Productos: 7 productos en 5 categorías")
    print("   💰 Rango precios: $5,990 - $89,990")
    
    print("\n🌿 GREEN HOUSE:")
    print("   📧 Email: admin@greenhouse.com") 
    print("   🔐 Password: green123")
    print("   📱 WhatsApp: +3456789012")
    print("   🛍️ Productos: 8 productos en 6 categorías")
    print("   💰 Rango precios: $12,990 - $189,990")
    
    print(f"\n🚀 SIGUIENTE PASO:")
    print("   Actualizar whatsapp-bot-fastapi/services/tenant_service.py")
    print("   con la configuración generada en config_bot_update.txt")

if __name__ == "__main__":
    crear_cuentas_especializadas()