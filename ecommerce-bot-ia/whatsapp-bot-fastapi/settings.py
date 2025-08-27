import os
import logging
from typing import Optional
from adapters import WhatsAppAdapter, TwilioAdapter, MetaAdapter

logger = logging.getLogger(__name__)

# Variable de entorno para seleccionar proveedor
WA_PROVIDER = os.getenv("WA_PROVIDER", "twilio")  # Default a Twilio por compatibilidad

# Futuro mapeo por tenant (comentado para implementación posterior)
# TENANT_PROVIDER = {
#     "tenant_1": "twilio",
#     "tenant_2": "meta",
#     "mundo_canino": "meta",
# }

def get_config_from_db() -> Optional[dict]:
    """
    Obtiene configuración global de WhatsApp desde la base de datos (single tenant)
    
    Returns:
        dict: Configuración global o None si no existe
    """
    try:
        import sys
        from pathlib import Path
        
        # Agregar path del backend
        backend_path = Path(__file__).parent.parent / "backend"
        sys.path.append(str(backend_path))
        
        from database import SessionLocal
        from models import WhatsAppSettings
        from encryption_service import decrypt_sensitive_data
        
        db = SessionLocal()
        try:
            db_settings = db.query(WhatsAppSettings).filter(
                WhatsAppSettings.is_active == True
            ).first()
            
            if not db_settings:
                return None
            
            config = {
                "provider": db_settings.provider,
                "is_active": db_settings.is_active
            }
            
            if db_settings.provider == "twilio":
                config.update({
                    "twilio_account_sid": db_settings.twilio_account_sid,
                    "twilio_auth_token": decrypt_sensitive_data(db_settings.twilio_auth_token) if db_settings.twilio_auth_token else None,
                    "twilio_from": db_settings.twilio_from
                })
            elif db_settings.provider == "meta":
                config.update({
                    "meta_token": decrypt_sensitive_data(db_settings.meta_token) if db_settings.meta_token else None,
                    "meta_phone_number_id": db_settings.meta_phone_number_id,
                    "meta_graph_api_version": db_settings.meta_graph_api_version
                })
            
            return config
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error getting config from DB: {str(e)}")
        return None

def create_adapter_with_config(provider: str, config: dict) -> WhatsAppAdapter:
    """
    Crea un adapter con configuración específica
    
    Args:
        provider: Tipo de proveedor ("twilio" o "meta")
        config: Configuración específica del proveedor
        
    Returns:
        WhatsAppAdapter: Instancia del adapter configurado
    """
    # Backup de variables de entorno actuales
    os_backup = {}
    
    try:
        if provider == "twilio":
            # Backup y establecer variables de entorno para Twilio
            twilio_vars = ["TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN", "TWILIO_WHATSAPP_NUMBER"]
            for var in twilio_vars:
                if var in os.environ:
                    os_backup[var] = os.environ[var]
            
            if config.get("twilio_account_sid"):
                os.environ["TWILIO_ACCOUNT_SID"] = config["twilio_account_sid"]
            if config.get("twilio_auth_token"):
                os.environ["TWILIO_AUTH_TOKEN"] = config["twilio_auth_token"]
            if config.get("twilio_from"):
                os.environ["TWILIO_WHATSAPP_NUMBER"] = config["twilio_from"]
            
            adapter = TwilioAdapter()
            
        elif provider == "meta":
            # Backup y establecer variables de entorno para Meta
            meta_vars = ["WHATSAPP_TOKEN", "WHATSAPP_PHONE_NUMBER_ID", "GRAPH_API_VERSION"]
            for var in meta_vars:
                if var in os.environ:
                    os_backup[var] = os.environ[var]
            
            if config.get("meta_token"):
                os.environ["WHATSAPP_TOKEN"] = config["meta_token"]
            if config.get("meta_phone_number_id"):
                os.environ["WHATSAPP_PHONE_NUMBER_ID"] = config["meta_phone_number_id"]
            if config.get("meta_graph_api_version"):
                os.environ["GRAPH_API_VERSION"] = config["meta_graph_api_version"]
            
            adapter = MetaAdapter()
        else:
            raise ValueError(f"Unsupported provider: {provider}")
        
        return adapter
        
    finally:
        # Restaurar variables de entorno
        for var, value in os_backup.items():
            os.environ[var] = value
        
        # Limpiar variables que no existían antes
        if provider == "twilio":
            for var in ["TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN", "TWILIO_WHATSAPP_NUMBER"]:
                if var not in os_backup and var in os.environ:
                    del os.environ[var]
        elif provider == "meta":
            for var in ["WHATSAPP_TOKEN", "WHATSAPP_PHONE_NUMBER_ID", "GRAPH_API_VERSION"]:
                if var not in os_backup and var in os.environ:
                    del os.environ[var]

def get_adapter(tenant_id: Optional[str] = None) -> WhatsAppAdapter:
    """
    Obtiene el adapter de WhatsApp apropiado según configuración (single tenant)
    
    Prioridad:
    1. Configuración en DB (si existe y está activa)
    2. Variables de entorno globales (fallback)
    
    Args:
        tenant_id: Parámetro legacy - se ignora en single tenant
        
    Returns:
        WhatsAppAdapter: Instancia del adapter configurado
        
    Raises:
        ValueError: Si el proveedor no es válido o falta configuración
    """
    
    provider = WA_PROVIDER.lower()
    config = None
    
    # 1. Intentar obtener configuración desde DB
    config = get_config_from_db()
    if config:
        provider = config["provider"].lower()
        logger.info(f"Using DB config: provider={provider}")
    else:
        logger.info("No DB config found, using global env config")
    
    # 2. Si tenemos configuración específica, crear adapter con esa config
    if config:
        try:
            return create_adapter_with_config(provider, config)
        except Exception as e:
            logger.error(f"Failed to create adapter with DB config: {str(e)}")
            # Continuar con fallback a configuración global
    
    # 3. Fallback a configuración global de variables de entorno
    logger.info(f"Using global WhatsApp provider: {provider}")
    
    try:
        if provider == "twilio":
            return TwilioAdapter()
        elif provider == "meta":
            return MetaAdapter()
        else:
            raise ValueError(f"Unsupported WhatsApp provider: {provider}")
            
    except Exception as e:
        logger.error(f"Failed to initialize {provider} adapter: {str(e)}")
        # Fallback a Twilio si Meta falla y viceversa
        if provider == "meta":
            logger.info("Falling back to Twilio adapter")
            try:
                return TwilioAdapter()
            except Exception as twilio_error:
                logger.error(f"Twilio fallback also failed: {str(twilio_error)}")
        elif provider == "twilio":
            logger.info("Falling back to Meta adapter")
            try:
                return MetaAdapter()
            except Exception as meta_error:
                logger.error(f"Meta fallback also failed: {str(meta_error)}")
        
        # Si ambos fallan, re-lanzar el error original
        raise e

def get_available_providers() -> dict:
    """
    Retorna información sobre los proveedores disponibles y su estado
    
    Returns:
        dict: Estado de cada proveedor
    """
    providers_status = {}
    
    # Verificar Twilio
    try:
        twilio_adapter = TwilioAdapter()
        providers_status["twilio"] = {
            "available": True,
            "name": twilio_adapter.get_provider_name(),
            "configured": bool(os.getenv("TWILIO_ACCOUNT_SID") and os.getenv("TWILIO_AUTH_TOKEN"))
        }
    except Exception as e:
        providers_status["twilio"] = {
            "available": False,
            "error": str(e),
            "configured": bool(os.getenv("TWILIO_ACCOUNT_SID") and os.getenv("TWILIO_AUTH_TOKEN"))
        }
    
    # Verificar Meta
    try:
        meta_adapter = MetaAdapter()
        providers_status["meta"] = {
            "available": True,
            "name": meta_adapter.get_provider_name(),
            "configured": bool(os.getenv("WHATSAPP_TOKEN") and os.getenv("WHATSAPP_PHONE_NUMBER_ID"))
        }
    except Exception as e:
        providers_status["meta"] = {
            "available": False,
            "error": str(e),
            "configured": bool(os.getenv("WHATSAPP_TOKEN") and os.getenv("WHATSAPP_PHONE_NUMBER_ID"))
        }
    
    return {
        "current_provider": WA_PROVIDER,
        "providers": providers_status
    }