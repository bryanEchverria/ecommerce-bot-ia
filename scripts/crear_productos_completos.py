import requests

def crear_productos_especializados():
    print("CREANDO PRODUCTOS ESPECIALIZADOS")
    print("=" * 50)
    
    # Login Mundo Canino
    print("\nCONFIGURANDO MUNDO CANINO")
    login_response = requests.post('http://localhost:8002/auth/login', json={
        'email': 'admin@mundocanino.com',
        'password': 'canino123'
    })
    
    if login_response.status_code == 200:
        token = login_response.json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # Productos para Mundo Canino
        productos_caninos = [
            {
                "name": "Royal Canin Adulto 15kg",
                "description": "Alimento premium para perros adultos, nutricion completa y balanceada",
                "category": "Alimento",
                "price": 89990,
                "stock": 25,
                "image_url": "https://example.com/royal-canin.jpg",
                "status": "active"
            },
            {
                "name": "Pelota Kong Resistente",
                "description": "Juguete resistente e indestructible para perros de todas las razas",
                "category": "Juguetes",
                "price": 12990,
                "stock": 40,
                "image_url": "https://example.com/kong-ball.jpg",
                "status": "active"
            },
            {
                "name": "Collar Antipulgas Seresto",
                "description": "Collar antipulgas y garrapatas de larga duracion (8 meses)",
                "category": "Accesorios",
                "price": 45990,
                "stock": 18,
                "image_url": "https://example.com/seresto-collar.jpg",
                "status": "active"
            },
            {
                "name": "Shampoo Hipoalergenico",
                "description": "Shampoo suave para pieles sensibles, libre de quimicos agresivos",
                "category": "Higiene",
                "price": 8990,
                "stock": 30,
                "image_url": "https://example.com/shampoo.jpg",
                "status": "active"
            },
            {
                "name": "Cama Ortopedica Memory Foam",
                "description": "Cama ergonomica con memory foam para perros de edad avanzada",
                "category": "Camas",
                "price": 65990,
                "stock": 12,
                "image_url": "https://example.com/memory-foam-bed.jpg",
                "status": "active"
            },
            {
                "name": "Snacks Dentales Pedigree",
                "description": "Snacks que ayudan a la higiene dental y reducen el sarro",
                "category": "Alimento",
                "price": 5990,
                "stock": 50,
                "image_url": "https://example.com/dental-snacks.jpg",
                "status": "active"
            },
            {
                "name": "Correa Retractil Flexi",
                "description": "Correa extensible de 5 metros para paseos comodos y seguros",
                "category": "Accesorios",
                "price": 28990,
                "stock": 22,
                "image_url": "https://example.com/flexi-leash.jpg",
                "status": "active"
            }
        ]
        
        for producto in productos_caninos:
            response = requests.post('http://localhost:8002/api/products', json=producto, headers=headers)
            if response.status_code in [200, 201]:
                print(f"   Producto creado: {producto['name']} - ${producto['price']:,}")
            else:
                print(f"   Error creando {producto['name']}: {response.status_code}")
                print(f"   Error detail: {response.text}")
    
    # Login Green House
    print("\nCONFIGURANDO GREEN HOUSE")
    login_response = requests.post('http://localhost:8002/auth/login', json={
        'email': 'admin@greenhouse.com',
        'password': 'green123'
    })
    
    if login_response.status_code == 200:
        token = login_response.json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # Productos para Green House
        productos_cannabis = [
            {
                "name": "OG Kush Premium 3.5g",
                "description": "Flor hibrida de alta calidad con 22% THC, ideal para relajacion",
                "category": "Flores",
                "price": 25990,
                "stock": 15,
                "image_url": "https://example.com/og-kush.jpg",
                "status": "active"
            },
            {
                "name": "Shatter Golden Goat 1g",
                "description": "Concentrado de alta pureza con 85% THC, sabor citrico intenso",
                "category": "Concentrados",
                "price": 35990,
                "stock": 8,
                "image_url": "https://example.com/golden-goat-shatter.jpg",
                "status": "active"
            },
            {
                "name": "Brownies THC 100mg",
                "description": "Brownies artesanales con 100mg THC, efecto duradero",
                "category": "Comestibles",
                "price": 15990,
                "stock": 20,
                "image_url": "https://example.com/thc-brownies.jpg",
                "status": "active"
            },
            {
                "name": "Vaporizador Pax 3",
                "description": "Vaporizador portatil premium con control de temperatura preciso",
                "category": "Accesorios",
                "price": 189990,
                "stock": 6,
                "image_url": "https://example.com/pax-3.jpg",
                "status": "active"
            },
            {
                "name": "Aceite CBD 30ml (1000mg)",
                "description": "Aceite de CBD de espectro completo para bienestar diario",
                "category": "CBD",
                "price": 45990,
                "stock": 12,
                "image_url": "https://example.com/cbd-oil.jpg",
                "status": "active"
            },
            {
                "name": "Semillas Blue Dream x5",
                "description": "Pack de 5 semillas feminizadas Blue Dream, genetica estable",
                "category": "Semillas",
                "price": 89990,
                "stock": 10,
                "image_url": "https://example.com/blue-dream-seeds.jpg",
                "status": "active"
            },
            {
                "name": "Gummies CBD 300mg",
                "description": "Gomitas con CBD sin THC, ideales para ansiedad y estres",
                "category": "CBD",
                "price": 19990,
                "stock": 25,
                "image_url": "https://example.com/cbd-gummies.jpg",
                "status": "active"
            },
            {
                "name": "Grinder Metalico 4 Piezas",
                "description": "Picador profesional de aluminio con compartimento para kief",
                "category": "Accesorios",
                "price": 12990,
                "stock": 18,
                "image_url": "https://example.com/metal-grinder.jpg",
                "status": "active"
            }
        ]
        
        for producto in productos_cannabis:
            response = requests.post('http://localhost:8002/api/products', json=producto, headers=headers)
            if response.status_code in [200, 201]:
                print(f"   Producto creado: {producto['name']} - ${producto['price']:,}")
            else:
                print(f"   Error creando {producto['name']}: {response.status_code}")
                print(f"   Error detail: {response.text}")
    
    print(f"\nPRODUCTOS CREADOS EXITOSAMENTE")

if __name__ == "__main__":
    crear_productos_especializados()