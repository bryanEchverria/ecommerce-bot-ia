import requests

# Login to Mundo Canino
login_response = requests.post('http://localhost:8002/auth/login', json={
    'email': 'admin@mundocanino.com',
    'password': 'canino123'
})

if login_response.status_code == 200:
    auth_data = login_response.json()
    token = auth_data['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    
    print("Creating tenant orders for Mundo Canino...")
    
    orders = [
        {
            "code": "MC-001",
            "customer_name": "Maria Gonzalez +56987654321",
            "total": "89990",
            "status": "Completed"
        },
        {
            "code": "MC-002", 
            "customer_name": "Carlos Martinez +56912345678",
            "total": "45990",
            "status": "Pending"
        },
        {
            "code": "MC-003",
            "customer_name": "Ana Silva +56923456789",
            "total": "65990", 
            "status": "Shipped"
        }
    ]
    
    for order in orders:
        response = requests.post('http://localhost:8002/api/tenant-orders/', 
                               json=order, headers=headers)
        
        if response.status_code in [200, 201]:
            print(f"Created: {order['code']} - {order['customer_name']}")
        else:
            print(f"Failed: {order['code']} - {response.status_code}")
    
    # Check results
    tenant_orders = requests.get('http://localhost:8002/api/tenant-orders/', headers=headers)
    if tenant_orders.status_code == 200:
        orders_data = tenant_orders.json()
        print(f"\nMundo Canino tenant orders: {len(orders_data)}")
        
        for order in orders_data:
            print(f"  {order.get('code')} - {order.get('customer_name')} - ${int(order.get('total', 0)):,}")
    
    # Compare with legacy
    legacy_orders = requests.get('http://localhost:8002/api/orders', headers=headers)
    if legacy_orders.status_code == 200:
        legacy_data = legacy_orders.json()
        print(f"\nLegacy orders (all clients): {len(legacy_data)}")
        
        print(f"\n[RESULT] Tenant isolation: {len(orders_data)} vs {len(legacy_data)}")
        if len(orders_data) < len(legacy_data):
            print("[SUCCESS] Tenant isolation working - orders are isolated by client")
        else:
            print("[WARNING] Possible isolation issue")
            
else:
    print(f"Login failed: {login_response.text}")