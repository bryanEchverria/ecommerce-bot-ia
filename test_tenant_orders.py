import requests
import datetime

# Check tenant-aware orders for Test Store
print('=== CHECKING TENANT-AWARE ORDERS ===')
login_response = requests.post('http://localhost:8002/auth/login', json={
    'email': 'admin@teststore.com',
    'password': 'test123'
})

if login_response.status_code == 200:
    token = login_response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    
    # Check tenant orders
    tenant_orders = requests.get('http://localhost:8002/api/tenant-orders/', headers=headers)
    if tenant_orders.status_code == 200:
        orders = tenant_orders.json()
        print(f'Tenant-aware orders for Test Store: {len(orders)}')
        
        # Show latest order
        if orders:
            latest = orders[0]  # Ordered by created_at desc
            print(f'Latest: {latest.get("code")} | {latest.get("customer_name")} | ${latest.get("total")}')
            
            # Check if this is recent (from our test)
            created = latest.get('created_at', '')
            if created:
                created_time = datetime.datetime.fromisoformat(created.replace('Z', '+00:00'))
                now = datetime.datetime.now(datetime.timezone.utc)
                diff = (now - created_time).total_seconds()
                if diff < 300:  # Less than 5 minutes ago
                    print('   -> This order is from our recent test!')
                else:
                    print(f'   -> This order is {diff/60:.1f} minutes old')
        else:
            print('No tenant-aware orders found')
    else:
        print(f'Failed to get tenant orders: {tenant_orders.status_code}')
else:
    print(f'Login failed: {login_response.status_code}')

# Also check legacy orders
print('\n=== CHECKING LEGACY ORDERS ===')
legacy_orders = requests.get('http://localhost:8002/api/orders', headers=headers)
if legacy_orders.status_code == 200:
    orders = legacy_orders.json()
    whatsapp_orders = [o for o in orders if 'WhatsApp' in o.get('customer_name', '')]
    recent_whatsapp = sorted(whatsapp_orders, key=lambda x: x.get('created_at', ''), reverse=True)[:3]
    
    print(f'Recent WhatsApp orders in legacy: {len(recent_whatsapp)}')
    for order in recent_whatsapp:
        order_num = order.get('order_number', 'N/A')
        customer = order.get('customer_name', 'N/A')
        total = order.get('total', 0)
        date = order.get('created_at', '')[:19]
        print(f'  - {order_num} | {customer} | ${total} | {date}')