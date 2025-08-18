import requests
import time

def test_new_order_integration():
    print("Testing new order creation from WhatsApp bot...")
    
    webhook_url = "http://localhost:8003/webhook"
    orders_url = "http://localhost:8004/api/orders"
    
    # Get current order count
    response = requests.get(orders_url)
    initial_orders = len(response.json()) if response.status_code == 200 else 0
    print(f"Initial orders in backoffice: {initial_orders}")
    
    # Create new order via WhatsApp bot
    test_phone = "56999888777"
    
    # Step 1: Product inquiry
    print(f"\n1. Product inquiry from {test_phone}")
    response = requests.post(webhook_url, json={
        "telefono": test_phone,
        "mensaje": "quiero comprar un iPhone 15"
    })
    print(f"Bot response: {response.json()['respuesta'][:80]}...")
    
    # Step 2: Quantity
    print("\n2. Specify quantity")
    response = requests.post(webhook_url, json={
        "telefono": test_phone,
        "mensaje": "quiero 1 unidad"
    })
    print(f"Bot response: {response.json()['respuesta'][:80]}...")
    
    # Step 3: Confirm purchase
    print("\n3. Confirm purchase")
    response = requests.post(webhook_url, json={
        "telefono": test_phone,
        "mensaje": "confirmo compra"
    })
    
    if response.status_code == 200:
        bot_response = response.json()['respuesta']
        print(f"Bot response: {bot_response[:100]}...")
        
        if "flow.cl" in bot_response or "pago" in bot_response.lower():
            print("Payment process initiated!")
        else:
            print("No payment process detected")
    
    # Step 4: Check if order appeared in backoffice
    print("\n4. Checking backoffice for new order...")
    time.sleep(3)  # Wait for order creation
    
    response = requests.get(orders_url)
    if response.status_code == 200:
        orders = response.json()
        new_orders = len(orders)
        print(f"Orders after test: {new_orders}")
        
        # Look for our test order
        test_orders = [order for order in orders if test_phone[-4:] in order.get('customer_name', '')]
        if test_orders:
            print(f"Found {len(test_orders)} orders from test phone!")
            latest_order = test_orders[0]
            print(f"  Order ID: {latest_order.get('id')}")
            print(f"  Customer: {latest_order.get('customer_name')}")
            print(f"  Total: ${latest_order.get('total')}")
            print(f"  Status: {latest_order.get('status')}")
            print(f"  Items: {latest_order.get('items')}")
        else:
            print("No orders found from test phone")
    else:
        print(f"Error getting orders: {response.status_code}")
    
    print("\nIntegration test completed!")

if __name__ == "__main__":
    test_new_order_integration()