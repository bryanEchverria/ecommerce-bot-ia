import requests
import time

def test_order_statuses_display():
    """Test order status translations and display"""
    
    print("=== TESTING ORDER STATUS DISPLAY ===")
    
    # Create a test order
    print("\n1. Creating test order...")
    order_data = {
        "customer_name": "Cliente Prueba Estados",
        "date": "2025-01-15T12:00:00",
        "total": 35000.0,
        "status": "Pending",
        "items": 3
    }
    
    try:
        response = requests.post("http://localhost:8002/api/orders", json=order_data)
        if response.status_code in [200, 201]:
            order = response.json()
            order_id = order['id']
            order_number = order.get('order_number')
            print(f"[OK] Order created: {order_number}")
        else:
            print(f"[ERROR] Failed to create order: {response.status_code}")
            return
    except Exception as e:
        print(f"[ERROR] Error creating order: {e}")
        return
    
    # Test all order status transitions
    print(f"\n2. Testing order status transitions...")
    
    statuses = [
        ("Pending", "Pendiente"),
        ("Received", "Recibido"), 
        ("Shipping", "En Envío"),
        ("Delivered", "Entregado")
    ]
    
    for status_en, status_es in statuses:
        print(f"\n   Testing status: {status_en} / {status_es}")
        
        # Update order status
        update_data = {"status": status_en}
        try:
            response = requests.put(f"http://localhost:8002/api/orders/{order_id}", json=update_data)
            if response.status_code == 200:
                updated_order = response.json()
                print(f"   [OK] Status updated to: {updated_order['status']}")
                print(f"   [INFO] Order number: {updated_order.get('order_number', 'N/A')}")
            else:
                print(f"   [ERROR] Failed to update to {status_en}: {response.status_code}")
        except Exception as e:
            print(f"   [ERROR] Error updating to {status_en}: {e}")
        
        time.sleep(1)
    
    # Test order lookup by number
    print(f"\n3. Testing order lookup by number...")
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
    
    # Check orders list
    print(f"\n4. Checking orders list...")
    try:
        response = requests.get("http://localhost:8002/api/orders")
        if response.status_code == 200:
            orders = response.json()
            print(f"[OK] Total orders in system: {len(orders)}")
            
            # Find orders with different statuses for display verification
            status_counts = {}
            for order in orders:
                status = order.get('status', 'Unknown')
                status_counts[status] = status_counts.get(status, 0) + 1
            
            print(f"   Status distribution:")
            for status, count in status_counts.items():
                print(f"     - {status}: {count} orders")
                
        else:
            print(f"[ERROR] Failed to get orders list: {response.status_code}")
    except Exception as e:
        print(f"[ERROR] Error getting orders list: {e}")
    
    print(f"\n=== STATUS DISPLAY TEST COMPLETE ===")
    print(f"Test Order Number: {order_number}")
    print(f"Final Status: Delivered")
    print(f"\nNow check the frontend at http://127.0.0.1:3000 to verify:")
    print(f"1. Order numbers are displayed correctly")
    print(f"2. Status badges show proper translations")
    print(f"3. New statuses (Received, Shipping) are visible")
    print(f"4. Search by order number works")

if __name__ == "__main__":
    test_order_statuses_display()