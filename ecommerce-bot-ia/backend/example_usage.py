"""
Example usage of the tenant middleware in application code
"""
from fastapi import APIRouter, HTTPException
from app.middleware.tenant import get_tenant_id, set_tenant_id

# Example router showing how to use tenant middleware
example_router = APIRouter()

@example_router.get("/orders")
async def get_tenant_orders():
    """Example endpoint that uses tenant_id from middleware."""
    try:
        # Get current tenant_id from request context
        tenant_id = get_tenant_id()
        
        # Use tenant_id in your business logic
        # For example, filter database queries by tenant
        # orders = db.query(Order).filter_by(tenant_id=tenant_id).all()
        
        return {
            "tenant_id": tenant_id,
            "message": f"Retrieved orders for tenant {tenant_id}",
            "orders": []  # Your actual order data here
        }
        
    except HTTPException as e:
        # Tenant not resolved
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@example_router.post("/webhook")
async def webhook_handler():
    """Example webhook that manually sets tenant_id."""
    try:
        # In webhooks, you might need to determine tenant_id from payload
        # and set it manually since there's no Host/Header context
        webhook_tenant_id = "12345678-1234-1234-1234-123456789abc"
        
        # Manually set tenant for this request
        set_tenant_id(webhook_tenant_id)
        
        # Now any code that calls get_tenant_id() will get the correct value
        current_tenant = get_tenant_id()
        
        return {
            "tenant_id": current_tenant,
            "message": "Webhook processed successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Example service function
async def process_order_for_current_tenant(order_data: dict):
    """Example service function that uses current tenant context."""
    # Get tenant_id from current request context
    tenant_id = get_tenant_id()
    
    # Add tenant_id to order data
    order_data['tenant_id'] = tenant_id
    
    # Process order with tenant isolation
    # save_order_to_database(order_data)
    
    return {
        "order": order_data,
        "processed_for_tenant": tenant_id
    }


# Example database query helper
def get_filtered_query_for_current_tenant(base_query):
    """Helper to add tenant filtering to database queries."""
    tenant_id = get_tenant_id()
    return base_query.filter_by(tenant_id=tenant_id)

# Usage example:
# orders_query = db.query(Order)
# tenant_orders_query = get_filtered_query_for_current_tenant(orders_query)
# orders = tenant_orders_query.all()