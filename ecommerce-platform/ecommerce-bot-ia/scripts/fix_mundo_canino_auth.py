import requests
import time

def fix_mundo_canino_auth():
    print("=== FIXING MUNDO CANINO AUTHENTICATION ===")
    
    # Test fresh login multiple times to ensure it works
    for attempt in range(3):
        print(f"\nAttempt {attempt + 1}:")
        
        login_response = requests.post('http://localhost:8002/auth/login', json={
            'email': 'admin@mundocanino.com',
            'password': 'canino123'
        })
        
        print(f"Login status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            auth_data = login_response.json()
            token = auth_data['access_token']
            
            print(f"Token generated: {token[:20]}...")
            print(f"Client: {auth_data['client']['name']}")
            
            # Test immediate product access
            headers = {'Authorization': f'Bearer {token}'}
            products_response = requests.get('http://localhost:8002/api/products', headers=headers)
            
            print(f"Products access: {products_response.status_code}")
            
            if products_response.status_code == 200:
                products = products_response.json()
                print(f"Products count: {len(products)}")
                if products:
                    print(f"First product: {products[0].get('name')}")
                    print("✅ AUTHENTICATION WORKING!")
                    break
            elif products_response.status_code == 403:
                print("❌ 403 Forbidden - Authentication issue")
            else:
                print(f"❌ Unexpected status: {products_response.status_code}")
        else:
            print(f"❌ Login failed: {login_response.text}")
        
        time.sleep(1)
    
    print("\n=== INSTRUCTIONS FOR FRONTEND ACCESS ===")
    print("1. Open browser in INCOGNITO mode")
    print("2. Go to: http://localhost:3000")
    print("3. Login with: admin@mundocanino.com / canino123")
    print("4. If still no products, check browser console for errors (F12)")
    print("5. Try hard refresh: Ctrl+Shift+R")
    
    print("\n=== TESTING ALL ACCOUNTS FOR COMPARISON ===")
    
    accounts = [
        ("Demo Company", "admin@demo.com", "demo123"),
        ("Test Store", "admin@teststore.com", "test123"),
        ("Mundo Canino", "admin@mundocanino.com", "canino123"),
        ("Green House", "admin@greenhouse.com", "green123")
    ]
    
    for name, email, password in accounts:
        login_resp = requests.post('http://localhost:8002/auth/login', json={
            'email': email, 
            'password': password
        })
        
        if login_resp.status_code == 200:
            token = login_resp.json()['access_token']
            headers = {'Authorization': f'Bearer {token}'}
            
            products_resp = requests.get('http://localhost:8002/api/products', headers=headers)
            
            if products_resp.status_code == 200:
                count = len(products_resp.json())
                print(f"✅ {name}: {count} products")
            else:
                print(f"❌ {name}: {products_resp.status_code} error")
        else:
            print(f"❌ {name}: Login failed")

if __name__ == "__main__":
    fix_mundo_canino_auth()