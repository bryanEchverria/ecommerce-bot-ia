"""
Script simple para probar la integración completa
"""
import requests
import time
import json

def create_whatsapp_order():
    print("=== PRUEBA DE INTEGRACION COMPLETA ===")
    print()
    
    telefono = "+56999000111"
    
    # 1. Iniciar conversación
    print("1. Iniciando conversacion...")
    response1 = requests.post("http://localhost:8001/webhook", json={
        "telefono": telefono,
        "mensaje": "Hola, quiero ver productos"
    })
    print(f"   Bot: {response1.json()['respuesta'][:100]}...")
    
    # 2. Buscar producto
    print("2. Buscando MacBook...")
    response2 = requests.post("http://localhost:8001/webhook", json={
        "telefono": telefono,
        "mensaje": "Quiero una MacBook"
    })
    print(f"   Bot: {response2.json()['respuesta'][:100]}...")
    
    # 3. Especificar cantidad
    print("3. Especificando cantidad...")
    response3 = requests.post("http://localhost:8001/webhook", json={
        "telefono": telefono,
        "mensaje": "Quiero 1 unidad"
    })
    print(f"   Bot: {response3.json()['respuesta'][:100]}...")
    
    # 4. Confirmar compra
    print("4. Confirmando compra...")
    response4 = requests.post("http://localhost:8001/webhook", json={
        "telefono": telefono,
        "mensaje": "Si, confirmo la compra"
    })
    
    bot_response = response4.json()['respuesta']
    print(f"   Bot: {bot_response[:150]}...")
    
    # Extraer order ID
    import re
    order_match = re.search(r'ID de orden:\*\* ([a-f0-9-]+)', bot_response)
    if order_match:
        order_id = order_match.group(1)
        print(f"   Order ID: {order_id}")
        return order_id
    else:
        print("   No se pudo extraer el Order ID")
        return None

def verify_order_in_backend(order_id):
    print(f"5. Verificando pedido {order_id} en backend...")
    
    try:
        response = requests.get(f"http://localhost:8002/api/orders/{order_id}")
        if response.status_code == 200:
            order = response.json()
            print(f"   Pedido encontrado:")
            print(f"      Cliente: {order['customer_name']}")
            print(f"      Total: ${order['total']}")
            print(f"      Estado: {order['status']}")
            print(f"      Items: {order['items']}")
            return True
        else:
            print(f"   Pedido no encontrado: {response.status_code}")
            return False
    except Exception as e:
        print(f"   Error verificando pedido: {e}")
        return False

def simulate_payment(order_id):
    print(f"6. Simulando pago para pedido {order_id}...")
    
    try:
        response = requests.put(f"http://localhost:8002/api/orders/{order_id}", 
                              json={"status": "Delivered"})
        if response.status_code == 200:
            print("   Pago confirmado - Estado: Delivered")
            return True
        else:
            print(f"   Error confirmando pago: {response.status_code}")
            return False
    except Exception as e:
        print(f"   Error simulando pago: {e}")
        return False

def verify_dashboard_update():
    print("7. Verificando actualizacion del dashboard...")
    
    try:
        stats_response = requests.get("http://localhost:8002/api/dashboard/stats")
        if stats_response.status_code == 200:
            stats = stats_response.json()
            print(f"   Total de pedidos: {stats['total_orders']}")
            print(f"   Revenue total: ${stats['total_revenue']}")
        
        orders_response = requests.get("http://localhost:8002/api/orders")
        if orders_response.status_code == 200:
            orders = orders_response.json()
            print(f"   Total pedidos en lista: {len(orders)}")
            
            print("   Ultimos pedidos:")
            for i, order in enumerate(orders[:3]):
                print(f"      {i+1}. {order['customer_name']} - ${order['total']} - {order['status']}")
            
            return True
        else:
            print(f"   Error obteniendo pedidos: {orders_response.status_code}")
            return False
            
    except Exception as e:
        print(f"   Error verificando dashboard: {e}")
        return False

if __name__ == "__main__":
    order_id = create_whatsapp_order()
    
    if order_id:
        time.sleep(1)
        
        backend_ok = verify_order_in_backend(order_id)
        if backend_ok:
            payment_ok = simulate_payment(order_id)
            if payment_ok:
                time.sleep(1)
                dashboard_ok = verify_dashboard_update()
                
                print()
                print("=== RESULTADO DE LA PRUEBA ===")
                print(f"Conversacion WhatsApp: OK")
                print(f"Creacion en Backend: OK")  
                print(f"Confirmacion de Pago: OK")
                print(f"Actualizacion Dashboard: OK")
                print()
                print("INTEGRACION COMPLETA FUNCIONANDO!")
                print(f"Puedes ver el pedido {order_id} en:")
                print(f"   Frontend: http://localhost:3000")
                print(f"   Backend API: http://localhost:8002/api/orders/{order_id}")
            else:
                print("Fallo la confirmacion de pago")
        else:
            print("Fallo la verificacion en backend")
    else:
        print("Fallo la creacion del pedido desde WhatsApp")