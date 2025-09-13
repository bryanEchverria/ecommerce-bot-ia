#!/usr/bin/env bash
set -euo pipefail

# Extended Flow multi-tenant test
API="http://localhost:8002"

ok(){ printf "\033[32m✅ %s\033[0m\n" "$*"; }
warn(){ printf "\033[33m⚠️  %s\033[0m\n" "$*"; }
err(){ printf "\033[31m❌ %s\033[0m\n" "$*"; }
line(){ printf "\n\033[36m═══ %s ═══\033[0m\n" "$*"; }

line "FLOW MULTI-TENANT EXTENDED TEST"

# Test 1: Verify tenant isolation in /flow/orders
line "TEST 1: Tenant Isolation Verification"

echo "🔍 Testing ACME tenant (should see 2 orders)"
acme_orders=$(curl -s -H "Host: acme.sintestesia.cl" "$API/flow/orders")
echo "$acme_orders" | jq '.'
acme_count=$(echo "$acme_orders" | jq '.pedidos | length')
acme_tenant_ids=$(echo "$acme_orders" | jq -r '.pedidos[].tenant_id' | sort -u | wc -l)

echo "🔍 Testing BRAVO tenant (should see 1 order)"
bravo_orders=$(curl -s -H "Host: bravo.sintestesia.cl" "$API/flow/orders")  
echo "$bravo_orders" | jq '.'
bravo_count=$(echo "$bravo_orders" | jq '.pedidos | length')
bravo_tenant_ids=$(echo "$bravo_orders" | jq -r '.pedidos[].tenant_id' | sort -u | wc -l)

# Verify isolation
if [[ "$acme_count" == "2" && "$acme_tenant_ids" == "1" ]]; then
    ok "ACME isolation: $acme_count orders, $acme_tenant_ids unique tenant_id"
else
    err "ACME isolation failed: $acme_count orders, $acme_tenant_ids tenant_ids"
fi

if [[ "$bravo_count" == "1" && "$bravo_tenant_ids" == "1" ]]; then
    ok "BRAVO isolation: $bravo_count orders, $bravo_tenant_ids unique tenant_id"
else
    err "BRAVO isolation failed: $bravo_count orders, $bravo_tenant_ids tenant_ids"
fi

# Test 2: Stats verification
line "TEST 2: Stats Isolation"

echo "🔍 ACME stats"
acme_stats=$(curl -s -H "Host: acme.sintestesia.cl" "$API/flow/stats")
echo "$acme_stats" | jq '.'
acme_total=$(echo "$acme_stats" | jq '.total_pedidos')
acme_pagados=$(echo "$acme_stats" | jq '.pedidos_pagados')

echo "🔍 BRAVO stats" 
bravo_stats=$(curl -s -H "Host: bravo.sintestesia.cl" "$API/flow/stats")
echo "$bravo_stats" | jq '.'
bravo_total=$(echo "$bravo_stats" | jq '.total_pedidos')
bravo_pagados=$(echo "$bravo_stats" | jq '.pedidos_pagados')

if [[ "$acme_total" == "2" && "$acme_pagados" == "1" ]]; then
    ok "ACME stats correct: $acme_total total, $acme_pagados paid"
else
    err "ACME stats wrong: $acme_total total, $acme_pagados paid"  
fi

if [[ "$bravo_total" == "1" && "$bravo_pagados" == "1" ]]; then
    ok "BRAVO stats correct: $bravo_total total, $bravo_pagados paid"
else
    err "BRAVO stats wrong: $bravo_total total, $bravo_pagados paid"
fi

# Test 3: Cross-tenant data leakage test
line "TEST 3: Cross-Tenant Data Leakage Test"

# Get ACME tenant ID from an order
acme_tenant_id=$(echo "$acme_orders" | jq -r '.pedidos[0].tenant_id')
bravo_tenant_id=$(echo "$bravo_orders" | jq -r '.pedidos[0].tenant_id')

echo "🔍 ACME tenant_id: $acme_tenant_id"
echo "🔍 BRAVO tenant_id: $bravo_tenant_id"

# Verify they are different
if [[ "$acme_tenant_id" != "$bravo_tenant_id" ]]; then
    ok "Tenant IDs are different (no cross-contamination)"
else
    err "Tenant IDs are the same! Data leakage detected!"
fi

# Test 4: Flow return endpoint (webhook simulation)
line "TEST 4: Flow Return Webhook Test"

acme_order_id=$(echo "$acme_orders" | jq -r '.pedidos[0].id')
bravo_order_id=$(echo "$bravo_orders" | jq -r '.pedidos[0].id')

echo "🔍 Testing /flow/return with ACME context (order $acme_order_id)"
acme_return=$(curl -s -H "Host: acme.sintestesia.cl" "$API/flow/return?status=SUCCESS&commerceOrder=$acme_order_id" | head -c 200)
echo "Response preview: $acme_return..."

echo "🔍 Testing /flow/return with BRAVO context (order $bravo_order_id)"  
bravo_return=$(curl -s -H "Host: bravo.sintestesia.cl" "$API/flow/return?status=SUCCESS&commerceOrder=$bravo_order_id" | head -c 200)
echo "Response preview: $bravo_return..."

# Test 5: Direct API verification
line "TEST 5: Direct Database Verification"

echo "🔍 Checking database directly for verification"
docker exec ecommerce-postgres psql -U ecommerce_user -d ecommerce_multi_tenant -c "
SELECT 
    tenant_id, 
    COUNT(*) as orders, 
    COUNT(*) FILTER (WHERE estado = 'pagado') as paid_orders,
    SUM(total) FILTER (WHERE estado = 'pagado') as total_revenue
FROM flow_pedidos 
GROUP BY tenant_id 
ORDER BY tenant_id;"

line "SUMMARY"
echo "🎯 Multi-tenant Flow system test completed"
echo "📊 ACME tenant: $acme_count orders"  
echo "📊 BRAVO tenant: $bravo_count orders"
echo "🔒 Data isolation: $([ "$acme_tenant_id" != "$bravo_tenant_id" ] && echo "✅ VERIFIED" || echo "❌ FAILED")"
echo "📈 Stats isolation: $([ "$acme_total" != "$bravo_total" ] && echo "✅ VERIFIED" || echo "❌ FAILED")"