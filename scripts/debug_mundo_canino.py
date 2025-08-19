import requests

print('=== DEBUGGING MUNDO CANINO ===')

# Login to Mundo Canino
login_response = requests.post('http://localhost:8002/auth/login', json={
    'email': 'admin@mundocanino.com',
    'password': 'canino123'
})

print(f'Login status: {login_response.status_code}')

if login_response.status_code == 200:
    auth_data = login_response.json()
    token = auth_data['access_token']
    client_id = auth_data['client']['id']
    client_name = auth_data['client']['name']
    
    print(f'Client ID: {client_id}')
    print(f'Client Name: {client_name}')
    
    headers = {'Authorization': f'Bearer {token}'}
    
    # Check products
    products_response = requests.get('http://localhost:8002/api/products', headers=headers)
    print(f'Products API status: {products_response.status_code}')
    
    if products_response.status_code == 200:
        products = products_response.json()
        print(f'Number of products: {len(products)}')
        
        if products:
            print('Products found:')
            for i, product in enumerate(products[:5]):
                print(f'  {i+1}. {product.get("name", "No name")} - ${product.get("price", 0):,} - Stock: {product.get("stock", 0)}')
        else:
            print('No products found for this client')
            
            # Let's check the database directly to see what's happening
            print('\n=== CHECKING ALL CLIENTS ===')
            
            # Try to get client info
            clients_response = requests.get('http://localhost:8002/api/clients', headers=headers)
            if clients_response.status_code == 200:
                print(f'Clients API works: {clients_response.status_code}')
            
    else:
        print(f'Error getting products: {products_response.text}')
else:
    print(f'Login failed: {login_response.text}')

print('\n=== COMPARING WITH OTHER ACCOUNTS ===')

# Check Demo Company for comparison
demo_login = requests.post('http://localhost:8002/auth/login', json={
    'email': 'admin@demo.com',
    'password': 'demo123'
})

if demo_login.status_code == 200:
    demo_token = demo_login.json()['access_token']
    demo_headers = {'Authorization': f'Bearer {demo_token}'}
    
    demo_products = requests.get('http://localhost:8002/api/products', headers=demo_headers)
    if demo_products.status_code == 200:
        demo_count = len(demo_products.json())
        print(f'Demo Company has {demo_count} products')
    
    demo_client_id = demo_login.json()['client']['id']
    print(f'Demo Company Client ID: {demo_client_id}')