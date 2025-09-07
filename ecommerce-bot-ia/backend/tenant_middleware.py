"""
Multi-tenant middleware for FastAPI with tenant resolution and global context.
"""
import asyncio
import time
from contextvars import ContextVar
from typing import Optional, Dict, Any
from urllib.parse import urlparse

from fastapi import HTTPException, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text

from database import SessionLocal

# Global context variable for tenant_id per request
_tenant_context: ContextVar[Optional[str]] = ContextVar('tenant_id', default=None)

# Simple in-memory cache with TTL for slug->tenant_id mapping
_slug_cache: Dict[str, Dict[str, Any]] = {}
_cache_ttl = 60  # seconds


class TenantMiddleware(BaseHTTPMiddleware):
    """
    Middleware that resolves tenant_id from request and makes it available globally.
    
    Resolution order:
    1. X-Tenant-Id header (use as-is)
    2. Subdomain extraction from Host header, mapped via tenant_clients table
    
    If no tenant can be resolved, returns 400 error (except for bypass paths).
    """
    
    # Paths that don't require tenant resolution
    BYPASS_PATHS = [
        "/",
        "/health",
        "/__debug/health",
        "/docs",
        "/openapi.json",
        "/redoc"
    ]
    
    # Path prefixes that don't require tenant resolution
    BYPASS_PREFIXES = [
        "/auth/",
        "/static/",
        "/twilio/"
    ]

    async def dispatch(self, request: Request, call_next) -> Response:
        """Process request and resolve tenant_id."""
        try:
            # Check if this path should bypass tenant resolution
            if self._should_bypass_tenant_resolution(request.url.path):
                # Process request without tenant resolution
                response = await call_next(request)
                return response
            
            tenant_id = await self._resolve_tenant_id(request)
            
            if not tenant_id:
                raise HTTPException(
                    status_code=400,
                    detail="Tenant no resuelto"
                )
            
            # Set tenant_id in context
            _tenant_context.set(tenant_id)
            
            # Process request
            response = await call_next(request)
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Error resolviendo tenant: {str(e)}"
            )
        finally:
            # Clear context after request
            _tenant_context.set(None)

    def _should_bypass_tenant_resolution(self, path: str) -> bool:
        """
        Check if a path should bypass tenant resolution.
        
        Args:
            path: Request path
            
        Returns:
            True if path should bypass tenant resolution
        """
        # Exact match for bypass paths
        if path in self.BYPASS_PATHS:
            return True
        
        # Check bypass prefixes
        if any(path.startswith(prefix) for prefix in self.BYPASS_PREFIXES):
            return True
        
        # Allow specific debug endpoints (not tenant-related ones)
        if path in ["/__debug/health", "/__debug/tenant/cache", "/__debug/tenant/cache/clear"]:
            return True
            
        # Allow static assets
        if path.endswith(('.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.ico', '.svg', '.woff', '.woff2', '.ttf', '.eot')):
            return True
            
        return False

    async def _resolve_tenant_id(self, request: Request) -> Optional[str]:
        """
        Resolve tenant_id using the configured resolution order.
        
        Args:
            request: FastAPI request object
            
        Returns:
            Tenant ID string or None if not resolvable
        """
        # 1. Check X-Tenant-Id header first
        tenant_header = request.headers.get("X-Tenant-Id")
        if tenant_header:
            return tenant_header.strip()
        
        # 2. Extract subdomain from Host header
        host = request.headers.get("Host", "")
        if host:
            subdomain = self._extract_subdomain(host)
            if subdomain:
                tenant_id = await self._resolve_subdomain_to_tenant_id(subdomain)
                if tenant_id:
                    return tenant_id
        
        return None

    def _extract_subdomain(self, host: str) -> Optional[str]:
        """
        Extract subdomain from host header.
        
        Examples:
            acme.midominio.com -> "acme"
            localhost -> None
            acme.localhost -> "acme"
            
        Args:
            host: Host header value
            
        Returns:
            Subdomain or None
        """
        try:
            # Remove port if present
            host_clean = host.split(':')[0]
            
            # Split by dots
            parts = host_clean.split('.')
            
            # Need at least 2 parts for subdomain (subdomain.domain)
            if len(parts) >= 2:
                subdomain = parts[0]
                # Don't consider www as subdomain
                if subdomain.lower() != 'www':
                    return subdomain
                    
            return None
        except Exception:
            return None

    async def _resolve_subdomain_to_tenant_id(self, subdomain: str) -> Optional[str]:
        """
        Resolve subdomain to tenant_id using tenant_clients table with caching.
        
        Args:
            subdomain: Subdomain string to resolve
            
        Returns:
            Tenant ID or None if not found
        """
        # Check cache first
        cache_key = f"subdomain:{subdomain}"
        cached = self._get_cached_value(cache_key)
        if cached is not None:
            return cached

        # Query database
        tenant_id = await self._query_tenant_by_slug(subdomain)
        
        # Cache result (even if None, to avoid repeated DB calls)
        self._set_cached_value(cache_key, tenant_id)
        
        return tenant_id

    async def _query_tenant_by_slug(self, slug: str) -> Optional[str]:
        """
        Query tenant_clients table for tenant_id by slug.
        
        Args:
            slug: Slug to search for
            
        Returns:
            Tenant ID or None if not found
        """
        try:
            with SessionLocal() as db:
                # Use raw SQL to avoid model dependencies
                result = db.execute(
                    text("SELECT id FROM tenant_clients WHERE slug = :slug LIMIT 1"),
                    {"slug": slug}
                )
                row = result.fetchone()
                return row[0] if row else None
                
        except Exception as e:
            # Log error but don't break request processing
            print(f"Error querying tenant by slug '{slug}': {e}")
            return None

    def _get_cached_value(self, key: str) -> Optional[str]:
        """Get value from cache if not expired."""
        if key not in _slug_cache:
            return None
            
        entry = _slug_cache[key]
        if time.time() - entry['timestamp'] > _cache_ttl:
            # Expired, remove from cache
            del _slug_cache[key]
            return None
            
        return entry['value']

    def _set_cached_value(self, key: str, value: Optional[str]) -> None:
        """Set value in cache with current timestamp."""
        _slug_cache[key] = {
            'value': value,
            'timestamp': time.time()
        }


def get_tenant_id() -> str:
    """
    Get current tenant_id from request context.
    
    Returns:
        Current tenant_id
        
    Raises:
        HTTPException: If no tenant_id is set in context
    """
    tenant_id = _tenant_context.get()
    print(f"DEBUG get_tenant_id: context value = {tenant_id}")  # DEBUG
    if not tenant_id:
        print("DEBUG get_tenant_id: No tenant_id in context!")  # DEBUG
        raise HTTPException(
            status_code=400,
            detail="Tenant no resuelto"
        )
    return tenant_id


def set_tenant_id(tenant_id: str) -> None:
    """
    Manually set tenant_id in context (useful for webhooks).
    
    Args:
        tenant_id: Tenant ID to set
    """
    _tenant_context.set(tenant_id)


def clear_tenant_cache() -> None:
    """Clear the slug->tenant_id cache (useful for testing)."""
    global _slug_cache
    _slug_cache.clear()


def get_cache_stats() -> Dict[str, Any]:
    """Get cache statistics (useful for debugging)."""
    current_time = time.time()
    total_entries = len(_slug_cache)
    expired_entries = sum(
        1 for entry in _slug_cache.values()
        if current_time - entry['timestamp'] > _cache_ttl
    )
    
    return {
        'total_entries': total_entries,
        'expired_entries': expired_entries,
        'active_entries': total_entries - expired_entries,
        'cache_ttl': _cache_ttl
    }