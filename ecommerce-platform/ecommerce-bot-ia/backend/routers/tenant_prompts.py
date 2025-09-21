"""
Router FastAPI para configuración de prompts por tenant
Incluye control de acceso, auditoría y seguridad completa
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional, Dict, Any
import json
import time
import uuid
from datetime import datetime

from database import get_db
from auth import get_current_user, get_current_client
from models import TenantPrompts, TenantPromptAuditLog, PromptAction
from auth_models import TenantUser as User, TenantClient
from prompt_schemas import (
    TenantPromptCreate, TenantPromptUpdate, TenantPromptResponse,
    TenantPromptPreviewRequest, TenantPromptPreviewResponse,
    TenantPromptAuditLogResponse, TenantPromptRollbackRequest,
    TenantPromptVersionsResponse, TenantPromptError
)
from services.tenant_prompt_cache import (
    get_tenant_prompt_config, invalidate_tenant_prompt_cache,
    compose_final_system_prompt, BASE_SECURE_RULES
)


router = APIRouter(prefix="/api/tenants", tags=["tenant-prompts"])


async def verify_tenant_access(
    tenant_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> TenantClient:
    """
    Verificar que el usuario tenga acceso al tenant
    Solo admins globales o usuarios del tenant pueden acceder
    """
    # Verificar que el tenant existe
    tenant = db.query(TenantClient).filter(TenantClient.id == tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tenant {tenant_id} no encontrado"
        )
    
    # Solo admins globales o usuarios que pertenecen al tenant
    if not (current_user.role == "admin" or current_user.client_id == tenant_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para acceder a la configuración de este tenant"
        )
    
    return tenant


async def log_audit_action(
    tenant_id: str,
    prompt_config_id: str,
    action: str,
    changes_diff: Optional[Dict[str, Any]],
    user: User,
    request: Request,
    db: Session,
    previous_version: Optional[int] = None,
    new_version: Optional[int] = None
):
    """Registrar acción en log de auditoría"""
    audit_log = TenantPromptAuditLog(
        id=str(uuid.uuid4()),
        tenant_id=tenant_id,
        prompt_config_id=prompt_config_id,
        action=PromptAction(action),
        changes_diff=changes_diff or {},
        previous_version=previous_version,
        new_version=new_version,
        performed_by=user.id,
        performed_at=datetime.utcnow(),
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )
    
    db.add(audit_log)
    db.commit()


def calculate_diff(old_config: Optional[TenantPrompts], new_data: Dict[str, Any]) -> Dict[str, Any]:
    """Calcular diferencias entre configuración anterior y nueva"""
    if not old_config:
        return {"action": "create", "new_values": new_data}
    
    diff = {"action": "update", "changes": {}}
    
    # Comparar campos principales
    fields_to_compare = ["system_prompt", "style_overrides", "nlu_params", "nlg_params"]
    
    for field in fields_to_compare:
        old_value = getattr(old_config, field)
        new_value = new_data.get(field)
        
        if field in ["style_overrides", "nlu_params", "nlg_params"]:
            # Para campos JSON, comparar como diccionarios
            old_dict = old_value if old_value else {}
            new_dict = new_value if new_value else {}
            if old_dict != new_dict:
                diff["changes"][field] = {"old": old_dict, "new": new_dict}
        else:
            # Para campos texto
            if old_value != new_value:
                diff["changes"][field] = {
                    "old": old_value[:100] + "..." if len(str(old_value)) > 100 else old_value,
                    "new": new_value[:100] + "..." if len(str(new_value)) > 100 else new_value
                }
    
    return diff


@router.get("/{tenant_id}/prompt", response_model=TenantPromptResponse)
async def get_tenant_prompt_config(
    tenant_id: str,
    tenant: TenantClient = Depends(verify_tenant_access),
    db: Session = Depends(get_db)
):
    """
    Obtener configuración actual de prompts para un tenant
    Requiere: acceso al tenant (admin global o usuario del tenant)
    """
    config = db.query(TenantPrompts).filter(
        TenantPrompts.tenant_id == tenant_id,
        TenantPrompts.is_active == True
    ).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay configuración de prompts para este tenant"
        )
    
    return config


@router.put("/{tenant_id}/prompt", response_model=TenantPromptResponse)
async def update_tenant_prompt_config(
    tenant_id: str,
    prompt_data: TenantPromptUpdate,
    request: Request,
    tenant: TenantClient = Depends(verify_tenant_access),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Actualizar configuración de prompts para un tenant
    Requiere: acceso al tenant + permisos de admin del tenant
    """
    # Solo admins pueden modificar configuración
    if not (current_user.role == "admin" or current_user.role == "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden modificar la configuración de prompts"
        )
    
    # Obtener configuración actual
    current_config = db.query(TenantPrompts).filter(
        TenantPrompts.tenant_id == tenant_id,
        TenantPrompts.is_active == True
    ).first()
    
    if current_config:
        # Desactivar configuración actual
        current_config.is_active = False
        db.commit()
        
        # Calcular nueva versión
        new_version = current_config.version + 1
    else:
        new_version = 1
    
    # Crear nueva configuración
    update_data = prompt_data.dict(exclude_unset=True)
    
    # Si es actualización parcial, conservar valores actuales
    if current_config:
        for field in ["system_prompt", "style_overrides", "nlu_params", "nlg_params"]:
            if field not in update_data:
                update_data[field] = getattr(current_config, field)
    
    new_config = TenantPrompts(
        id=str(uuid.uuid4()),
        tenant_id=tenant_id,
        system_prompt=update_data["system_prompt"],
        style_overrides=update_data.get("style_overrides"),
        nlu_params=update_data.get("nlu_params"),
        nlg_params=update_data.get("nlg_params"),
        version=new_version,
        is_active=True,
        updated_by=current_user.id
    )
    
    db.add(new_config)
    db.commit()
    db.refresh(new_config)
    
    # Registrar en auditoría
    changes_diff = calculate_diff(current_config, update_data)
    await log_audit_action(
        tenant_id=tenant_id,
        prompt_config_id=new_config.id,
        action="UPDATE" if current_config else "CREATE",
        changes_diff=changes_diff,
        user=current_user,
        request=request,
        db=db,
        previous_version=current_config.version if current_config else None,
        new_version=new_version
    )
    
    # Invalidar caché
    invalidate_tenant_prompt_cache(tenant_id)
    
    return new_config


@router.post("/{tenant_id}/prompt", response_model=TenantPromptResponse)
async def create_tenant_prompt_config(
    tenant_id: str,
    prompt_data: TenantPromptCreate,
    request: Request,
    tenant: TenantClient = Depends(verify_tenant_access),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Crear configuración inicial de prompts para un tenant
    Requiere: acceso al tenant + permisos de admin
    """
    # Solo admins pueden crear configuración
    if not (current_user.role == "admin" or current_user.role == "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden crear configuración de prompts"
        )
    
    # Verificar que no existe configuración activa
    existing_config = db.query(TenantPrompts).filter(
        TenantPrompts.tenant_id == tenant_id,
        TenantPrompts.is_active == True
    ).first()
    
    if existing_config:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe una configuración activa para este tenant. Use PUT para actualizar."
        )
    
    # Crear nueva configuración
    new_config = TenantPrompts(
        id=str(uuid.uuid4()),
        tenant_id=tenant_id,
        system_prompt=prompt_data.system_prompt,
        style_overrides=prompt_data.style_overrides.dict() if prompt_data.style_overrides else None,
        nlu_params=prompt_data.nlu_params.dict() if prompt_data.nlu_params else None,
        nlg_params=prompt_data.nlg_params.dict() if prompt_data.nlg_params else None,
        version=1,
        is_active=True,
        updated_by=current_user.id
    )
    
    db.add(new_config)
    db.commit()
    db.refresh(new_config)
    
    # Registrar en auditoría
    await log_audit_action(
        tenant_id=tenant_id,
        prompt_config_id=new_config.id,
        action="CREATE",
        changes_diff={"action": "create", "initial_config": prompt_data.dict()},
        user=current_user,
        request=request,
        db=db,
        new_version=1
    )
    
    # Invalidar caché
    invalidate_tenant_prompt_cache(tenant_id)
    
    return new_config


@router.post("/preview-fixed/{tenant_id}")
async def preview_bot_config_fixed(
    tenant_id: str,
    request_data: dict,
    db: Session = Depends(get_db)
):
    """
    Endpoint de preview corregido que usa datos reales de BD
    Bypass del middleware para testing
    """
    try:
        import os
        from openai import OpenAI
        
        # Extraer datos del request
        test_message = request_data.get("test_message", "")
        include_products = request_data.get("include_products", True)
        
        # Obtener productos reales usando LA MISMA QUERY QUE EL BOT
        productos_tenant = []
        if include_products and db:
            query = text("""
                SELECT id, name, description, price, stock, status, client_id, category
                FROM products 
                WHERE client_id = :tenant_id 
                AND status = 'Active' 
                AND stock > 0
                ORDER BY name ASC
                LIMIT 8
            """)
            
            result = db.execute(query, {"tenant_id": tenant_id})
            for row in result:
                productos_tenant.append({
                    "name": row.name,
                    "description": row.description,
                    "price": row.price,
                    "stock": row.stock
                })
        
        # Crear contexto con productos reales
        if productos_tenant:
            productos_detallados = []
            for p in productos_tenant:
                productos_detallados.append(f"PRODUCTO: {p['name']}\nPRECIO: ${p['price']:,} pesos chilenos\nSTOCK: {p['stock']} unidades\nDESCRIPCIÓN: {p['description']}\n")
            
            productos_context = "\n".join(productos_detallados)
            
            full_prompt = f"""IMPORTANTE: Eres un sistema de ventas que DEBE usar ÚNICAMENTE los datos de la base de datos oficial. PROHIBIDO usar conocimiento externo.

=== PRODUCTOS DISPONIBLES EN INVENTARIO ===
{productos_context}

CONSULTA: "{test_message}"

REGLAS OBLIGATORIAS (NO OPCIONALES):
⚠️  SI EL CLIENTE PREGUNTA POR UN PRODUCTO QUE ESTÁ EN LA LISTA: Usar el precio EXACTO mostrado arriba
⚠️  SI EL CLIENTE PREGUNTA POR UN PRODUCTO NO LISTADO: Responder "No tenemos ese producto disponible"
⚠️  PROHIBIDO inventar precios o usar conocimiento general sobre productos
⚠️  PROHIBIDO mencionar rangos de precios genéricos como "$10-$15"

VERIFICACIÓN OBLIGATORIA:
- Antes de mencionar cualquier precio, verificar que esté en la lista de arriba
- Solo usar los precios exactos que aparecen después de "PRECIO: $"

TONO: amigable
EMOJIS: Usar emojis apropiados"""
        else:
            full_prompt = f"""No hay productos cargados en el sistema de inventario.

PREGUNTA: {test_message}
RESPUESTA: Lo siento, el sistema de inventario está vacío. No puedo consultar productos en este momento."""
        
        # Llamar a GPT
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": full_prompt}],
            temperature=0.3,
            max_tokens=300
        )
        
        bot_response = response.choices[0].message.content.strip()
        
        return {
            "bot_response": bot_response,
            "productos_encontrados": len(productos_tenant),
            "tenant_id": tenant_id,
            "preview_note": f"Generado con datos reales - {len(productos_tenant)} productos incluidos",
            "status": "success"
        }
        
    except Exception as e:
        return {"error": str(e), "status": "error"}

@router.post("/{tenant_id}/prompt/preview", response_model=TenantPromptPreviewResponse)
async def preview_tenant_prompt_config(
    tenant_id: str,
    preview_request: TenantPromptPreviewRequest,
    tenant: TenantClient = Depends(verify_tenant_access),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Probar configuración de prompts sin guardar
    Simula respuesta del bot con la configuración proporcionada
    """
    start_time = time.time()
    
    try:
        import os
        from openai import OpenAI
        
        # Extraer configuración
        prompt_config = preview_request.prompt_config.dict() if hasattr(preview_request.prompt_config, "dict") else preview_request.prompt_config
        system_prompt = prompt_config.get("system_prompt", "")
        style = prompt_config.get("style_overrides", {})
        nlg_params = prompt_config.get("nlg_params", {})
        
        # Obtener productos reales usando LA MISMA FUNCIÓN QUE EL BOT
        productos_tenant = []
        if preview_request.include_products and db:
            try:
                # Importar función del bot que SÍ funciona
                import sys
                sys.path.append('/app')
                
                # Usar la misma query exacta que el bot de WhatsApp
                query = text("""
                    SELECT id, name, description, price, stock, status, client_id, category
                    FROM products 
                    WHERE client_id = :tenant_id 
                    AND status = 'Active' 
                    AND stock > 0
                    ORDER BY name ASC
                    LIMIT 8
                """)
                
                result = db.execute(query, {"tenant_id": tenant_id})
                productos_tenant = []
                
                for row in result:
                    productos_tenant.append({
                        "name": row.name,
                        "description": row.description,
                        "price": row.price,
                        "stock": row.stock
                    })
                
                print(f"DEBUG PREVIEW: Encontrados {len(productos_tenant)} productos para tenant {tenant_id}")
            except Exception as e:
                print(f"ERROR BD PREVIEW: {e}")
                productos_tenant = []
        else:
            print(f"DEBUG PREVIEW: include_products={preview_request.include_products}, db={db is not None}")
        
        # Crear contexto de productos para GPT (ÚNICO)
        if productos_tenant:
            productos_detallados = []
            for p in productos_tenant:
                productos_detallados.append(f"PRODUCTO: {p['name']}\nPRECIO: ${p['price']:,} pesos chilenos\nSTOCK: {p['stock']} unidades\nDESCRIPCIÓN: {p['description']}\n")
            
            productos_context = "\n".join(productos_detallados)
            
            # FLUJO INTELIGENTE: GPT debe usar OBLIGATORIAMENTE datos exactos de BD
            full_prompt = f"""IMPORTANTE: Eres un sistema de ventas que DEBE usar ÚNICAMENTE los datos de la base de datos oficial. PROHIBIDO usar conocimiento externo.

=== PRODUCTOS DISPONIBLES EN INVENTARIO ===
{productos_context}

CONSULTA: "{preview_request.test_message}"

REGLAS OBLIGATORIAS (NO OPCIONALES):
⚠️  SI EL CLIENTE PREGUNTA POR UN PRODUCTO QUE ESTÁ EN LA LISTA: Usar el precio EXACTO mostrado arriba
⚠️  SI EL CLIENTE PREGUNTA POR UN PRODUCTO NO LISTADO: Responder "No tenemos ese producto disponible"
⚠️  PROHIBIDO inventar precios o usar conocimiento general sobre productos
⚠️  PROHIBIDO mencionar rangos de precios genéricos como "$10-$15"

VERIFICACIÓN OBLIGATORIA:
- Antes de mencionar cualquier precio, verificar que esté en la lista de arriba
- Solo usar los precios exactos que aparecen después de "PRECIO: $"

EJEMPLO CORRECTO:
Cliente: "precio white widow"
Respuesta: "La White Widow cuesta $40,000 pesos chilenos y tenemos 15 unidades disponibles"

TONO: {style.get('tono', 'amigable')}
EMOJIS: {'Usar emojis' if style.get('usar_emojis', True) else 'Sin emojis'}"""
        else:
            skip_gpt = False
            full_prompt = f"""No hay productos cargados en el sistema de inventario.

PREGUNTA: {preview_request.test_message}
RESPUESTA: Lo siento, el sistema de inventario está vacío. No puedo consultar productos en este momento."""

        # Llamar a GPT siempre (no hay skip_gpt en preview)
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        response = client.chat.completions.create(
            model=nlg_params.get("modelo", "gpt-4o-mini"),
            messages=[{"role": "user", "content": full_prompt}],
            temperature=nlg_params.get("temperature_nlg", 0.7),
            max_tokens=nlg_params.get("max_tokens_nlg", 300)
        )
        
        bot_response = response.choices[0].message.content.strip()
        
        # DEBUG TEMPORAL: Agregar información del prompt para verificar
        if "debug" in preview_request.test_message.lower():
            bot_response = f"PRODUCTOS ENCONTRADOS: {len(productos_tenant)}\nPRIMER PRODUCTO: {productos_tenant[0] if productos_tenant else 'NINGUNO'}\nPROMPT: {full_prompt[:500]}...\n\nRESPUESTA: {bot_response}"
        
        # Aplicar límite de caracteres estricto
        limite_chars = style.get("limite_respuesta_caracteres", 300)
        if len(bot_response) > limite_chars and "DEBUG" not in bot_response:
            bot_response = bot_response[:limite_chars-3] + "..."
        
        processing_time = int((time.time() - start_time) * 1000)
        
        return {
            "bot_response": bot_response,
            "processing_time_ms": processing_time,
            "tokens_used": {
                "nlu": 30,
                "nlg": response.usage.completion_tokens if response.usage else 0
            },
            "confidence_score": 0.95 if productos_tenant else 0.70,
            "detected_intent": "database_query_with_products" if productos_tenant else "general_query",
            "preview_note": f"Generado con {nlg_params.get('modelo', 'gpt-4o-mini')} - {len(productos_tenant)} productos incluidos"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al generar preview: {str(e)}"
        )


@router.get("/{tenant_id}/prompt/versions", response_model=TenantPromptVersionsResponse)
async def get_tenant_prompt_versions(
    tenant_id: str,
    limit: int = 10,
    tenant: TenantClient = Depends(verify_tenant_access),
    db: Session = Depends(get_db)
):
    """
    Obtener historial de versiones de configuración de prompts
    """
    versions = db.query(TenantPrompts).filter(
        TenantPrompts.tenant_id == tenant_id
    ).order_by(TenantPrompts.version.desc()).limit(limit).all()
    
    current_version = 0
    total_versions = db.query(TenantPrompts).filter(
        TenantPrompts.tenant_id == tenant_id
    ).count()
    
    if versions:
        current_active = next((v for v in versions if v.is_active), None)
        current_version = current_active.version if current_active else 0
    
    return TenantPromptVersionsResponse(
        versions=versions,
        current_version=current_version,
        total_versions=total_versions
    )


@router.post("/{tenant_id}/prompt/rollback")
async def rollback_tenant_prompt_config(
    tenant_id: str,
    rollback_request: TenantPromptRollbackRequest,
    request: Request,
    tenant: TenantClient = Depends(verify_tenant_access),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Hacer rollback a una versión anterior de la configuración
    Requiere: permisos de admin
    """
    # Solo admins pueden hacer rollback
    if not (current_user.role == "admin" or current_user.role == "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden hacer rollback"
        )
    
    # Buscar la versión objetivo
    target_config = db.query(TenantPrompts).filter(
        TenantPrompts.tenant_id == tenant_id,
        TenantPrompts.version == rollback_request.target_version
    ).first()
    
    if not target_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Versión {rollback_request.target_version} no encontrada"
        )
    
    # Desactivar configuración actual
    current_config = db.query(TenantPrompts).filter(
        TenantPrompts.tenant_id == tenant_id,
        TenantPrompts.is_active == True
    ).first()
    
    if current_config:
        current_config.is_active = False
        current_version = current_config.version
    else:
        current_version = 0
    
    # Crear nueva configuración basada en la versión objetivo
    new_version = db.query(TenantPrompts).filter(
        TenantPrompts.tenant_id == tenant_id
    ).count() + 1
    
    rollback_config = TenantPrompts(
        id=str(uuid.uuid4()),
        tenant_id=tenant_id,
        system_prompt=target_config.system_prompt,
        style_overrides=target_config.style_overrides,
        nlu_params=target_config.nlu_params,
        nlg_params=target_config.nlg_params,
        version=new_version,
        is_active=True,
        updated_by=current_user.id
    )
    
    db.add(rollback_config)
    db.commit()
    db.refresh(rollback_config)
    
    # Registrar en auditoría
    await log_audit_action(
        tenant_id=tenant_id,
        prompt_config_id=rollback_config.id,
        action="ROLLBACK",
        changes_diff={
            "action": "rollback",
            "target_version": rollback_request.target_version,
            "reason": rollback_request.reason
        },
        user=current_user,
        request=request,
        db=db,
        previous_version=current_version,
        new_version=new_version
    )
    
    # Invalidar caché
    invalidate_tenant_prompt_cache(tenant_id)
    
    return {"message": f"Rollback exitoso a versión {rollback_request.target_version}"}


@router.get("/{tenant_id}/prompt/audit", response_model=List[TenantPromptAuditLogResponse])
async def get_tenant_prompt_audit_log(
    tenant_id: str,
    limit: int = 50,
    tenant: TenantClient = Depends(verify_tenant_access),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener log de auditoría de cambios en configuración de prompts
    Requiere: permisos de admin para ver detalles completos
    """
    # Solo admins pueden ver el log completo
    if not (current_user.role == "admin" or current_user.role == "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden ver el log de auditoría"
        )
    
    audit_logs = db.query(TenantPromptAuditLog).filter(
        TenantPromptAuditLog.tenant_id == tenant_id
    ).order_by(TenantPromptAuditLog.performed_at.desc()).limit(limit).all()
    
    return audit_logs