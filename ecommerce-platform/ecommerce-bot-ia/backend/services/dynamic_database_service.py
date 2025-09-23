"""
🗃️ SERVICIO DE CONSULTAS DINÁMICAS A BASE DE DATOS
Permite al bot ejecutar queries SQL configurables de manera segura
"""
import logging
import time
import re
from typing import Dict, List, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import SessionLocal
from prompt_schemas import DatabaseQuery, DatabaseQueries
import hashlib
import json

logger = logging.getLogger(__name__)

# Cache simple en memoria para queries frecuentes
_query_cache: Dict[str, Dict[str, Any]] = {}

class DynamicDatabaseService:
    """
    🔍 Servicio para ejecutar queries SQL dinámicas configuradas por tenant
    
    Características:
    - Validación de seguridad SQL
    - Parámetros seguros con placeholders
    - Cache configurable por query
    - Límites de resultados
    - Logging de auditoría
    """
    
    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.db = SessionLocal()
    
    def __del__(self):
        """Cleanup database connection"""
        if hasattr(self, 'db') and self.db:
            self.db.close()
    
    def execute_query(
        self,
        query_config: DatabaseQuery,
        parameters: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Ejecuta una query dinámica de manera segura
        
        Args:
            query_config: Configuración de la query
            parameters: Parámetros para la query
            
        Returns:
            Lista de resultados como diccionarios
        """
        try:
            # Verificar si la query está activa
            if not query_config.is_active:
                logger.warning(f"Query {query_config.name} está desactivada")
                return []
            
            # Preparar parámetros
            safe_params = self._prepare_parameters(query_config, parameters or {})
            
            # Verificar cache
            cache_key = self._generate_cache_key(query_config, safe_params)
            cached_result = self._get_cached_result(cache_key, query_config.cache_ttl_seconds)
            if cached_result is not None:
                logger.info(f"Cache hit para query {query_config.name}")
                return cached_result
            
            # Validar SQL por seguridad
            safe_sql = self._validate_and_prepare_sql(query_config.sql_template, safe_params)
            
            # Ejecutar query
            logger.info(f"Ejecutando query {query_config.name} para tenant {self.tenant_id}")
            results = self._execute_safe_sql(safe_sql, safe_params, query_config.max_results)
            
            # Cachear resultado
            self._cache_result(cache_key, results, query_config.cache_ttl_seconds)
            
            logger.info(f"Query {query_config.name} retornó {len(results)} resultados")
            return results
            
        except Exception as e:
            logger.error(f"Error ejecutando query {query_config.name}: {str(e)}")
            return []
    
    def execute_database_queries(
        self,
        db_queries: DatabaseQueries,
        query_name: str,
        parameters: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Ejecuta una query específica del conjunto de queries configuradas
        
        Args:
            db_queries: Configuración completa de queries
            query_name: Nombre de la query a ejecutar
            parameters: Parámetros para la query
            
        Returns:
            Lista de resultados
        """
        try:
            # Buscar la query solicitada
            query_config = None
            
            # Queries predefinidas
            if query_name == "productos" or query_name == "products":
                query_config = db_queries.products_query
            elif query_name == "campanas" or query_name == "campaigns":
                query_config = db_queries.campaigns_query
            elif query_name == "descuentos" or query_name == "discounts":
                query_config = db_queries.discounts_query
            else:
                # Buscar en custom queries
                for custom_query in db_queries.custom_queries or []:
                    if custom_query.name == query_name:
                        query_config = custom_query
                        break
            
            if not query_config:
                logger.warning(f"Query '{query_name}' no encontrada para tenant {self.tenant_id}")
                return []
            
            # Agregar client_id automáticamente si es requerido
            if "client_id" in query_config.parameters:
                parameters = parameters or {}
                parameters["client_id"] = self.tenant_id
            
            return self.execute_query(query_config, parameters)
            
        except Exception as e:
            logger.error(f"Error ejecutando query '{query_name}': {str(e)}")
            return []
    
    def _prepare_parameters(
        self,
        query_config: DatabaseQuery,
        user_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Prepara y valida parámetros de manera segura"""
        safe_params = {}
        
        # Agregar parámetros esperados
        for param_name in query_config.parameters:
            if param_name == "client_id":
                safe_params[param_name] = self.tenant_id
            elif param_name == "limit":
                safe_params[param_name] = min(user_params.get("limit", query_config.max_results), query_config.max_results)
            elif param_name in user_params:
                # Sanitizar parámetro
                param_value = user_params[param_name]
                if isinstance(param_value, str):
                    # Sanitizar strings
                    param_value = re.sub(r"[';\"\\]", "", param_value)[:100]  # Límite de longitud
                safe_params[param_name] = param_value
            else:
                # Valor por defecto para parámetros requeridos
                if param_name == "category":
                    safe_params[param_name] = "%"  # Wildcard para ILIKE
                else:
                    safe_params[param_name] = ""
        
        return safe_params
    
    def _validate_and_prepare_sql(self, sql_template: str, parameters: Dict[str, Any]) -> str:
        """Valida y prepara SQL de manera segura"""
        sql = sql_template
        
        # Reemplazar placeholders de manera segura
        for param_name, param_value in parameters.items():
            placeholder = f"${param_name}"
            if placeholder in sql:
                # Para PostgreSQL, usar parámetros numerados
                sql = sql.replace(placeholder, f":param_{param_name}")
        
        return sql
    
    def _execute_safe_sql(
        self,
        sql: str,
        parameters: Dict[str, Any],
        max_results: int
    ) -> List[Dict[str, Any]]:
        """Ejecuta SQL de manera segura con parámetros"""
        try:
            # Preparar parámetros para SQLAlchemy
            sql_params = {}
            for param_name, param_value in parameters.items():
                sql_params[f"param_{param_name}"] = param_value
            
            # Ejecutar query con límite
            result = self.db.execute(text(sql), sql_params)
            
            # Convertir resultados a diccionarios
            columns = result.keys()
            rows = result.fetchmany(max_results)
            
            return [dict(zip(columns, row)) for row in rows]
            
        except Exception as e:
            logger.error(f"Error ejecutando SQL: {str(e)}")
            raise
    
    def _generate_cache_key(self, query_config: DatabaseQuery, parameters: Dict[str, Any]) -> str:
        """Genera clave única para cache"""
        cache_data = {
            "query_name": query_config.name,
            "tenant_id": self.tenant_id,
            "parameters": parameters,
            "sql": query_config.sql_template
        }
        cache_string = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_string.encode()).hexdigest()
    
    def _get_cached_result(self, cache_key: str, ttl_seconds: int) -> Optional[List[Dict[str, Any]]]:
        """Obtiene resultado del cache si no ha expirado"""
        if cache_key not in _query_cache:
            return None
        
        cache_entry = _query_cache[cache_key]
        if time.time() - cache_entry["timestamp"] > ttl_seconds:
            # Cache expirado
            del _query_cache[cache_key]
            return None
        
        return cache_entry["data"]
    
    def _cache_result(self, cache_key: str, data: List[Dict[str, Any]], ttl_seconds: int):
        """Guarda resultado en cache"""
        if ttl_seconds > 0:  # Solo cachear si TTL > 0
            _query_cache[cache_key] = {
                "data": data,
                "timestamp": time.time()
            }
    
    @staticmethod
    def clear_cache():
        """Limpia todo el cache (útil para testing)"""
        global _query_cache
        _query_cache.clear()
    
    @staticmethod
    def get_cache_stats() -> Dict[str, Any]:
        """Obtiene estadísticas del cache"""
        return {
            "total_entries": len(_query_cache),
            "cache_keys": list(_query_cache.keys())
        }


def get_available_queries() -> DatabaseQueries:
    """
    Retorna las queries por defecto disponibles
    """
    return DatabaseQueries()


def test_query_security(sql_template: str) -> Tuple[bool, str]:
    """
    Prueba la seguridad de un template SQL
    
    Returns:
        (is_safe, error_message)
    """
    try:
        from prompt_schemas import DatabaseQuery
        
        test_query = DatabaseQuery(
            name="test",
            sql_template=sql_template,
            parameters=[]
        )
        return True, "Query SQL es segura"
        
    except ValueError as e:
        return False, str(e)
    except Exception as e:
        return False, f"Error validando query: {str(e)}"