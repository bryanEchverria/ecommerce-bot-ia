import requests
import json

BASE_URL = "http://localhost:8002"

def create_demo_data():
    """Create demo data for multi-tenant system."""
    print("[SEED] Creating demo data for multi-tenant system...")
    
    # Demo clients and users
    demo_data = [
        {
            "client_name": "Demo Company",
            "client_slug": "demo",
            "users": [
                {"email": "admin@demo.com", "password": "demo123", "role": "owner"},
                {"email": "user@demo.com", "password": "demo123", "role": "user"}
            ],
            "orders": [
                {"code": "ORD-DEMO-001", "customer_name": "Juan Pérez", "total": "15000.00", "status": "pending"},
                {"code": "ORD-DEMO-002", "customer_name": "María García", "total": "25000.00", "status": "confirmed"},
                {"code": "ORD-DEMO-003", "customer_name": "Carlos López", "total": "8500.00", "status": "shipped"},
            ]
        },
        {
            "client_name": "Test Store",
            "client_slug": "test-store",
            "users": [
                {"email": "admin@teststore.com", "password": "test123", "role": "owner"},
            ],
            "orders": [
                {"code": "TST-001", "customer_name": "Ana Rodríguez", "total": "12000.00", "status": "pending"},
                {"code": "TST-002", "customer_name": "Luis Martínez", "total": "18500.00", "status": "delivered"},
            ]
        }
    ]
    
    created_tokens = {}
    
    for company_data in demo_data:
        print(f"\n[COMPANY] Creating company: {company_data['client_name']}")
        
        # Create owner user (which creates the company)
        owner_data = company_data["users"][0]
        register_data = {
            "email": owner_data["email"],
            "password": owner_data["password"],
            "client_name": company_data["client_name"]
        }
        
        try:
            response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
            if response.status_code == 200:
                auth_data = response.json()
                created_tokens[company_data["client_slug"]] = auth_data["access_token"]
                print(f"  [OK] Created owner: {owner_data['email']}")
            else:
                print(f"  [ERROR] Failed to create owner: {response.text}")
                continue
        except Exception as e:
            print(f"  [ERROR] Error creating owner: {e}")
            continue
        
        # Create additional users
        for user_data in company_data["users"][1:]:
            user_register_data = {
                "email": user_data["email"],
                "password": user_data["password"],
                "client_slug": company_data["client_slug"]
            }
            
            try:
                response = requests.post(f"{BASE_URL}/auth/register", json=user_register_data)
                if response.status_code == 200:
                    print(f"  [OK] Created user: {user_data['email']}")
                else:
                    print(f"  [ERROR] Failed to create user: {response.text}")
            except Exception as e:
                print(f"  [ERROR] Error creating user: {e}")
        
        # Create orders for this company
        token = created_tokens.get(company_data["client_slug"])
        if token:
            headers = {"Authorization": f"Bearer {token}"}
            
            for order_data in company_data["orders"]:
                try:
                    response = requests.post(
                        f"{BASE_URL}/api/tenant-orders/",
                        json=order_data,
                        headers=headers
                    )
                    if response.status_code == 200:
                        print(f"  [OK] Created order: {order_data['code']}")
                    else:
                        print(f"  [ERROR] Failed to create order: {response.text}")
                except Exception as e:
                    print(f"  [ERROR] Error creating order: {e}")
    
    print("\n[CREDENTIALS] Demo credentials:")
    print("=" * 50)
    for company_data in demo_data:
        print(f"\n[COMPANY] {company_data['client_name']} ({company_data['client_slug']})")
        for user_data in company_data["users"]:
            print(f"  Email: {user_data['email']} | Password: {user_data['password']} | Role: {user_data['role']}")
    
    print(f"\n[ACCESS] Access the application at: http://localhost:3000")
    print("[INFO] Use any of the credentials above to login")

if __name__ == "__main__":
    create_demo_data()