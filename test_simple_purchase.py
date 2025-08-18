"""
Prueba simple de compra con productos reales
"""
import requests
import time

def test_simple_purchase():
    print("===== PRODUCTOS REALES DE DEMO COMPANY =====")
    
    # Login como Demo Company
    demo_login = requests.post('http://localhost:8002/auth/login', json={
        'email': 'admin@demo.com',
        'password': 'demo123'
    })
    
    if demo_login.status_code == 200:
        token = demo_login.json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # Obtener productos reales
        products_response = requests.get('http://localhost:8002/api/products', headers=headers)
        
        if products_response.status_code == 200:
            products = products_response.json()
            print(f"Demo Company tiene {len(products)} productos:")
            
            for product in products:
                name = product['name']
                category = product['category']
                price = product['price']
                stock = product['stock']
                print(f"- {name} | {category} | ${price} | Stock: {stock}")
            
            if products:
                # Usar el primer producto disponible
                producto_prueba = products[0]['name']
                print(f"\nPROBARE COMPRA CON: {producto_prueba}")
                
                # Nueva conversacion con numero fresco
                telefono_nuevo = "+5555555555"
                
                print(f"\n===== CONVERSACION DE COMPRA =====")
                
                # Paso 1: Saludo
                print("\n1. Cliente: Hola")
                response = requests.post('http://localhost:8001/webhook', json={
                    'telefono': telefono_nuevo,
                    'mensaje': 'Hola'
                })
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"Bot: {result.get('respuesta', '')[:100]}...")
                
                time.sleep(2)
                
                # Paso 2: Solicitar producto especifico
                print(f"\n2. Cliente: quiero comprar {producto_prueba}")
                response = requests.post('http://localhost:8001/webhook', json={
                    'telefono': telefono_nuevo,
                    'mensaje': f'quiero comprar {producto_prueba}'
                })
                
                if response.status_code == 200:
                    result = response.json()
                    respuesta = result.get('respuesta', '')
                    print(f"Bot: {respuesta[:200]}...")
                    
                    if 'precio' in respuesta.lower() or 'cuesta' in respuesta.lower():
                        print("[OK] Bot menciona precio")
                
                time.sleep(2)
                
                # Paso 3: Confirmar cantidad
                print("\n3. Cliente: quiero 1")
                response = requests.post('http://localhost:8001/webhook', json={
                    'telefono': telefono_nuevo,
                    'mensaje': 'quiero 1'
                })
                
                if response.status_code == 200:
                    result = response.json()
                    respuesta = result.get('respuesta', '')
                    print(f"Bot: {respuesta[:250]}...")
                    
                    if 'confirma' in respuesta.lower():
                        print("[OK] Bot pide confirmacion")
                
                time.sleep(2)
                
                # Paso 4: Confirmacion final
                print("\n4. Cliente: si, confirmo")
                response = requests.post('http://localhost:8001/webhook', json={
                    'telefono': telefono_nuevo,
                    'mensaje': 'si, confirmo'
                })
                
                if response.status_code == 200:
                    result = response.json()
                    respuesta = result.get('respuesta', '')
                    print(f"Bot: {respuesta[:400]}...")
                    
                    # Buscar orden generada
                    import re
                    orders = re.findall(r'ORD-\d{6}', respuesta)
                    if orders:
                        print(f"[SUCCESS] ORDEN CREADA: {orders[0]}")
                        return orders[0]
                    
                    # Buscar enlace de pago
                    if 'http' in respuesta:
                        print("[SUCCESS] Enlace de pago generado!")
                    
                    if 'pago' in respuesta.lower():
                        print("[OK] Proceso de pago iniciado")
                        
                    if 'error' in respuesta.lower() or 'problema' in respuesta.lower():
                        print("[ERROR] Bot reporta problema")
                else:
                    print(f"[ERROR] Status final: {response.status_code}")
                
                # Verificar si la orden aparece en el backoffice
                print(f"\n===== VERIFICAR EN BACKOFFICE =====")
                orders_response = requests.get('http://localhost:8002/api/orders', headers=headers)
                
                if orders_response.status_code == 200:
                    orders = orders_response.json()
                    print(f"Total ordenes en backoffice: {len(orders)}")
                    
                    # Buscar ordenes recientes (ultimos 5 minutos)
                    from datetime import datetime, timedelta
                    now = datetime.now()
                    recent_orders = []
                    
                    for order in orders:
                        try:
                            order_time = datetime.fromisoformat(order['created_at'].replace('Z', '+00:00').replace('+00:00', ''))
                            if (now - order_time).total_seconds() < 300:  # 5 minutos
                                recent_orders.append(order)
                        except:
                            pass
                    
                    if recent_orders:
                        print(f"Ordenes recientes (ultimos 5 min): {len(recent_orders)}")
                        for order in recent_orders:
                            order_num = order.get('order_number', order.get('id'))
                            customer = order.get('customer_name', 'N/A')
                            total = order.get('total', 0)
                            print(f"- {order_num} | {customer} | ${total}")
                    else:
                        print("No hay ordenes recientes")
                else:
                    print(f"Error obteniendo ordenes: {orders_response.status_code}")
                    
            else:
                print("No hay productos disponibles")
        else:
            print(f"Error obteniendo productos: {products_response.status_code}")
    else:
        print(f"Error en login: {demo_login.status_code}")

if __name__ == "__main__":
    test_simple_purchase()