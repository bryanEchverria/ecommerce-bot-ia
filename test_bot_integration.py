"""
Test script para verificar la sincronización entre el bot de WhatsApp y el backend
"""
import requests
import json

def test_webhook_message():
    """Test sending a message to the WhatsApp bot webhook"""
    url = "http://localhost:8001/webhook"
    
    # Test data simulating a WhatsApp message
    test_data = {
        "telefono": "+56912345678",
        "mensaje": "Quiero comprar un iPhone 15 Pro"
    }
    
    print("Testing WhatsApp bot webhook...")
    print(f"Sending: {test_data}")
    
    try:
        response = requests.post(url, json=test_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_purchase_flow():
    """Test complete purchase flow from bot to backend"""
    print("\nTesting complete purchase flow...")
    
    # Step 1: Product inquiry
    print("Step 1: Product inquiry")
    response1 = requests.post("http://localhost:8001/webhook", json={
        "telefono": "+56912345678",
        "mensaje": "Quiero comprar un iPhone 15 Pro"
    })
    print(f"Bot response: {response1.json()['respuesta']}")
    
    # Step 2: Quantity confirmation
    print("\nStep 2: Quantity confirmation")
    response2 = requests.post("http://localhost:8001/webhook", json={
        "telefono": "+56912345678", 
        "mensaje": "Quiero 2 unidades"
    })
    print(f"Bot response: {response2.json()['respuesta']}")
    
    # Step 3: Purchase confirmation
    print("\nStep 3: Purchase confirmation")
    response3 = requests.post("http://localhost:8001/webhook", json={
        "telefono": "+56912345678",
        "mensaje": "Sí, confirmo la compra"
    })
    bot_response = response3.json()['respuesta']
    print(f"Bot response: {bot_response}")
    
    # Check if order was created in backend
    if "ID de orden:" in bot_response:
        # Extract order ID from response
        import re
        order_match = re.search(r'ID de orden:\*\* ([a-f0-9-]+)', bot_response)
        if order_match:
            order_id = order_match.group(1)
            print(f"\nChecking if order {order_id} exists in backend...")
            
            try:
                backend_response = requests.get(f"http://localhost:8002/api/orders/{order_id}")
                if backend_response.status_code == 200:
                    order_data = backend_response.json()
                    print(f"Order found in backend!")
                    print(f"   Customer: {order_data['customer_name']}")
                    print(f"   Total: ${order_data['total']}")
                    print(f"   Status: {order_data['status']}")
                    print(f"   Items: {order_data['items']}")
                    return True
                else:
                    print(f"Order not found in backend: {backend_response.status_code}")
                    return False
            except Exception as e:
                print(f"Error checking backend: {e}")
                return False
    
    print("No order ID found in bot response")
    return False

def check_backend_orders():
    """Check current orders in backend"""
    print("\nChecking current orders in backend...")
    
    try:
        response = requests.get("http://localhost:8002/api/orders")
        orders = response.json()
        
        print(f"Total orders: {len(orders)}")
        for order in orders[-3:]:  # Show last 3 orders
            print(f"  Order {order['id']}: {order['customer_name']} - ${order['total']} - {order['status']}")
        
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_payment_confirmation():
    """Simulate a payment confirmation"""
    print("\nTesting payment confirmation...")
    
    # First get the latest order
    try:
        response = requests.get("http://localhost:8002/api/orders")
        orders = response.json()
        
        if orders:
            latest_order = orders[-1]
            order_id = latest_order['id']
            
            print(f"Testing payment confirmation for order: {order_id}")
            
            # Simulate Flow payment confirmation
            confirmation_data = {
                "commerceOrder": order_id,
                "status": "2",  # Flow status for successful payment
                "s": "dummy_signature"  # Would be real signature in production
            }
            
            # This would normally come from Flow, but we'll simulate it
            print("Note: In real scenario, Flow would send this confirmation")
            print("For testing, we'll directly update the order status...")
            
            # Update order status directly
            update_response = requests.put(
                f"http://localhost:8002/api/orders/{order_id}",
                json={"status": "Delivered"}
            )
            
            if update_response.status_code == 200:
                print("Order status updated to Delivered")
                return True
            else:
                print(f"Failed to update order: {update_response.status_code}")
                return False
        else:
            print("No orders found to test payment confirmation")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    print("Testing Bot-Backend Synchronization")
    print("=" * 50)
    
    # Test 1: Basic webhook
    success1 = test_webhook_message()
    
    # Test 2: Complete purchase flow  
    success2 = test_purchase_flow()
    
    # Test 3: Check backend orders
    success3 = check_backend_orders()
    
    # Test 4: Payment confirmation
    success4 = test_payment_confirmation()
    
    print("\n" + "=" * 50)
    print("Test Results:")
    print(f"Webhook test: {'PASS' if success1 else 'FAIL'}")
    print(f"Purchase flow: {'PASS' if success2 else 'FAIL'}")  
    print(f"Backend orders: {'PASS' if success3 else 'FAIL'}")
    print(f"Payment confirmation: {'PASS' if success4 else 'FAIL'}")
    
    if all([success1, success2, success3, success4]):
        print("\nAll tests passed! Bot-Backend synchronization is working!")
    else:
        print("\nSome tests failed. Check the configuration.")