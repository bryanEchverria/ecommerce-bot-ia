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
                "price": 89990,
                "stock": 25
            },
            {
                "name": "Pelota Kong Resistente",
                "description": "Juguete resistente e indestructible para perros de todas las razas",
                "price": 12990,
                "stock": 40
            },
            {
                "name": "Collar Antipulgas Seresto",
                "description": "Collar antipulgas y garrapatas de larga duracion (8 meses)",
                "price": 45990,
                "stock": 18
            },
            {
                "name": "Shampoo Hipoalergenico",
                "description": "Shampoo suave para pieles sensibles, libre de quimicos agresivos",
                "price": 8990,
                "stock": 30
            },
            {
                "name": "Cama Ortopedica Memory Foam",
                "description": "Cama ergonomica con memory foam para perros de edad avanzada",
                "price": 65990,
                "stock": 12
            },
            {
                "name": "Snacks Dentales Pedigree",
                "description": "Snacks que ayudan a la higiene dental y reducen el sarro",
                "price": 5990,
                "stock": 50
            },
            {
                "name": "Correa Retractil Flexi",
                "description": "Correa extensible de 5 metros para paseos comodos y seguros",
                "price": 28990,
                "stock": 22
            }
        ]
        
        for producto in productos_caninos:
            response = requests.post('http://localhost:8002/api/products', json=producto, headers=headers)
            if response.status_code in [200, 201]:
                print(f"   Producto creado: {producto['name']} - ${producto['price']:,}")
            else:
                print(f"   Error creando {producto['name']}: {response.status_code}")
    
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
                "price": 25990,
                "stock": 15
            },
            {
                "name": "Shatter Golden Goat 1g",
                "description": "Concentrado de alta pureza con 85% THC, sabor citrico intenso",
                "price": 35990,
                "stock": 8
            },
            {
                "name": "Brownies THC 100mg",
                "description": "Brownies artesanales con 100mg THC, efecto duradero",
                "price": 15990,
                "stock": 20
            },
            {
                "name": "Vaporizador Pax 3",
                "description": "Vaporizador portatil premium con control de temperatura preciso",
                "price": 189990,
                "stock": 6
            },
            {
                "name": "Aceite CBD 30ml (1000mg)",
                "description": "Aceite de CBD de espectro completo para bienestar diario",
                "price": 45990,
                "stock": 12
            },
            {
                "name": "Semillas Blue Dream x5",
                "description": "Pack de 5 semillas feminizadas Blue Dream, genetica estable",
                "price": 89990,
                "stock": 10
            },
            {
                "name": "Gummies CBD 300mg",
                "description": "Gomitas con CBD sin THC, ideales para ansiedad y estres",
                "price": 19990,
                "stock": 25
            },
            {
                "name": "Grinder Metalico 4 Piezas",
                "description": "Picador profesional de aluminio con compartimento para kief",
                "price": 12990,
                "stock": 18
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