"""
Sistema de Bot Multi-Tenant Dinámico y Escalable
Integra configuración personalizada del tenant con IA GPT para respuestas inteligentes
"""
import json
import os
from typing import Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from models import TenantPrompts
import openai

# Configuración OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

def get_tenant_bot_config(db: Session, tenant_id: str) -> Optional[Dict[str, Any]]:
    """
    Obtiene la configuración activa del bot para un tenant específico
    Escalable y dinámico - consulta la BD en tiempo real
    """
    try:
        config = db.query(TenantPrompts).filter(
            TenantPrompts.tenant_id == tenant_id,
            TenantPrompts.is_active == True
        ).first()
        
        if not config:
            print(f"⚠️ No hay configuración activa para tenant: {tenant_id}")
            return None
        
        return {
            "system_prompt": config.system_prompt,
            "style_overrides": config.style_overrides or {},
            "nlu_params": config.nlu_params or {},
            "nlg_params": config.nlg_params or {},
            "version": config.version
        }
    except Exception as e:
        print(f"❌ Error obteniendo configuración de tenant {tenant_id}: {e}")
        return None

def process_message_with_dynamic_ai(
    db: Session, 
    telefono: str, 
    mensaje: str, 
    tenant_id: str,
    productos: list,
    tenant_info: dict
) -> str:
    """
    Procesa mensaje usando IA GPT con configuración dinámica del tenant
    Sistema escalable que se adapta a cualquier tenant y sus productos
    """
    
    # 1. Obtener configuración personalizada del tenant
    bot_config = get_tenant_bot_config(db, tenant_id)
    if not bot_config:
        # Fallback con configuración básica pero dinámica
        bot_config = {
            "system_prompt": f"Eres un asistente de ventas especializado para {tenant_info.get('name', tenant_id)}. Ayuda con productos y responde de manera profesional.",
            "style_overrides": {"tono": "profesional_amigable", "usar_emojis": True},
            "nlg_params": {"modelo": "gpt-4o-mini", "temperature_nlg": 0.7, "max_tokens_nlg": 300}
        }
    
    # 2. Construir contexto dinámico de productos
    productos_contexto = ""
    if productos:
        productos_contexto = f"\n\nPRODUCTOS DISPONIBLES ({len(productos)} productos):\n"
        for i, producto in enumerate(productos[:10]):  # Limitar para no saturar
            precio = float(producto.get('price', 0))
            sale_price = float(producto.get('sale_price', 0)) if producto.get('sale_price') else None
            precio_mostrar = sale_price if sale_price else precio
            
            productos_contexto += f"• {producto.get('name', 'N/A')}"
            if precio_mostrar > 0:
                productos_contexto += f" - ${precio_mostrar:,.0f}"
            if producto.get('stock', 0) > 0:
                productos_contexto += f" (Stock: {producto.get('stock')})"
            productos_contexto += f"\n"
    
    # 3. Construir prompt dinámico personalizado
    system_prompt_completo = f"""{bot_config['system_prompt']}

INFORMACIÓN DEL NEGOCIO:
- Empresa: {tenant_info.get('name', tenant_id)}
- Tenant ID: {tenant_id}
- Moneda: {tenant_info.get('currency', 'CLP')}

{productos_contexto}

CONFIGURACIÓN DE ESTILO:
- Tono: {bot_config['style_overrides'].get('tono', 'profesional')}
- Usar emojis: {'Sí' if bot_config['style_overrides'].get('usar_emojis', True) else 'No'}
- Límite caracteres: {bot_config['style_overrides'].get('limite_respuesta_caracteres', 300)}

INSTRUCCIONES PARA LA RESPUESTA:
1. SIEMPRE usa información REAL de productos de la lista de arriba
2. Menciona precios exactos cuando sea relevante
3. Verifica stock disponible antes de recomendar productos
4. Respeta el tono y estilo configurado para este tenant
5. Si preguntan por productos específicos, busca coincidencias en la lista
6. Sé conciso pero informativo

MENSAJE DEL CLIENTE: "{mensaje}"

RESPONDE como el asistente de {tenant_info.get('name', tenant_id)} usando la información real de productos:"""

    # 4. Llamada a GPT con configuración personalizada
    try:
        client = openai.OpenAI()
        
        # Usar parámetros del tenant o valores por defecto
        modelo = bot_config['nlg_params'].get('modelo', 'gpt-4o-mini')
        temperature = float(bot_config['nlg_params'].get('temperature_nlg', 0.7))
        max_tokens = int(bot_config['nlg_params'].get('max_tokens_nlg', 300))
        
        print(f"🤖 Procesando con {modelo} (temp: {temperature}, tokens: {max_tokens}) para {tenant_id}")
        
        response = client.chat.completions.create(
            model=modelo,
            messages=[
                {"role": "system", "content": system_prompt_completo},
                {"role": "user", "content": mensaje}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        respuesta = response.choices[0].message.content.strip()
        
        # 5. Aplicar límite de caracteres si está configurado
        limite_chars = bot_config['style_overrides'].get('limite_respuesta_caracteres')
        if limite_chars and len(respuesta) > limite_chars:
            respuesta = respuesta[:limite_chars-3] + "..."
        
        print(f"✅ Respuesta generada para {tenant_id} (config v{bot_config.get('version', 'N/A')})")
        return respuesta
        
    except Exception as e:
        print(f"❌ Error en GPT para {tenant_id}: {e}")
        
        # Fallback inteligente que aún usa información real
        if productos and "producto" in mensaje.lower():
            productos_texto = ", ".join([p.get('name', 'N/A') for p in productos[:5]])
            return f"🌿 ¡Hola! Soy el asistente de {tenant_info.get('name', tenant_id)}. Algunos de nuestros productos disponibles: {productos_texto}. ¿Te interesa alguno en particular?"
        
        return f"¡Hola! Soy el asistente de {tenant_info.get('name', tenant_id)}. ¿En qué puedo ayudarte hoy? 🤖"

def get_dynamic_greeting_with_products(tenant_info: dict, productos: list) -> str:
    """
    Genera saludo dinámico personalizado con productos reales
    """
    empresa = tenant_info.get('name', 'nuestra tienda')
    
    if not productos:
        return f"¡Hola! Bienvenido a {empresa}. ¿En qué puedo ayudarte?"
    
    # Obtener categorías dinámicamente de los productos reales
    categorias = set()
    for producto in productos:
        categoria = producto.get('category', '').strip()
        if categoria:
            categorias.add(categoria.lower())
    
    if categorias:
        categorias_texto = ", ".join(sorted(categorias)[:4])
        return f"¡Hola! Bienvenido a {empresa} 👋\n\n🌿 Tenemos productos en: {categorias_texto} y más.\n\n¿Qué estás buscando hoy?"
    
    return f"¡Hola! Bienvenido a {empresa} 👋\n\nTenemos {len(productos)} productos disponibles. ¿En qué puedo ayudarte?"

def validate_tenant_message_context(tenant_id: str, mensaje: str, config: dict) -> bool:
    """
    Valida que el mensaje sea apropiado para el contexto del tenant
    Escalable para diferentes tipos de negocio
    """
    # Validaciones básicas de seguridad multi-tenant
    forbidden_patterns = [
        "change tenant", "switch client", "admin", "config", "delete", 
        "sql", "database", "hack", f"tenant:{tenant_id}"
    ]
    
    mensaje_lower = mensaje.lower()
    for pattern in forbidden_patterns:
        if pattern in mensaje_lower:
            print(f"⚠️ Mensaje bloqueado para {tenant_id}: contiene '{pattern}'")
            return False
    
    return True

def format_response_for_tenant(respuesta: str, tenant_info: dict, config: dict) -> str:
    """
    Formatea la respuesta según las preferencias del tenant
    """
    # Aplicar configuración de emojis
    if not config.get('style_overrides', {}).get('usar_emojis', True):
        # Remover emojis si están deshabilitados
        import re
        respuesta = re.sub(r'[^\w\s\.,\!\?\-\(\)]', '', respuesta)
    
    # Agregar branding si está habilitado
    if config.get('style_overrides', {}).get('incluir_contexto_empresa', True):
        empresa = tenant_info.get('name', '')
        if empresa and empresa.lower() not in respuesta.lower():
            respuesta = f"{respuesta}\n\n---\n{empresa}"
    
    return respuesta