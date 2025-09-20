"""
🏢 SISTEMA DE AISLAMIENTO DE DATOS MULTI-TENANT
Sesiones de BD que automáticamente filtran por tenant_id
"""
from typing import Optional, Generator, Dict, Any, List
from functools import wraps
from contextvars import ContextVar

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session, Query
from sqlalchemy import text, event
from sqlalchemy.sql import Select
import logging

from database import SessionLocal
from tenant_middleware import get_tenant_id

logger = logging.getLogger(__name__)

# Context para tracking de queries por tenant
_query_context: ContextVar[Dict] = ContextVar('query_context', default={})


class TenantSession:
    """
    🔒 SESIÓN DE BD CON AISLAMIENTO AUTOMÁTICO POR TENANT
    
    Funcionalidades:
    - Filtrado automático por tenant_id en todas las queries
    - Prevención de cross-tenant data leaks
    - Logging de queries para auditoría
    - Validación de tenant_id en inserts/updates
    """
    
    def __init__(self, db: Session, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id
        self._query_count = 0
        self._setup_query_logging()
    
    def _setup_query_logging(self):
        """Configura logging de queries para auditoría"""
        @event.listens_for(self.db, 'before_cursor_execute')
        def log_sql_query(conn, cursor, statement, parameters, context, executemany):
            self._query_count += 1
            logger.debug(f"TENANT_QUERY [{self.tenant_id}]: {statement[:200]}")
    
    def execute(self, stmt, params=None):
        """Ejecuta query con contexto de tenant"""
        try:
            return self.db.execute(stmt, params)
        except Exception as e:
            logger.error(f"Query error for tenant {self.tenant_id}: {e}")
            raise
    
    def query(self, *args, **kwargs):
        """Query con filtrado automático por tenant_id"""
        query = self.db.query(*args, **kwargs)
        return self._apply_tenant_filter(query)
    
    def _apply_tenant_filter(self, query: Query) -> Query:
        """
        🔒 Aplica filtrado automático por tenant_id
        
        Args:
            query: Query de SQLAlchemy
            
        Returns:
            Query filtrada por tenant_id
        """
        # Obtener el modelo principal de la query
        if hasattr(query, 'column_descriptions') and query.column_descriptions:
            model = query.column_descriptions[0]['type']
            
            # Verificar si el modelo tiene campo tenant_id
            if hasattr(model, 'tenant_id'):
                logger.debug(f"Applying tenant filter for {model.__name__}: {self.tenant_id}")
                return query.filter(model.tenant_id == self.tenant_id)
            elif hasattr(model, 'client_id'):  # Soporte para campo legacy
                logger.debug(f"Applying client filter for {model.__name__}: {self.tenant_id}")
                return query.filter(model.client_id == self.tenant_id)
        
        # Si no tiene tenant_id, log warning pero permitir query
        logger.warning(f"Query without tenant filter detected for tenant {self.tenant_id}")
        return query
    
    def add(self, instance):
        """Add con validación de tenant_id"""
        if hasattr(instance, 'tenant_id'):
            if not instance.tenant_id:
                instance.tenant_id = self.tenant_id
            elif instance.tenant_id != self.tenant_id:
                raise HTTPException(
                    status_code=403,
                    detail=f"Cross-tenant operation detected: {instance.tenant_id} != {self.tenant_id}"
                )
        elif hasattr(instance, 'client_id'):  # Campo legacy
            if not instance.client_id:
                instance.client_id = self.tenant_id
            elif instance.client_id != self.tenant_id:
                raise HTTPException(
                    status_code=403,
                    detail=f"Cross-tenant operation detected: {instance.client_id} != {self.tenant_id}"
                )
        
        return self.db.add(instance)
    
    def commit(self):
        """Commit con logging de auditoría"""
        try:
            logger.debug(f"Committing {self._query_count} queries for tenant {self.tenant_id}")
            return self.db.commit()
        except Exception as e:
            logger.error(f"Commit error for tenant {self.tenant_id}: {e}")
            self.db.rollback()
            raise
    
    def rollback(self):
        """Rollback con logging"""
        logger.warning(f"Rolling back transaction for tenant {self.tenant_id}")
        return self.db.rollback()
    
    def close(self):
        """Close con limpieza de contexto"""
        logger.debug(f"Closing session for tenant {self.tenant_id} ({self._query_count} queries)")
        return self.db.close()
    
    def __getattr__(self, name):
        """Proxy para otros métodos de Session"""
        return getattr(self.db, name)


def get_tenant_database() -> Generator[TenantSession, None, None]:
    """
    🎯 DEPENDENCY PARA FASTAPI - SESIÓN CON AISLAMIENTO AUTOMÁTICO
    
    Uso en endpoints:
    ```python
    @app.get("/products")
    def get_products(db: TenantSession = Depends(get_tenant_database)):
        # Automáticamente filtrado por tenant_id del request
        return db.query(Product).all()
    ```
    
    Returns:
        TenantSession con filtrado automático por tenant_id
    """
    # Obtener tenant_id del contexto del request
    tenant_id = get_tenant_id()
    
    # Crear sesión normal de BD
    db = SessionLocal()
    
    try:
        # Envolver en TenantSession para aislamiento automático
        tenant_session = TenantSession(db, tenant_id)
        
        # Establecer contexto para debugging
        _query_context.set({
            "tenant_id": tenant_id,
            "session_id": id(tenant_session),
            "timestamp": str(logger.handlers[0].formatter.formatTime(None) if logger.handlers else "")
        })
        
        yield tenant_session
        
    finally:
        db.close()
        _query_context.set({})


def require_tenant_isolation(func):
    """
    🔒 DECORADOR PARA ASEGURAR AISLAMIENTO DE TENANT
    
    Uso:
    ```python
    @require_tenant_isolation
    def get_user_data(user_id: str, db: Session):
        # Automáticamente valida que user pertenece al tenant actual
        pass
    ```
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        current_tenant = get_tenant_id()
        
        # Log de operación para auditoría
        logger.info(f"TENANT_OPERATION: {func.__name__} for tenant {current_tenant}")
        
        try:
            result = func(*args, **kwargs)
            
            # Validar que resultado no contiene datos de otros tenants
            if hasattr(result, '__iter__') and not isinstance(result, (str, bytes)):
                for item in result:
                    if hasattr(item, 'tenant_id') and item.tenant_id != current_tenant:
                        logger.error(f"CROSS_TENANT_LEAK detected in {func.__name__}: {item.tenant_id}")
                        raise HTTPException(
                            status_code=500,
                            detail="Data isolation error detected"
                        )
            elif hasattr(result, 'tenant_id') and result.tenant_id != current_tenant:
                logger.error(f"CROSS_TENANT_LEAK detected in {func.__name__}: {result.tenant_id}")
                raise HTTPException(
                    status_code=500,
                    detail="Data isolation error detected"
                )
            
            return result
            
        except Exception as e:
            logger.error(f"Error in tenant operation {func.__name__} for {current_tenant}: {e}")
            raise
    
    return wrapper


def get_tenant_stats() -> Dict[str, Any]:
    """
    📊 Estadísticas de uso por tenant (para debugging)
    
    Returns:
        Diccionario con estadísticas de queries y sesiones
    """
    context = _query_context.get({})
    return {
        "current_tenant": context.get("tenant_id"),
        "session_id": context.get("session_id"),
        "timestamp": context.get("timestamp"),
        "total_sessions": len(_query_context.get("sessions", {}))
    }


# Funciones de utilidad para consultas comunes con aislamiento automático

def get_tenant_products(db: TenantSession, limit: int = 100) -> List:
    """Obtiene productos del tenant actual con límite"""
    return db.query(text("""
        SELECT id, name, price, stock, status 
        FROM products 
        WHERE client_id = :tenant_id 
        ORDER BY name 
        LIMIT :limit
    """)).params(tenant_id=db.tenant_id, limit=limit).all()


def get_tenant_orders(db: TenantSession, status: Optional[str] = None) -> List:
    """Obtiene pedidos del tenant actual opcionalmente filtrados por estado"""
    query = """
        SELECT id, phone, total_amount, status, created_at
        FROM orders 
        WHERE client_id = :tenant_id
    """
    params = {"tenant_id": db.tenant_id}
    
    if status:
        query += " AND status = :status"
        params["status"] = status
    
    query += " ORDER BY created_at DESC"
    
    return db.execute(text(query), params).all()


def validate_tenant_access(db: TenantSession, resource_id: str, table: str) -> bool:
    """
    🔒 Valida que un recurso pertenece al tenant actual
    
    Args:
        db: Sesión con tenant
        resource_id: ID del recurso a validar
        table: Tabla donde validar
        
    Returns:
        True si el recurso pertenece al tenant
    """
    result = db.execute(text(f"""
        SELECT 1 FROM {table} 
        WHERE id = :resource_id 
        AND (tenant_id = :tenant_id OR client_id = :tenant_id)
        LIMIT 1
    """), {
        "resource_id": resource_id,
        "tenant_id": db.tenant_id
    })
    
    return result.fetchone() is not None