import requests
import time
import json

def test_complete_order_flow():
    """Test the complete order flow: creation -> status updates -> customer tracking"""
    
    print("=== TESTING COMPLETE ORDER FLOW ===")
    
    # Step 1: Create a test order via backend API
    print("\n1. Creating test order...")
    order_data = {
        "customer_name": "Cliente Prueba WhatsApp",
        "client_id": None,
        "date": "2025-01-15T10:30:00",
        "total": 25000.0,
        "status": "Pending",
        "items": 2
    }
    
    try:
        response = requests.post("http://localhost:8002/api/orders", json=order_data)
        if response.status_code in [200, 201]:
            order = response.json()
            order_id = order['id']
            order_number = order.get('order_number')
            print(f"[OK] Order created successfully!")
            print(f"   Order ID: {order_id}")
            print(f"   Order Number: {order_number}")
            print(f"   Status: {order['status']}")
        else:
            print(f"[ERROR] Failed to create order: {response.status_code}")
            print(f"   Response: {response.text}")
            return
    except Exception as e:
        print(f"[ERROR] Error creating order: {e}")
        return
    
    # Step 2: Test order status updates (simulate store owner workflow)
    print(f"\n2. Testing order status updates...")
    
    statuses = ["Received", "Shipping", "Delivered"]
    
    for new_status in statuses:
        print(f"\n   Updating order to: {new_status}")
        update_data = {"status": new_status}
        
        try:
            response = requests.put(f"http://localhost:8002/api/orders/{order_id}", json=update_data)
            if response.status_code == 200:
                updated_order = response.json()
                print(f"   [OK] Status updated to: {updated_order['status']}")
            else:
                print(f"   [ERROR] Failed to update status: {response.status_code}")
        except Exception as e:
            print(f"   [ERROR] Error updating status: {e}")
        
        time.sleep(1)  # Brief delay between updates
    
    # Step 3: Test order lookup by number (simulate customer checking status)
    print(f"\n3. Testing customer order lookup...")
    
    if order_number:
        try:
            response = requests.get(f"http://localhost:8002/api/orders/number/{order_number}")
            if response.status_code == 200:
                lookup_order = response.json()
                print(f"[OK] Order lookup successful!")
                print(f"   Order Number: {lookup_order.get('order_number')}")
                print(f"   Customer: {lookup_order['customer_name']}")
                print(f"   Status: {lookup_order['status']}")
                print(f"   Total: ${lookup_order['total']:,.0f}")
            else:
                print(f"[ERROR] Order lookup failed: {response.status_code}")
        except Exception as e:
            print(f"[ERROR] Error in order lookup: {e}")
    else:
        print("[ERROR] No order number available for lookup test")
    
    # Step 4: Test bot integration for order status checking
    print(f"\n4. Testing bot order status integration...")
    
    if order_number:
        # Simulate bot message asking for order status
        bot_data = {
            "mensaje": f"Hola, quiero consultar el estado de mi pedido {order_number}",
            "telefono": "+56912345678"
        }
        
        try:
            response = requests.post("http://localhost:8001/webhook", json=bot_data)
            if response.status_code == 200:
                bot_response = response.json()
                print(f"[OK] Bot order status check successful!")
                print(f"   Bot response: {bot_response.get('respuesta', 'No response')}")
            else:
                print(f"[ERROR] Bot integration failed: {response.status_code}")
                print(f"   Response: {response.text}")
        except Exception as e:
            print(f"[ERROR] Error testing bot integration: {e}")
    
    # Step 5: Verify frontend integration
    print(f"\n5. Testing frontend API integration...")
    
    try:
        response = requests.get("http://localhost:8002/api/orders")
        if response.status_code == 200:
            orders = response.json()
            print(f"[OK] Frontend API integration working!")
            print(f"   Total orders in system: {len(orders)}")
            
            # Find our test order
            test_order = next((o for o in orders if o['id'] == order_id), None)
            if test_order:
                print(f"   Test order found with status: {test_order['status']}")
                print(f"   Order number: {test_order.get('order_number', 'N/A')}")
            else:
                print(f"   [WARNING] Test order not found in orders list")
        else:
            print(f"[ERROR] Frontend API failed: {response.status_code}")
    except Exception as e:
        print(f"[ERROR] Error testing frontend integration: {e}")
    
    print(f"\n=== TEST COMPLETE ===")
    print(f"Order ID: {order_id}")
    print(f"Order Number: {order_number}")

if __name__ == "__main__":
    test_complete_order_flow()