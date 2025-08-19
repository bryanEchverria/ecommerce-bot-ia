import requests
import json

print("=== DEBUGGING FRONTEND AUTH ISSUE ===")
print()

# Simulate frontend login process
print("1. Testing login process (como hace el frontend)...")
login_data = {
    'email': 'admin@mundocanino.com',
    'password': 'canino123'
}

login_response = requests.post('http://localhost:8002/auth/login', json=login_data)
print(f"Login status: {login_response.status_code}")

if login_response.status_code == 200:
    auth_data = login_response.json()
    token = auth_data['access_token']
    client_info = auth_data['client']
    
    print(f"Token received: {token[:50]}...")
    print(f"Client ID: {client_info['id']}")
    print(f"Client Name: {client_info['name']}")
    print()
    
    # Test token immediately (como hace el frontend)
    print("2. Testing immediate token usage (GET /api/products)...")
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    products_response = requests.get('http://localhost:8002/api/products', headers=headers)
    print(f"Products GET status: {products_response.status_code}")
    
    if products_response.status_code == 403:
        print("ERROR: 403 Forbidden!")
        print(f"Response body: {products_response.text}")
        
        # Let's check token validation
        print()
        print("3. Testing token validation...")
        
        # Try to decode token (without validation)
        import base64
        try:
            # Split token into parts
            parts = token.split('.')
            if len(parts) == 3:
                # Decode payload (with padding)
                payload = parts[1]
                # Add padding if needed
                padding = 4 - len(payload) % 4
                if padding != 4:
                    payload += '=' * padding
                
                decoded = base64.b64decode(payload)
                payload_data = json.loads(decoded)
                
                print(f"Token payload:")
                print(f"  - sub (user): {payload_data.get('sub')}")
                print(f"  - client_id: {payload_data.get('client_id')}")  
                print(f"  - exp (expires): {payload_data.get('exp')}")
                print(f"  - iat (issued): {payload_data.get('iat')}")
        except Exception as e:
            print(f"Error decoding token: {e}")
        
        print()
        print("4. Testing with fresh login...")
        # Try fresh login
        fresh_login = requests.post('http://localhost:8002/auth/login', json=login_data)
        if fresh_login.status_code == 200:
            fresh_token = fresh_login.json()['access_token']
            fresh_headers = {
                'Authorization': f'Bearer {fresh_token}',
                'Content-Type': 'application/json'
            }
            
            fresh_products = requests.get('http://localhost:8002/api/products', headers=fresh_headers)
            print(f"Fresh token products status: {fresh_products.status_code}")
            
            if fresh_products.status_code == 200:
                print("SUCCESS: Fresh token works!")
                products = fresh_products.json()
                print(f"Products found: {len(products)}")
            else:
                print(f"ERROR: Fresh token also fails: {fresh_products.text}")
    
    elif products_response.status_code == 200:
        products = products_response.json()
        print(f"SUCCESS: Found {len(products)} products")
        
        # Test POST (create product)
        print()
        print("3. Testing product creation (POST /api/products)...")
        test_product = {
            "name": "Test Product Frontend",
            "description": "Producto de prueba desde frontend debugging",
            "category": "Test",
            "price": 999,
            "stock": 1,
            "image_url": "https://example.com/test.jpg",
            "status": "active"
        }
        
        create_response = requests.post('http://localhost:8002/api/products', 
                                      json=test_product, headers=headers)
        print(f"Product creation status: {create_response.status_code}")
        
        if create_response.status_code == 403:
            print("ERROR: Cannot create products - 403 Forbidden")
            print(f"Response: {create_response.text}")
        elif create_response.status_code in [200, 201]:
            print("SUCCESS: Product creation works")
        else:
            print(f"ERROR: Unexpected status {create_response.status_code}")
            print(f"Response: {create_response.text}")
    
    else:
        print(f"ERROR: Unexpected products status: {products_response.status_code}")
        print(f"Response: {products_response.text}")

else:
    print(f"ERROR: Login failed: {login_response.text}")

print()
print("=== CHECKING AUTH MIDDLEWARE ===")
print("Possible issues:")
print("- Token validation in backend failing for this specific client")
print("- CORS or header issues")
print("- Client ID mismatch in database")
print("- Token expiration issues")
print("- Database permissions for this client")