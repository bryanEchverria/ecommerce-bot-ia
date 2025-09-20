from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import WhatsAppSettings
from whatsapp_schemas import (
    WhatsAppSettingsCreate,
    WhatsAppSettingsUpdate,
    WhatsAppSettingsResponse,
    WhatsAppTestRequest,
    WhatsAppTestResponse,
    WhatsAppProvidersInfo
)
from encryption_service import encrypt_sensitive_data, decrypt_sensitive_data
import logging
from datetime import datetime
from typing import Optional
import os

router = APIRouter()
logger = logging.getLogger(__name__)

def get_whatsapp_settings(db: Session) -> Optional[WhatsAppSettings]:
    """Obtiene la configuración global de WhatsApp (single tenant)"""
    return db.query(WhatsAppSettings).first()

def create_settings_response(db_settings: WhatsAppSettings) -> WhatsAppSettingsResponse:
    """Convierte el modelo de DB a schema de respuesta (sin exponer tokens)"""
    return WhatsAppSettingsResponse(
        id=db_settings.id,
        provider=db_settings.provider,
        is_active=db_settings.is_active,
        has_twilio_config=bool(db_settings.twilio_account_sid and db_settings.twilio_auth_token),
        has_meta_config=bool(db_settings.meta_token and db_settings.meta_phone_number_id),
        twilio_from=db_settings.twilio_from,
        meta_phone_number_id=db_settings.meta_phone_number_id,
        meta_graph_api_version=db_settings.meta_graph_api_version,
        created_at=db_settings.created_at,
        updated_at=db_settings.updated_at
    )

@router.post("/settings/whatsapp", response_model=WhatsAppSettingsResponse)
async def create_or_update_whatsapp_settings(
    settings: WhatsAppSettingsCreate,
    db: Session = Depends(get_db)
):
    """Crear o actualizar configuración global de WhatsApp"""
    try:
        # Validar que se proporcionen las configuraciones necesarias según el proveedor
        if settings.provider == "twilio" and not settings.twilio_settings:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Se requiere configuración de Twilio para el proveedor twilio"
            )
        
        if settings.provider == "meta" and not settings.meta_settings:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Se requiere configuración de Meta para el proveedor meta"
            )
        
        # Buscar configuración existente (siempre habrá máximo 1 registro)
        db_settings = get_whatsapp_settings(db)
        
        if db_settings:
            # Actualizar existente
            db_settings.provider = settings.provider
            db_settings.is_active = settings.is_active
            db_settings.updated_at = datetime.utcnow()
            
            # Limpiar configuraciones anteriores
            if settings.provider == "twilio":
                db_settings.twilio_account_sid = settings.twilio_settings.account_sid if settings.twilio_settings else None
                db_settings.twilio_auth_token = encrypt_sensitive_data(settings.twilio_settings.auth_token) if settings.twilio_settings else None
                db_settings.twilio_from = settings.twilio_settings.from_number if settings.twilio_settings else None
                # Limpiar configuración Meta
                db_settings.meta_token = None
                db_settings.meta_phone_number_id = None
                db_settings.meta_graph_api_version = "v21.0"
            else:  # meta
                db_settings.meta_token = encrypt_sensitive_data(settings.meta_settings.token) if settings.meta_settings else None
                db_settings.meta_phone_number_id = settings.meta_settings.phone_number_id if settings.meta_settings else None
                db_settings.meta_graph_api_version = settings.meta_settings.graph_api_version if settings.meta_settings else "v21.0"
                # Limpiar configuración Twilio
                db_settings.twilio_account_sid = None
                db_settings.twilio_auth_token = None
                db_settings.twilio_from = None
        else:
            # Crear nueva configuración (siempre con id=1 para single tenant)
            db_settings = WhatsAppSettings(
                id=1,  # Single tenant - solo un registro
                provider=settings.provider,
                is_active=settings.is_active
            )
            
            if settings.provider == "twilio" and settings.twilio_settings:
                db_settings.twilio_account_sid = settings.twilio_settings.account_sid
                db_settings.twilio_auth_token = encrypt_sensitive_data(settings.twilio_settings.auth_token)
                db_settings.twilio_from = settings.twilio_settings.from_number
            elif settings.provider == "meta" and settings.meta_settings:
                db_settings.meta_token = encrypt_sensitive_data(settings.meta_settings.token)
                db_settings.meta_phone_number_id = settings.meta_settings.phone_number_id
                db_settings.meta_graph_api_version = settings.meta_settings.graph_api_version
            
            db.add(db_settings)
        
        db.commit()
        db.refresh(db_settings)
        
        return create_settings_response(db_settings)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating/updating WhatsApp settings: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.get("/settings/whatsapp", response_model=WhatsAppSettingsResponse)
async def get_whatsapp_settings_endpoint(db: Session = Depends(get_db)):
    """Obtener configuración global de WhatsApp (sin exponer tokens)"""
    try:
        db_settings = get_whatsapp_settings(db)
        
        if not db_settings:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Configuración de WhatsApp no encontrada"
            )
        
        return create_settings_response(db_settings)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting WhatsApp settings: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.post("/settings/whatsapp/test", response_model=WhatsAppTestResponse)
async def test_whatsapp_settings(
    test_request: WhatsAppTestRequest,
    db: Session = Depends(get_db)
):
    """Probar configuración global de WhatsApp enviando un mensaje de prueba"""
    try:
        db_settings = get_whatsapp_settings(db)
        
        if not db_settings:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Configuración de WhatsApp no encontrada"
            )
        
        if not db_settings.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La configuración de WhatsApp está desactivada"
            )
        
        # Intentar enviar mensaje de prueba usando la configuración de DB
        success = False
        error_message = ""
        
        try:
            # Importar el servicio de mensajería aquí para evitar dependencias circulares
            import sys
            from pathlib import Path
            
            # Agregar path del whatsapp-bot-fastapi
            whatsapp_bot_path = Path(__file__).parent.parent.parent / "whatsapp-bot-fastapi"
            sys.path.append(str(whatsapp_bot_path))
            
            from adapters.base import WhatsAppAdapter
            
            # Crear adapter específico usando configuración de DB
            if db_settings.provider == "twilio":
                from adapters.twilio_adapter import TwilioAdapter
                
                # Backup variables de entorno actuales
                os_backup = {}
                twilio_vars = ["TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN", "TWILIO_WHATSAPP_NUMBER"]
                for var in twilio_vars:
                    if var in os.environ:
                        os_backup[var] = os.environ[var]
                
                try:
                    # Establecer variables temporalmente
                    os.environ["TWILIO_ACCOUNT_SID"] = db_settings.twilio_account_sid
                    os.environ["TWILIO_AUTH_TOKEN"] = decrypt_sensitive_data(db_settings.twilio_auth_token)
                    os.environ["TWILIO_WHATSAPP_NUMBER"] = db_settings.twilio_from or "whatsapp:+14155238886"
                    
                    adapter = TwilioAdapter()
                    success = await adapter.send_text(test_request.phone_number, test_request.message)
                    
                finally:
                    # Restaurar variables de entorno
                    for var in twilio_vars:
                        if var in os_backup:
                            os.environ[var] = os_backup[var]
                        elif var in os.environ:
                            del os.environ[var]
                            
            elif db_settings.provider == "meta":
                from adapters.meta_adapter import MetaAdapter
                
                # Backup variables de entorno actuales
                os_backup = {}
                meta_vars = ["WHATSAPP_TOKEN", "WHATSAPP_PHONE_NUMBER_ID", "GRAPH_API_VERSION"]
                for var in meta_vars:
                    if var in os.environ:
                        os_backup[var] = os.environ[var]
                
                try:
                    # Establecer variables temporalmente
                    os.environ["WHATSAPP_TOKEN"] = decrypt_sensitive_data(db_settings.meta_token)
                    os.environ["WHATSAPP_PHONE_NUMBER_ID"] = db_settings.meta_phone_number_id
                    os.environ["GRAPH_API_VERSION"] = db_settings.meta_graph_api_version or "v21.0"
                    
                    adapter = MetaAdapter()
                    success = await adapter.send_text(test_request.phone_number, test_request.message)
                    
                finally:
                    # Restaurar variables de entorno
                    for var in meta_vars:
                        if var in os_backup:
                            os.environ[var] = os_backup[var]
                        elif var in os.environ:
                            del os.environ[var]
            
        except Exception as e:
            error_message = str(e)
            logger.error(f"Error testing WhatsApp configuration: {error_message}")
        
        if success:
            return WhatsAppTestResponse(
                success=True,
                provider_used=db_settings.provider,
                message="Mensaje de prueba enviado exitosamente",
                details={"phone": test_request.phone_number, "provider": db_settings.provider}
            )
        else:
            return WhatsAppTestResponse(
                success=False,
                provider_used=db_settings.provider,
                message=f"Error enviando mensaje de prueba: {error_message}",
                details={"error": error_message}
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in test endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.delete("/settings/whatsapp")
async def delete_whatsapp_settings(db: Session = Depends(get_db)):
    """Eliminar configuración global de WhatsApp"""
    try:
        db_settings = get_whatsapp_settings(db)
        
        if not db_settings:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Configuración de WhatsApp no encontrada"
            )
        
        db.delete(db_settings)
        db.commit()
        
        return {"message": "Configuración de WhatsApp eliminada exitosamente"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting WhatsApp settings: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.get("/settings/whatsapp/providers", response_model=WhatsAppProvidersInfo)
async def get_providers_info(db: Session = Depends(get_db)):
    """Obtener información de proveedores disponibles"""
    try:
        # Obtener configuración actual
        db_settings = get_whatsapp_settings(db)
        current_provider = db_settings.provider if db_settings else "twilio"  # Default
        
        # Obtener info de proveedores globales
        import sys
        from pathlib import Path
        
        whatsapp_bot_path = Path(__file__).parent.parent.parent / "whatsapp-bot-fastapi"
        sys.path.append(str(whatsapp_bot_path))
        
        from settings import get_available_providers
        global_providers = get_available_providers()
        
        return WhatsAppProvidersInfo(
            current_provider=current_provider,
            providers=global_providers["providers"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting providers info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )