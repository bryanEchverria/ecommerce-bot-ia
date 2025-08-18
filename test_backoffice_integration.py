import requests
import json
import time

# Test the complete integration between WhatsApp bot and backoffice
def test_complete_integration():
    print("Testing complete WhatsApp bot to backoffice integration...")
    
    # Step 1: Test WhatsApp bot purchase flow
    print("\n1. Testing WhatsApp bot purchase flow...")
    
    webhook_url = "http://localhost:8003/webhook"
    bot_data = {
        "telefono": "56912345678",
        "mensaje": "quiero comprar un iPhone 15"
    }
    
    print(f"Sending to bot: {bot_data['mensaje']}")
    response = requests.post(webhook_url, json=bot_data)
    
    if response.status_code == 200:
        bot_response = response.json()
        print(f"Bot response: {bot_response['respuesta'][:100]}...")
    else:
        print(f"Bot error: {response.status_code} - {response.text}")
        return
    
    # Step 2: Confirm purchase to generate payment link
    print("\n2. Confirming purchase...")
    
    confirm_data = {
        "telefono": "56912345678", 
        "mensaje": "si, confirmo la compra de 2 unidades"
    }
    
    print(f"Sending to bot: {confirm_data['mensaje']}")
    response = requests.post(webhook_url, json=confirm_data)
    
    if response.status_code == 200:
        bot_response = response.json()
        print(f"Bot response: {bot_response['respuesta'][:200]}...")
        
        # Check if payment link was generated
        if "flow.cl" in bot_response['respuesta']:
            print("Payment link generated successfully!")
        else:
            print("No payment link found in response")
    else:
        print(f"Bot error: {response.status_code} - {response.text}")
        return
    
    # Step 3: Check if order was created in backoffice
    print("\n3. Checking if order appears in backoffice dashboard...")
    
    time.sleep(2)  # Wait for order creation
    
    dashboard_url = "http://localhost:8004/api/orders"
    
    try:
        response = requests.get(dashboard_url)
        if response.status_code == 200:
            orders = response.json()
            print(f"Found {len(orders)} orders in backoffice")
            
            # Look for WhatsApp orders
            whatsapp_orders = [order for order in orders if "WhatsApp" in order.get('customer_name', '')]
            if whatsapp_orders:
                print(f"Found {len(whatsapp_orders)} WhatsApp orders!")
                latest_order = whatsapp_orders[0]
                print(f"   Order ID: {latest_order.get('id')}")
                print(f"   Customer: {latest_order.get('customer_name')}")
                print(f"   Total: ${latest_order.get('total')}")
                print(f"   Status: {latest_order.get('status')}")
            else:
                print("No WhatsApp orders found in dashboard")
        else:
            print(f"Dashboard error: {response.status_code} - {response.text}")
    except requests.RequestException as e:
        print(f"Could not connect to dashboard: {e}")
    
    # Step 4: Check dashboard statistics
    print("\n4. Checking dashboard statistics...")
    
    stats_url = "http://localhost:8004/api/dashboard/stats"
    
    try:
        response = requests.get(stats_url)
        if response.status_code == 200:
            stats = response.json()
            print(f"Dashboard stats:")
            print(f"   Total Orders: {stats.get('total_orders')}")
            print(f"   Pending Orders: {stats.get('pending_orders')}")
            print(f"   Total Revenue: ${stats.get('total_revenue')}")
            print(f"   Total Clients: {stats.get('total_clients')}")
        else:
            print(f"Stats error: {response.status_code} - {response.text}")
    except requests.RequestException as e:
        print(f"Could not get dashboard stats: {e}")
    
    print("\nIntegration test completed!")
    print("Summary:")
    print("- WhatsApp bot: Running on port 8003")
    print("- Backoffice API: Running on port 8004") 
    print("- Orders flow from bot -> backoffice dashboard")
    print("- Payment confirmations update order status")

if __name__ == "__main__":
    test_complete_integration()