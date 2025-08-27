import requests

# Login to Demo Company
login_response = requests.post('http://localhost:8002/auth/login', json={
    'email': 'admin@demo.com',
    'password': 'demo123'
})

if login_response.status_code == 200:
    token = login_response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    
    # Get recent orders
    orders_response = requests.get('http://localhost:8002/api/orders', headers=headers)
    
    if orders_response.status_code == 200:
        orders = orders_response.json()
        print(f'Total orders: {len(orders)}')
        
        # Show the most recent order
        if orders:
            latest_order = sorted(orders, key=lambda x: x.get('created_at', ''), reverse=True)[0]
            print(f'\nMost recent order:')
            print(f'  Order Number: {latest_order.get("order_number", "N/A")}')
            print(f'  Customer: {latest_order.get("customer_name", "N/A")}')
            print(f'  Total: ${latest_order.get("total", 0)}')
            print(f'  Status: {latest_order.get("status", "N/A")}')
            print(f'  Date: {latest_order.get("created_at", "N/A")[:19]}')
            
            # Check if this is our WhatsApp order
            if 'WhatsApp' in latest_order.get('customer_name', '') or latest_order.get('order_number') == 'ORD-000004':
                print('\n[SUCCESS] This is our WhatsApp order!')
                print('Enhanced Bot 2.0 successfully created order in backoffice!')
            else:
                print('\n[INFO] Recent order found')
        else:
            print('No orders found')
    else:
        print(f'Error getting orders: {orders_response.status_code}')
else:
    print(f'Login error: {login_response.status_code}')