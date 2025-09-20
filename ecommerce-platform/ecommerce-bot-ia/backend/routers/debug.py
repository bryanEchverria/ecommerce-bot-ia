"""
Debug router for testing and development.
"""
from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from tenant_middleware import get_tenant_id, get_cache_stats, clear_tenant_cache

router = APIRouter()


@router.get("/__debug/tenant")
async def debug_tenant() -> Dict[str, Any]:
    """
    Debug endpoint to test tenant resolution.
    
    Returns current tenant_id and debug information.
    
    Test with:
    - Header: curl -H "X-Tenant-Id: 00000000-0000-0000-0000-000000000001" http://localhost:8002/__debug/tenant
    - Subdomain: curl -H "Host: acme.localhost" http://localhost:8002/__debug/tenant
    """
    try:
        tenant_id = get_tenant_id()
        return {
            "tenant_id": tenant_id,
            "resolved": True,
            "message": "Tenant successfully resolved"
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting tenant: {str(e)}")


@router.get("/__debug/tenant/cache")
async def debug_tenant_cache() -> Dict[str, Any]:
    """
    Debug endpoint to view cache statistics.
    
    Returns cache statistics and current state.
    """
    try:
        stats = get_cache_stats()
        return {
            "cache_stats": stats,
            "message": "Cache statistics retrieved"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting cache stats: {str(e)}")


@router.post("/__debug/tenant/cache/clear")
async def debug_clear_tenant_cache() -> Dict[str, str]:
    """
    Debug endpoint to clear tenant cache.
    
    Useful for testing cache behavior.
    """
    try:
        clear_tenant_cache()
        return {
            "message": "Tenant cache cleared successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing cache: {str(e)}")


@router.get("/__debug/health")
async def debug_health() -> Dict[str, str]:
    """
    Simple health check endpoint.
    """
    return {
        "status": "healthy",
        "message": "Debug router is working"
    }