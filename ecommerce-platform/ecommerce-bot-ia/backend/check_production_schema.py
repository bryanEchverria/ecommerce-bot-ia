#!/usr/bin/env python3
"""
Check production database schema for tenant_id columns
"""
import requests
import json

PROD_API_URL = "https://api.sintestesia.cl"

def check_production_database():
    """Check production database schema via API endpoint"""
    print("[INFO] Checking production database schema...")
    
    try:
        # Try to get some data from flow tables to see structure
        endpoints_to_check = [
            "/api/flow-orders/",
            "/api/flow-sesiones/", 
            "/api/whatsapp-settings/",
            "/health",
            "/docs"
        ]
        
        for endpoint in endpoints_to_check:
            try:
                url = f"{PROD_API_URL}{endpoint}"
                print(f"\n[INFO] Checking: {url}")
                
                response = requests.get(url, timeout=10)
                print(f"  Status: {response.status_code}")
                
                if response.status_code == 200:
                    print(f"  ✅ {endpoint} is accessible")
                    
                    # Try to get some data if it's a data endpoint
                    if "flow" in endpoint:
                        try:
                            data = response.json()
                            if isinstance(data, list) and len(data) > 0:
                                # Check if first item has tenant_id
                                first_item = data[0]
                                if 'tenant_id' in first_item:
                                    print(f"    ✅ tenant_id found in {endpoint}")
                                    print(f"    Sample tenant_id: {first_item.get('tenant_id')}")
                                else:
                                    print(f"    ❌ tenant_id NOT found in {endpoint}")
                                    print(f"    Available fields: {list(first_item.keys())}")
                            else:
                                print(f"    ℹ️  No data returned from {endpoint}")
                        except Exception as e:
                            print(f"    ⚠️  Could not parse JSON: {e}")
                            
                elif response.status_code == 401:
                    print(f"  🔒 {endpoint} requires authentication")
                elif response.status_code == 404:
                    print(f"  ❌ {endpoint} not found")
                else:
                    print(f"  ⚠️  Unexpected status: {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                print(f"  ❌ Error accessing {endpoint}: {e}")
    
    except Exception as e:
        print(f"[ERROR] Production check failed: {e}")
        return False
    
    return True

def check_api_structure():
    """Check API structure to understand database schema"""
    print(f"\n[INFO] Checking API documentation...")
    
    try:
        # Check OpenAPI docs
        response = requests.get(f"{PROD_API_URL}/openapi.json", timeout=10)
        if response.status_code == 200:
            openapi = response.json()
            
            # Look for models/schemas that mention tenant_id
            schemas = openapi.get("components", {}).get("schemas", {})
            
            print(f"  Found {len(schemas)} API schemas")
            
            tenant_related_schemas = []
            for schema_name, schema_def in schemas.items():
                if "flow" in schema_name.lower() or "session" in schema_name.lower():
                    properties = schema_def.get("properties", {})
                    if "tenant_id" in properties:
                        tenant_related_schemas.append(schema_name)
                        print(f"    ✅ {schema_name} has tenant_id")
                    else:
                        print(f"    ❌ {schema_name} missing tenant_id")
                        print(f"        Properties: {list(properties.keys())}")
            
            if tenant_related_schemas:
                print(f"  ✅ Found {len(tenant_related_schemas)} schemas with tenant_id")
            else:
                print(f"  ❌ No schemas found with tenant_id")
                
        else:
            print(f"  ⚠️  Could not access OpenAPI docs: {response.status_code}")
            
    except Exception as e:
        print(f"  ⚠️  Error checking API docs: {e}")

def main():
    print("="*60)
    print("PRODUCTION DATABASE SCHEMA VERIFICATION")
    print("="*60)
    
    # Basic connectivity check
    print(f"[INFO] Production API: {PROD_API_URL}")
    
    try:
        response = requests.get(f"{PROD_API_URL}/health", timeout=10)
        if response.status_code == 200:
            print(f"✅ Production API is online")
        else:
            print(f"⚠️  Production API returned: {response.status_code}")
    except Exception as e:
        print(f"❌ Cannot reach production API: {e}")
        return
    
    # Check database schema
    check_production_database()
    
    # Check API structure
    check_api_structure()
    
    print(f"\n" + "="*60)
    print("RECOMMENDATIONS:")
    print("="*60)
    print("1. If tenant_id columns are missing in production, migration is needed")
    print("2. Check production logs for any tenant_id related errors")
    print("3. Backup production database before applying migration")
    print("4. Test migration on production staging environment first")
    print("5. Apply migration during low-traffic maintenance window")

if __name__ == "__main__":
    main()