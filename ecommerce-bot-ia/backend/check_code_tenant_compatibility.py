#!/usr/bin/env python3
"""
Check if current code is compatible with tenant_id columns
"""
import os
import re

def check_file_tenant_usage(file_path):
    """Check if a file uses tenant_id appropriately"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Look for database queries without tenant_id filtering
        issues = []
        
        # Check for queries that might need tenant_id
        flow_queries = re.findall(r'query\([^)]*Flow[^)]*\)', content)
        for query in flow_queries:
            if 'tenant_id' not in query and 'filter' in query:
                issues.append(f"Potentially missing tenant_id filter: {query}")
        
        # Check for hardcoded client_ids
        hardcoded_clients = re.findall(r'"sintestesia"', content)
        if hardcoded_clients:
            issues.append(f"Found {len(hardcoded_clients)} hardcoded 'sintestesia' references")
        
        # Check for tenant_id usage
        tenant_usages = len(re.findall(r'tenant_id', content))
        
        return {
            'file': file_path,
            'tenant_usages': tenant_usages,
            'issues': issues,
            'flow_queries': len(flow_queries),
        }
        
    except Exception as e:
        return {
            'file': file_path,
            'error': str(e),
            'tenant_usages': 0,
            'issues': [],
            'flow_queries': 0,
        }

def main():
    print("=" * 60)
    print("CÓDIGO COMPATIBILITY CHECK - TENANT_ID")
    print("=" * 60)
    
    # Files to check
    files_to_check = [
        "/root/ecommerce-bot-ia/backend/models.py",
        "/root/ecommerce-bot-ia/backend/routers/flow_router.py", 
        "/root/ecommerce-bot-ia/backend/routers/flow_orders.py",
        "/root/ecommerce-bot-ia/backend/services/flow_chat_service.py",
        "/root/ecommerce-bot-ia/whatsapp-bot-fastapi/models.py",
        "/root/ecommerce-bot-ia/whatsapp-bot-fastapi/services/flow_chat_service.py",
    ]
    
    total_issues = 0
    total_tenant_usages = 0
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            result = check_file_tenant_usage(file_path)
            
            file_name = os.path.basename(result['file'])
            print(f"\n📁 {file_name}")
            print(f"   tenant_id usages: {result['tenant_usages']}")
            print(f"   flow queries: {result['flow_queries']}")
            
            if result.get('error'):
                print(f"   ❌ Error: {result['error']}")
            
            if result['issues']:
                print(f"   ⚠️  Issues found:")
                for issue in result['issues']:
                    print(f"      - {issue}")
                total_issues += len(result['issues'])
            else:
                print(f"   ✅ No issues found")
            
            total_tenant_usages += result['tenant_usages']
        else:
            print(f"\n📁 {os.path.basename(file_path)}")
            print(f"   ❌ File not found")
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total tenant_id usages: {total_tenant_usages}")
    print(f"Total issues found: {total_issues}")
    
    if total_tenant_usages > 0:
        print("✅ Code appears to have tenant_id support")
    else:
        print("❌ Code does not appear to have tenant_id support")
    
    if total_issues > 0:
        print("⚠️  Issues found that may need attention")
        print("\nRECOMMENDATIONS:")
        print("1. Review hardcoded 'sintestesia' references")
        print("2. Add tenant_id filtering to flow queries")
        print("3. Update models to include tenant_id constraints")
        print("4. Test multi-tenant isolation")
    else:
        print("✅ No obvious compatibility issues found")
    
    print("\n" + "=" * 60)
    print("PRODUCTION READINESS")
    print("=" * 60)
    
    if total_tenant_usages > 10 and total_issues < 5:
        print("🟢 READY - Code appears tenant-ready")
    elif total_tenant_usages > 0:
        print("🟡 CAUTION - Partial tenant support, review issues")
    else:
        print("🔴 NOT READY - No tenant support found")
    
    print("\nNext steps:")
    print("1. Apply database migration (if not already done)")
    print("2. Update any hardcoded tenant references") 
    print("3. Test all flow-related functionality")
    print("4. Deploy during maintenance window")

if __name__ == "__main__":
    main()