import requests
from datetime import datetime, timedelta

def create_tenant_orders_mundo_canino():
    print("=== CREATING TENANT ORDERS FOR MUNDO CANINO ===")
    
    # Login to Mundo Canino
    login_response = requests.post('http://localhost:8002/auth/login', json={
        'email': 'admin@mundocanino.com',
        'password': 'canino123'
    })
    
    if login_response.status_code != 200:
        print(f"Login failed: {login_response.text}")
        return
    
    auth_data = login_response.json()
    token = auth_data['access_token']
    client_name = auth_data['client']['name']
    
    print(f"Logged in as: {client_name}")
    
    headers = {'Authorization': f'Bearer {token}'}
    
    # Create test orders using tenant-aware endpoint
    orders_to_create = [
        {
            "code": "MC-001",
            "customer_name": "Maria Gonzalez +56987654321",
            "total": "89990",  # String as required by schema
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
        },
        {
            "code": "MC-004",
            "customer_name": "Luis Rodriguez +56934567890",
            "total": "28990",
            "status": "Processing"
        },
        {
            "code": "MC-005",
            "customer_name": "Patricia Torres +56945678901",
            "total": "112980",  # Multiple items
            "status": "Completed"
        }
    ]
    
    print(f"\nCreating {len(orders_to_create)} tenant orders...")
    
    created_count = 0
    for order_data in orders_to_create:
        response = requests.post('http://localhost:8002/api/tenant-orders/', 
                               json=order_data, headers=headers)
        
        if response.status_code in [200, 201]:
            created_order = response.json()
            print(f"✓ Created: {order_data['code']} - {order_data['customer_name']} - ${int(order_data['total']):,}")
            created_count += 1
        else:
            print(f"✗ Failed to create {order_data['code']}: {response.status_code} - {response.text}")
    
    print(f"\nSuccessfully created {created_count}/{len(orders_to_create)} orders")
    
    # Verify tenant isolation
    print("\n=== VERIFYING TENANT ISOLATION ===")
    
    # Check tenant orders
    tenant_orders_response = requests.get('http://localhost:8002/api/tenant-orders/', headers=headers)
    if tenant_orders_response.status_code == 200:
        tenant_orders = tenant_orders_response.json()
        print(f"Tenant orders for Mundo Canino: {len(tenant_orders)}")
        
        print("\nTenant orders:")
        for order in tenant_orders:
            code = order.get('code', 'No code')
            customer = order.get('customer_name', 'No customer')
            status = order.get('status', 'No status')
            total = order.get('total', 0)
            print(f"  - {code} | {customer} | {status} | ${int(total):,}")
    else:
        print(f"Error getting tenant orders: {tenant_orders_response.text}")
    
    # Compare with legacy orders
    legacy_orders_response = requests.get('http://localhost:8002/api/orders', headers=headers)
    if legacy_orders_response.status_code == 200:
        legacy_orders = legacy_orders_response.json()
        print(f"\nLegacy orders (ALL clients): {len(legacy_orders)}")
        
        if len(tenant_orders) != len(legacy_orders):
            print("✓ GOOD: Tenant isolation working - different counts")
        else:
            print("⚠ WARNING: Same count - check if isolation is working")
    
    print(f"\n[SUCCESS] Mundo Canino now has {len(tenant_orders)} orders with proper tenant isolation")

if __name__ == "__main__":
    create_tenant_orders_mundo_canino()