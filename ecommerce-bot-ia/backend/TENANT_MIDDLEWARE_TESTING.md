# Multi-Tenant Middleware - Testing Guide

## 📋 Overview

The multi-tenant middleware resolves `tenant_id` from each request using the following order:
1. **X-Tenant-Id header** (direct, use as-is)
2. **Subdomain resolution** (extract from Host header, map via `tenant_clients` table)

## 🧪 Testing Setup

### Prerequisites
1. Backend server running on port 8002
2. Test tenant created in database:
   - **ID:** `12345678-1234-1234-1234-123456789abc`
   - **Slug:** `acme`
   - **Name:** `Acme Corporation`

### Test Data Verification
```bash
# Check if test tenant exists
docker exec ecommerce-postgres psql -U postgres -d ecommerce -c "SELECT id, name, slug FROM tenant_clients WHERE slug = 'acme';"
```

## 🚀 Test Commands

### 1. Test with X-Tenant-Id Header

```bash
# Test with direct tenant_id header
curl -H "X-Tenant-Id: 12345678-1234-1234-1234-123456789abc" \
     -H "Content-Type: application/json" \
     http://localhost:8002/__debug/tenant

# Expected response:
# {
#   "tenant_id": "12345678-1234-1234-1234-123456789abc",
#   "resolved": true,
#   "message": "Tenant successfully resolved"
# }
```

### 2. Test with Subdomain Resolution

```bash
# Test with subdomain (acme.localhost -> maps to tenant ID)
curl -H "Host: acme.localhost" \
     -H "Content-Type: application/json" \
     http://localhost:8002/__debug/tenant

# Expected response:
# {
#   "tenant_id": "12345678-1234-1234-1234-123456789abc",
#   "resolved": true,
#   "message": "Tenant successfully resolved"
# }
```

### 3. Test with Invalid/Missing Tenant

```bash
# Test with invalid subdomain
curl -H "Host: nonexistent.localhost" \
     -H "Content-Type: application/json" \
     http://localhost:8002/__debug/tenant

# Expected response (HTTP 400):
# {
#   "detail": "Tenant no resuelto"
# }
```

```bash
# Test with no tenant information
curl -H "Content-Type: application/json" \
     http://localhost:8002/__debug/tenant

# Expected response (HTTP 400):
# {
#   "detail": "Tenant no resuelto"
# }
```

### 4. Test Cache Functionality

```bash
# View cache statistics
curl http://localhost:8002/__debug/tenant/cache

# Expected response:
# {
#   "cache_stats": {
#     "total_entries": 1,
#     "expired_entries": 0,
#     "active_entries": 1,
#     "cache_ttl": 60
#   },
#   "message": "Cache statistics retrieved"
# }
```

```bash
# Clear cache
curl -X POST http://localhost:8002/__debug/tenant/cache/clear

# Expected response:
# {
#   "message": "Tenant cache cleared successfully"
# }
```

### 5. Test Precedence (Header over Subdomain)

```bash
# Test that X-Tenant-Id header takes precedence over subdomain
curl -H "X-Tenant-Id: 00000000-0000-0000-0000-000000000001" \
     -H "Host: acme.localhost" \
     -H "Content-Type: application/json" \
     http://localhost:8002/__debug/tenant

# Expected response (should use header value):
# {
#   "tenant_id": "00000000-0000-0000-0000-000000000001",
#   "resolved": true,
#   "message": "Tenant successfully resolved"
# }
```

## 🔧 Advanced Testing

### Test with Production-like Domains

```bash
# Simulate production subdomain
curl -H "Host: acme.yourdomain.com" \
     -H "Content-Type: application/json" \
     http://localhost:8002/__debug/tenant
```

### Test Cache Expiration

```bash
# 1. Make request to cache subdomain
curl -H "Host: acme.localhost" http://localhost:8002/__debug/tenant

# 2. Check cache stats
curl http://localhost:8002/__debug/tenant/cache

# 3. Wait 61 seconds (TTL is 60s), then check again
sleep 61
curl http://localhost:8002/__debug/tenant/cache
```

## 📊 Expected Behaviors

### ✅ Success Cases
- **Header resolution:** Direct UUID provided via `X-Tenant-Id`
- **Subdomain resolution:** Valid slug maps to tenant ID
- **Caching:** Repeated requests for same subdomain use cache
- **Precedence:** Header takes precedence over subdomain

### ❌ Error Cases (HTTP 400)
- **No tenant info:** Neither header nor valid subdomain
- **Invalid subdomain:** Subdomain not found in `tenant_clients`
- **Empty header:** `X-Tenant-Id` header present but empty

## 🐛 Troubleshooting

### Check Logs
```bash
# Watch backend logs for middleware activity
docker logs -f ecommerce-backend
```

### Database Issues
```bash
# Verify tenant_clients table exists and has data
docker exec ecommerce-postgres psql -U postgres -d ecommerce -c "\\dt tenant_clients"
docker exec ecommerce-postgres psql -U postgres -d ecommerce -c "SELECT * FROM tenant_clients LIMIT 5;"
```

### Clear All Cache
```bash
curl -X POST http://localhost:8002/__debug/tenant/cache/clear
```

## 🔑 Integration Usage

### In Your Router/Service Code

```python
from app.middleware.tenant import get_tenant_id

@router.get("/my-endpoint")
async def my_endpoint():
    tenant_id = get_tenant_id()  # Gets current request's tenant_id
    # Your logic here...
    return {"tenant_id": tenant_id}
```

### Manual Tenant Setting (for Webhooks)

```python
from app.middleware.tenant import set_tenant_id

@router.post("/webhook")
async def webhook_handler():
    # Manually set tenant for webhook processing
    set_tenant_id("12345678-1234-1234-1234-123456789abc")
    # Process webhook...
```

## 🚨 Production Notes

1. **Remove debug endpoints** in production
2. **Monitor cache performance** and adjust TTL if needed
3. **Set up proper DNS** for subdomain routing
4. **Use HTTPS** for production domains
5. **Log tenant resolution** for debugging

---

🎯 **Quick Verification:**
```bash
# Single command to test everything works:
curl -H "X-Tenant-Id: 12345678-1234-1234-1234-123456789abc" http://localhost:8002/__debug/tenant && echo ""
```