import pytest
import requests
import json
from typing import Dict, Any

# Test configuration
BASE_URL = "http://localhost:8002"
TEST_CLIENTS = [
    {"name": "Test Company A", "slug": "test-company-a"},
    {"name": "Test Company B", "slug": "test-company-b"}
]
TEST_USERS = [
    {"email": "admin@company-a.com", "password": "test123", "client_slug": "test-company-a"},
    {"email": "admin@company-b.com", "password": "test123", "client_slug": "test-company-b"}
]

class TestAuth:
    def test_register_with_new_client(self):
        """Test registering a user with a new client."""
        client_data = TEST_CLIENTS[0]
        user_data = {
            "email": "owner@company-a.com",
            "password": "test123",
            "client_name": client_data["name"]
        }
        
        response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "access_token" in data
        assert "refresh_token" in data
        assert "user" in data
        assert "client" in data
        
        # Verify user data
        assert data["user"]["email"] == user_data["email"]
        assert data["user"]["role"] == "owner"  # Should be owner since they created the client
        
        # Verify client data
        assert data["client"]["name"] == client_data["name"]
        assert data["client"]["slug"] == client_data["slug"]
        
        return data
    
    def test_register_with_existing_client(self):
        """Test registering a user with an existing client."""
        # First register with a new client to ensure it exists
        self.test_register_with_new_client()
        
        # Now register a new user with the existing client
        user_data = {
            "email": "user@company-a.com",
            "password": "test123",
            "client_slug": "test-company-a"
        }
        
        response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify user data
        assert data["user"]["email"] == user_data["email"]
        assert data["user"]["role"] == "user"  # Should be user since they didn't create the client
        
        # Verify same client
        assert data["client"]["slug"] == "test-company-a"
    
    def test_login(self):
        """Test user login."""
        # First register a user
        auth_data = self.test_register_with_new_client()
        
        # Now login
        login_data = {
            "email": "owner@company-a.com",
            "password": "test123",
            "client_slug": "test-company-a"
        }
        
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "access_token" in data
        assert data["user"]["email"] == login_data["email"]
        
        return data
    
    def test_refresh_token(self):
        """Test token refresh."""
        auth_data = self.test_register_with_new_client()
        
        refresh_data = {"refresh_token": auth_data["refresh_token"]}
        response = requests.post(f"{BASE_URL}/auth/refresh", json=refresh_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_get_me(self):
        """Test getting current user info."""
        auth_data = self.test_register_with_new_client()
        
        headers = {"Authorization": f"Bearer {auth_data['access_token']}"}
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "user" in data
        assert "client" in data
        assert data["user"]["email"] == "owner@company-a.com"

class TestTenantIsolation:
    def setup_method(self):
        """Setup test data for tenant isolation tests."""
        self.auth_tokens = {}
        
        # Register users for both companies
        for i, client_data in enumerate(TEST_CLIENTS):
            user_data = {
                "email": f"owner@{client_data['slug'].replace('-', '')}.com",
                "password": "test123",
                "client_name": client_data["name"]
            }
            
            response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
            assert response.status_code == 200
            
            auth_data = response.json()
            self.auth_tokens[client_data["slug"]] = auth_data["access_token"]
    
    def test_create_orders_per_tenant(self):
        """Test creating orders for different tenants."""
        orders_created = {}
        
        for slug, token in self.auth_tokens.items():
            headers = {"Authorization": f"Bearer {token}"}
            
            # Create order for this tenant
            order_data = {
                "code": f"ORD-{slug}-001",
                "customer_name": f"Customer from {slug}",
                "total": "1000.00",
                "status": "pending"
            }
            
            response = requests.post(
                f"{BASE_URL}/api/tenant-orders/",
                json=order_data,
                headers=headers
            )
            
            assert response.status_code == 200
            created_order = response.json()
            
            assert created_order["code"] == order_data["code"]
            assert created_order["customer_name"] == order_data["customer_name"]
            
            orders_created[slug] = created_order
        
        return orders_created
    
    def test_tenant_isolation_orders(self):
        """Test that tenants can only see their own orders."""
        # First create orders for both tenants
        self.test_create_orders_per_tenant()
        
        for slug, token in self.auth_tokens.items():
            headers = {"Authorization": f"Bearer {token}"}
            
            # Get orders for this tenant
            response = requests.get(f"{BASE_URL}/api/tenant-orders/", headers=headers)
            assert response.status_code == 200
            
            orders = response.json()
            
            # Should only see orders from this tenant
            for order in orders:
                assert order["code"].startswith(f"ORD-{slug}")
            
            # Should have at least one order (the one we created)
            assert len(orders) >= 1
    
    def test_cross_tenant_access_denied(self):
        """Test that one tenant cannot access another tenant's orders."""
        orders_created = self.test_create_orders_per_tenant()
        
        # Try to access company-a's order using company-b's token
        company_a_order_id = None
        company_b_token = None
        
        for slug, token in self.auth_tokens.items():
            if slug == "test-company-a":
                headers = {"Authorization": f"Bearer {token}"}
                response = requests.get(f"{BASE_URL}/api/tenant-orders/", headers=headers)
                orders = response.json()
                if orders:
                    company_a_order_id = orders[0]["id"]
            elif slug == "test-company-b":
                company_b_token = token
        
        if company_a_order_id and company_b_token:
            # Try to access company-a's order with company-b's token
            headers = {"Authorization": f"Bearer {company_b_token}"}
            response = requests.get(
                f"{BASE_URL}/api/tenant-orders/{company_a_order_id}",
                headers=headers
            )
            
            # Should return 404 (not found) because it doesn't exist in company-b's scope
            assert response.status_code == 404
    
    def test_unique_constraint_per_tenant(self):
        """Test that order codes are unique per tenant, but can be duplicated across tenants."""
        # Create order with same code for both tenants
        for slug, token in self.auth_tokens.items():
            headers = {"Authorization": f"Bearer {token}"}
            
            order_data = {
                "code": "DUPLICATE-CODE-001",
                "customer_name": f"Customer from {slug}",
                "total": "500.00",
                "status": "pending"
            }
            
            response = requests.post(
                f"{BASE_URL}/api/tenant-orders/",
                json=order_data,
                headers=headers
            )
            
            # Should succeed for both tenants
            assert response.status_code == 200
        
        # Now try to create duplicate within the same tenant
        first_token = list(self.auth_tokens.values())[0]
        headers = {"Authorization": f"Bearer {first_token}"}
        
        duplicate_order = {
            "code": "DUPLICATE-CODE-001",
            "customer_name": "Another customer",
            "total": "300.00",
            "status": "pending"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/tenant-orders/",
            json=duplicate_order,
            headers=headers
        )
        
        # Should fail with 400 because code already exists for this tenant
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

def run_tests():
    """Run all tests manually."""
    print("[TESTS] Starting Multi-Tenant Authentication Tests...")
    
    # Auth tests
    print("\n[AUTH] Testing Authentication...")
    auth_tests = TestAuth()
    
    try:
        print("  [OK] Register with new client")
        auth_tests.test_register_with_new_client()
        
        print("  [OK] Register with existing client")
        auth_tests.test_register_with_existing_client()
        
        print("  [OK] Login")
        auth_tests.test_login()
        
        print("  [OK] Refresh token")
        auth_tests.test_refresh_token()
        
        print("  [OK] Get current user info")
        auth_tests.test_get_me()
        
    except Exception as e:
        print(f"  [ERROR] Auth test failed: {e}")
        return False
    
    # Tenant isolation tests
    print("\n[ISOLATION] Testing Tenant Isolation...")
    isolation_tests = TestTenantIsolation()
    
    try:
        isolation_tests.setup_method()
        
        print("  [OK] Create orders per tenant")
        isolation_tests.test_create_orders_per_tenant()
        
        print("  [OK] Tenant isolation (orders)")
        isolation_tests.test_tenant_isolation_orders()
        
        print("  [OK] Cross-tenant access denied")
        isolation_tests.test_cross_tenant_access_denied()
        
        print("  [OK] Unique constraint per tenant")
        isolation_tests.test_unique_constraint_per_tenant()
        
    except Exception as e:
        print(f"  [ERROR] Tenant isolation test failed: {e}")
        return False
    
    print("\n[SUCCESS] All tests passed!")
    return True

if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)