import requests

def agregar_productos_originales():
    print("AGREGANDO PRODUCTOS A CUENTAS ORIGINALES")
    print("=" * 50)
    
    # Demo Company - Productos de tecnologia y electronica
    print("\nAGREGANDO PRODUCTOS A DEMO COMPANY")
    login_response = requests.post('http://localhost:8002/auth/login', json={
        'email': 'admin@demo.com',
        'password': 'demo123'
    })
    
    if login_response.status_code == 200:
        token = login_response.json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        
        productos_demo = [
            {
                "name": "iPhone 15 Pro Max 256GB",
                "description": "Ultimo iPhone con chip A17 Pro, camara titanium y pantalla Super Retina XDR",
                "category": "Smartphones",
                "price": 1299990,
                "stock": 15,
                "image_url": "https://example.com/iphone15.jpg",
                "status": "active"
            },
            {
                "name": "MacBook Air M3 13 pulgadas",
                "description": "Laptop ultra delgada con chip M3, 8GB RAM y 256GB SSD",
                "category": "Laptops",
                "price": 1199990,
                "stock": 8,
                "image_url": "https://example.com/macbook-air.jpg",
                "status": "active"
            },
            {
                "name": "Samsung TV QLED 55 4K",
                "description": "Smart TV QLED 55 pulgadas con tecnologia Quantum Dot y HDR10+",
                "category": "Televisores",
                "price": 899990,
                "stock": 12,
                "image_url": "https://example.com/samsung-tv.jpg",
                "status": "active"
            },
            {
                "name": "Sony PlayStation 5",
                "description": "Consola de videojuegos de nueva generacion con SSD ultrarapido",
                "category": "Gaming",
                "price": 599990,
                "stock": 6,
                "image_url": "https://example.com/ps5.jpg",
                "status": "active"
            },
            {
                "name": "iPad Pro 12.9 M2",
                "description": "Tablet profesional con chip M2, pantalla Liquid Retina XDR y soporte Apple Pencil",
                "category": "Tablets",
                "price": 1099990,
                "stock": 10,
                "image_url": "https://example.com/ipad-pro.jpg",
                "status": "active"
            },
            {
                "name": "AirPods Pro 2da Gen",
                "description": "Audifonos inalambricos con cancelacion activa de ruido y audio espacial",
                "category": "Audio",
                "price": 249990,
                "stock": 25,
                "image_url": "https://example.com/airpods-pro.jpg",
                "status": "active"
            },
            {
                "name": "Dell XPS 13 Plus",
                "description": "Ultrabook premium con Intel Core i7, 16GB RAM y pantalla OLED",
                "category": "Laptops",
                "price": 1599990,
                "stock": 5,
                "image_url": "https://example.com/dell-xps.jpg",
                "status": "active"
            },
            {
                "name": "Nintendo Switch OLED",
                "description": "Consola hibrida con pantalla OLED de 7 pulgadas y Joy-Con mejorados",
                "category": "Gaming",
                "price": 379990,
                "stock": 18,
                "image_url": "https://example.com/switch-oled.jpg",
                "status": "active"
            },
            {
                "name": "Samsung Galaxy S24 Ultra",
                "description": "Smartphone premium con S Pen, camara de 200MP y pantalla Dynamic AMOLED",
                "category": "Smartphones",
                "price": 1399990,
                "stock": 12,
                "image_url": "https://example.com/galaxy-s24.jpg",
                "status": "active"
            },
            {
                "name": "Monitor LG UltraWide 34",
                "description": "Monitor curvo ultrawide 34 pulgadas QHD con tecnologia IPS",
                "category": "Monitores",
                "price": 699990,
                "stock": 8,
                "image_url": "https://example.com/lg-monitor.jpg",
                "status": "active"
            }
        ]
        
        for producto in productos_demo:
            response = requests.post('http://localhost:8002/api/products', json=producto, headers=headers)
            if response.status_code in [200, 201]:
                print(f"   Producto creado: {producto['name']} - ${producto['price']:,}")
            else:
                print(f"   Error creando {producto['name']}: {response.status_code}")
    
    # Test Store - Productos de ropa y accesorios
    print("\nAGREGANDO PRODUCTOS A TEST STORE")
    login_response = requests.post('http://localhost:8002/auth/login', json={
        'email': 'admin@teststore.com',
        'password': 'test123'
    })
    
    if login_response.status_code == 200:
        token = login_response.json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        
        productos_test = [
            {
                "name": "Chaqueta Nike Sportswear",
                "description": "Chaqueta deportiva con capucha, perfecta para entrenamientos y uso casual",
                "category": "Ropa Deportiva",
                "price": 89990,
                "stock": 20,
                "image_url": "https://example.com/nike-jacket.jpg",
                "status": "active"
            },
            {
                "name": "Jeans Levis 501 Original",
                "description": "Jeans clasicos de corte recto en denim premium, icono de la moda",
                "category": "Pantalones",
                "price": 79990,
                "stock": 30,
                "image_url": "https://example.com/levis-501.jpg",
                "status": "active"
            },
            {
                "name": "Zapatillas Adidas Ultraboost 22",
                "description": "Zapatillas running con tecnologia Boost y upper Primeknit",
                "category": "Calzado",
                "price": 159990,
                "stock": 15,
                "image_url": "https://example.com/adidas-ultraboost.jpg",
                "status": "active"
            },
            {
                "name": "Polera Tommy Hilfiger",
                "description": "Polera clasica de algodon con logo bordado, corte regular",
                "category": "Poleras",
                "price": 49990,
                "stock": 40,
                "image_url": "https://example.com/tommy-polo.jpg",
                "status": "active"
            },
            {
                "name": "Reloj Fossil Grant Chronograph",
                "description": "Reloj analogico con cronografo, correa de cuero genuino",
                "category": "Accesorios",
                "price": 199990,
                "stock": 12,
                "image_url": "https://example.com/fossil-watch.jpg",
                "status": "active"
            },
            {
                "name": "Mochila Herschel Little America",
                "description": "Mochila urbana con compartimento para laptop y diseno retro",
                "category": "Accesorios",
                "price": 119990,
                "stock": 25,
                "image_url": "https://example.com/herschel-backpack.jpg",
                "status": "active"
            },
            {
                "name": "Sudadera Champion Reverse Weave",
                "description": "Sudadera premium con tecnologia anti-encogimiento",
                "category": "Ropa Deportiva",
                "price": 69990,
                "stock": 18,
                "image_url": "https://example.com/champion-hoodie.jpg",
                "status": "active"
            },
            {
                "name": "Gafas Ray-Ban Aviator",
                "description": "Gafas de sol iconicas con lentes polarizados y montura metalica",
                "category": "Accesorios",
                "price": 189990,
                "stock": 22,
                "image_url": "https://example.com/rayban-aviator.jpg",
                "status": "active"
            },
            {
                "name": "Vestido Zara Midi",
                "description": "Vestido elegante de largo midi, perfecto para ocasiones especiales",
                "category": "Vestidos",
                "price": 59990,
                "stock": 16,
                "image_url": "https://example.com/zara-dress.jpg",
                "status": "active"
            },
            {
                "name": "Cinturon Gucci GG Canvas",
                "description": "Cinturon de lujo con hebilla GG en canvas signature",
                "category": "Accesorios",
                "price": 449990,
                "stock": 8,
                "image_url": "https://example.com/gucci-belt.jpg",
                "status": "active"
            }
        ]
        
        for producto in productos_test:
            response = requests.post('http://localhost:8002/api/products', json=producto, headers=headers)
            if response.status_code in [200, 201]:
                print(f"   Producto creado: {producto['name']} - ${producto['price']:,}")
            else:
                print(f"   Error creando {producto['name']}: {response.status_code}")
    
    print(f"\nPRODUCTOS AGREGADOS EXITOSAMENTE")
    print("=" * 50)
    print("DEMO COMPANY (Tecnologia):")
    print("   - 10 productos nuevos agregados")
    print("   - Categorias: Smartphones, Laptops, Televisores, Gaming, Tablets, Audio, Monitores")
    print("   - Rango: $249,990 - $1,599,990")
    print("")
    print("TEST STORE (Ropa y Accesorios):")
    print("   - 10 productos nuevos agregados") 
    print("   - Categorias: Ropa Deportiva, Pantalones, Calzado, Poleras, Accesorios, Vestidos")
    print("   - Rango: $49,990 - $449,990")

if __name__ == "__main__":
    agregar_productos_originales()