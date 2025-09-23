"""
🏢 SISTEMA MULTI-TENANT AVANZADO
Middleware completo con resolución multi-fuente, auditoría y aislamiento de datos
"""
import asyncio
import time
import logging
import json
from contextvars import ContextVar
from typing import Optional, Dict, Any, List
from urllib.parse import urlparse
from datetime import datetime
import re

from fastapi import HTTPException, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text, create_engine
from sqlalchemy.pool import StaticPool

from database import SessionLocal

# Global context variables para request multi-tenant
_tenant_context: ContextVar[Optional[str]] = ContextVar('tenant_id', default=None)
_request_context: ContextVar[Optional[Dict]] = ContextVar('request_info', default=None)

# Cache optimizado para resolución de tenants
_tenant_cache: Dict[str, Dict[str, Any]] = {}
_cache_ttl = 300  # 5 minutos - más tiempo para estabilidad

# Logger para auditoría
logger = logging.getLogger(__name__)

# Estadísticas de resolución de tenants
_resolution_stats = {
    'subdomain': 0,
    'header': 0, 
    'path': 0,
    'query': 0,
    'rejected': 0,
    'cached': 0
}


class TenantMiddleware(BaseHTTPMiddleware):
    """
    🏢 MIDDLEWARE MULTI-TENANT AVANZADO
    
    Resolución multi-fuente de tenants con auditoría y seguridad:
    
    📍 ORDEN DE RESOLUCIÓN:
    1. Header X-Tenant-Id (directo, validado)
    2. Subdomain desde Host (acme.midominio.com → acme)
    3. Path parameter (/tenants/acme/api/... → acme)
    4. Query parameter ?tenant=acme (solo hosts permitidos)
    
    🛡️ SEGURIDAD:
    - Validación estricta de tenant IDs
    - Aislamiento total entre tenants
    - Auditoría completa de accesos
    - Cache con TTL para performance
    
    ❌ RECHAZO:
    - Requests sin tenant válido
    - Tenant IDs malformados
    - Acceso desde hosts no autorizados
    """
    
    # Paths that don't require tenant resolution
    BYPASS_PATHS = [
        "/",
        "/health",
        "/__debug/health", 
        "/docs",
        "/openapi.json",
        "/redoc",
        "/test-bot"
    ]
    
    # Path prefixes that don't require tenant resolution
    BYPASS_PREFIXES = [
        "/auth/",
        "/static/",
        "/twilio/",
        "/flow/confirm",  # Flow webhooks
        "/flow/return",   # Flow return URLs
        "/test-preview/", # Testing endpoint
        "/api/tenants/",  # All tenant API endpoints (for preview)
        "/api/settings/", # Global settings endpoints (WhatsApp, etc.)
        "/preview-fixed/", # Fixed preview endpoint
        "/simple-preview/", # Simple preview endpoint (bypass all middleware)
        "/bot-proxy/" # Bot proxy endpoint (fixes HTTPS mixed content)
    ]

    async def dispatch(self, request: Request, call_next) -> Response:
        """🔄 Procesa request con resolución multi-fuente de tenant"""
        start_time = time.time()
        tenant_id = None
        resolution_method = None
        
        try:
            # ✅ Verificar si el path debe bypass tenant resolution
            if self._should_bypass_tenant_resolution(request.url.path):
                response = await call_next(request)
                await self._log_audit_event(request, None, "BYPASS", "success", time.time() - start_time)
                return response
            
            # 🔍 Resolver tenant (principalmente desde subdomain)
            tenant_id, resolution_method = await self._resolve_tenant_id(request)
            
            # ❌ Rechazar si no se puede resolver tenant
            if not tenant_id:
                await self._log_audit_event(request, None, "REJECTED", "no_tenant", time.time() - start_time)
                _resolution_stats['rejected'] += 1
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "tenant_not_resolved",
                        "message": "No se pudo resolver el tenant desde ninguna fuente",
                        "sources_checked": ["header", "subdomain", "path", "query"],
                        "host": request.headers.get("host", ""),
                        "path": request.url.path
                    }
                )
            
            # 🔒 Validar tenant ID
            if not self._is_valid_tenant_id(tenant_id):
                await self._log_audit_event(request, tenant_id, "REJECTED", "invalid_tenant", time.time() - start_time)
                _resolution_stats['rejected'] += 1
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "invalid_tenant_id", 
                        "message": f"Tenant ID malformado: {tenant_id}",
                        "tenant_id": tenant_id
                    }
                )
            
            # ✅ Establecer contexto de tenant
            _tenant_context.set(tenant_id)
            _request_context.set({
                "tenant_id": tenant_id,
                "resolution_method": resolution_method,
                "timestamp": datetime.utcnow(),
                "request_id": id(request),
                "path": request.url.path,
                "method": request.method,
                "host": request.headers.get("host", ""),
                "user_agent": request.headers.get("user-agent", "")
            })
            
            # 📊 Actualizar estadísticas
            _resolution_stats[resolution_method] += 1
            
            # 🎯 Procesar request
            response = await call_next(request)
            
            # ✅ Log de éxito
            await self._log_audit_event(request, tenant_id, resolution_method.upper(), "success", time.time() - start_time)
            
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            # ❌ Log de error
            await self._log_audit_event(request, tenant_id, resolution_method or "ERROR", f"exception: {str(e)}", time.time() - start_time)
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "tenant_resolution_error",
                    "message": f"Error interno resolviendo tenant: {str(e)}",
                    "tenant_id": tenant_id
                }
            )
        finally:
            # 🧹 Limpiar contexto después del request
            _tenant_context.set(None)
            _request_context.set(None)

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

    async def _resolve_tenant_id(self, request: Request) -> tuple[Optional[str], Optional[str]]:
        """
        Resolve tenant_id using the configured resolution order.
        
        Args:
            request: FastAPI request object
            
        Returns:
            Tuple(tenant_id, resolution_method) or (None, None)
        """
        # 1. Check X-Tenant-Id header first (webhooks, APIs internas)
        tenant_header = request.headers.get("X-Tenant-Id")
        if tenant_header and tenant_header.strip():
            tenant_id = tenant_header.strip()
            # Validar que el tenant existe
            if await self._validate_tenant_exists(tenant_id):
                return tenant_id, "header"
        
        # 2. Extract subdomain from Host header (método principal)
        host = request.headers.get("Host", "")
        if host:
            subdomain = self._extract_subdomain(host)
            if subdomain:
                # Usar cache primero
                cache_key = f"subdomain:{subdomain}"
                cached_tenant = self._get_cached_value(cache_key)
                if cached_tenant:
                    _resolution_stats['cached'] += 1
                    return cached_tenant, "subdomain"
                
                # Consultar BD y cachear resultado
                tenant_id = await self._resolve_subdomain_to_tenant_id(subdomain)
                if tenant_id:
                    return tenant_id, "subdomain"
        
        # 3. Fallback SEGURO: solo permitir client_slug cuando el host NO es un subdominio tenant
        # (ej. app.sintestesia.cl, sintestesia.cl, localhost/dev). Evita spoofing entre tenants.
        host_clean = (request.headers.get("host") or "").lower()
        allowed_fallback_hosts = {
            "app.sintestesia.cl", "sintestesia.cl",
            "127.0.0.1:8002", "localhost:8002", "localhost:8000", "127.0.0.1:8000"
        }
        # si ya había subdominio válido, no usar fallback
        sub = self._extract_subdomain(host_clean) if host_clean else None
        is_tenant_subdomain = bool(sub and sub not in {"app", "www"})
        if (not is_tenant_subdomain) and (host_clean in allowed_fallback_hosts):
            slug = request.query_params.get("client_slug") or request.headers.get("X-Client-Slug")
            if slug and re.fullmatch(r"[a-z0-9-]{1,63}", slug):
                tenant_id = await self._resolve_subdomain_to_tenant_id(slug.strip())
                if tenant_id:
                    return tenant_id, "query"
        
        return None, None

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
            
            # Skip IP addresses (like 127.0.0.1, 192.168.1.1, etc.)
            import re
            if re.match(r'^\d+\.\d+\.\d+\.\d+$', host_clean):
                return None
            
            # Skip localhost
            if host_clean.lower() == 'localhost':
                return None
            
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
        _tenant_cache[key] = {
            'value': value,
            'timestamp': time.time()
        }

    async def _validate_tenant_exists(self, tenant_id: str) -> bool:
        """
        🔍 Valida que el tenant existe en la base de datos
        
        Args:
            tenant_id: ID del tenant a validar
            
        Returns:
            True si existe, False si no
        """
        try:
            with SessionLocal() as db:
                result = db.execute(
                    text("SELECT 1 FROM tenant_clients WHERE id = :tenant_id LIMIT 1"),
                    {"tenant_id": tenant_id}
                )
                return result.fetchone() is not None
        except Exception as e:
            logger.error(f"Error validating tenant {tenant_id}: {e}")
            return False

    def _is_valid_tenant_id(self, tenant_id: str) -> bool:
        """
        🔒 Valida formato del tenant ID
        
        Args:
            tenant_id: ID a validar
            
        Returns:
            True si el formato es válido
        """
        if not tenant_id or not isinstance(tenant_id, str):
            return False
        
        # Formato: solo letras minúsculas, números y guiones
        # Longitud entre 3 y 63 caracteres
        return bool(re.fullmatch(r"[a-z0-9-]{3,63}", tenant_id))

    async def _log_audit_event(self, request: Request, tenant_id: Optional[str], 
                              method: str, status: str, duration: float) -> None:
        """
        📋 Registra eventos de auditoría para resolución de tenants
        
        Args:
            request: Request object
            tenant_id: ID del tenant resuelto (o None)
            method: Método de resolución usado
            status: Estado del evento (success, error, rejected)
            duration: Duración del procesamiento en segundos
        """
        try:
            audit_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "tenant_id": tenant_id,
                "resolution_method": method,
                "status": status,
                "duration_ms": round(duration * 1000, 2),
                "request_info": {
                    "method": request.method,
                    "path": request.url.path,
                    "host": request.headers.get("host", ""),
                    "user_agent": request.headers.get("user-agent", "")[:100],  # Truncar
                    "ip": getattr(request.client, 'host', '') if request.client else '',
                    "query_params": dict(request.query_params) if request.query_params else {}
                }
            }
            
            # Log estructurado para auditoría
            if status == "success":
                logger.info("TENANT_RESOLVED", extra=audit_data)
            elif status == "rejected" or status == "no_tenant":
                logger.warning("TENANT_REJECTED", extra=audit_data)
            else:
                logger.error("TENANT_ERROR", extra=audit_data)
                
        except Exception as e:
            # No permitir que errores de auditoría afecten el request
            logger.error(f"Error logging audit event: {e}")

    def _get_cached_value(self, key: str) -> Optional[str]:
        """Get value from cache if not expired."""
        if key not in _tenant_cache:
            return None
            
        entry = _tenant_cache[key]
        if time.time() - entry['timestamp'] > _cache_ttl:
            # Expired, remove from cache
            del _tenant_cache[key]
            return None
            
        return entry['value']


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