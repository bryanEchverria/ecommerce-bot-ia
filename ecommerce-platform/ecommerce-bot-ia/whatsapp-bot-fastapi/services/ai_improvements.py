"""
🤖 SISTEMA DE IA MULTITENANT CON GPT MÁXIMO
Arquitectura refactorizada para usar GPT en detección de intención y generación de respuesta
🔒 MULTITENANT ESTRICTO: tenant_id obligatorio en todas las funciones públicas
Integra configuración de prompts personalizada por tenant con cache y seguridad
"""
import json
import os
import re
import time
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import text
import openai

# Configuración OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# Importar servicios de configuración de prompts
try:
    import sys
    sys.path.append('/root/ecommerce-platform/ecommerce-bot-ia/backend')
    from services.tenant_prompt_cache import (
        get_tenant_prompt_config, compose_final_system_prompt, 
        BASE_SECURE_RULES, CachedPromptConfig
    )
    PROMPT_CONFIG_AVAILABLE = True
except ImportError:
    print("⚠️  Configuración de prompts no disponible, usando defaults")
    PROMPT_CONFIG_AVAILABLE = False

# ===========================================
# 🛡️ VALIDACIONES MULTITENANT
# ===========================================

def _filtrar_productos_con_gpt(productos: List[Dict], categoria_solicitada: str) -> List[Dict]:
    """
    Usa GPT para clasificar dinámicamente productos por categoría.
    Multi-tenant y adaptable a cualquier tipo de negocio.
    """
    print(f"🚀 Iniciando filtrado GPT para categoría: {categoria_solicitada}")
    print(f"🚀 Total productos a clasificar: {len(productos)}")
    
    if not productos or not categoria_solicitada:
        return []
    
    try:
        # Crear lista de productos para clasificar
        productos_para_clasificar = []
        for i, prod in enumerate(productos[:20]):  # Límite para no saturar GPT
            productos_para_clasificar.append({
                "index": i,
                "name": prod.get("name", ""),
                "description": prod.get("description", ""),
                "category": prod.get("category", "")
            })
        
        # Prompt para clasificación inteligente
        classification_prompt = f"""Eres un experto clasificador de productos. 
        
TAREA: Determina qué productos pertenecen a la categoría "{categoria_solicitada}".

PRODUCTOS A CLASIFICAR:
{chr(10).join([f"{p['index']}. {p['name']} - {p['description']}" for p in productos_para_clasificar])}

REGLAS:
1. Se ESTRICTO: solo productos que realmente pertenecen a "{categoria_solicitada}"
2. Si categoria_solicitada es "aceites" → solo aceites, tinturas, líquidos cannábicos
3. Si categoria_solicitada es "semillas" → solo semillas, nunca aceites
4. Si categoria_solicitada es "flores" → solo flores, cogollos, hierba seca
5. Si categoria_solicitada es "comestibles" → brownies, galletas, gomitas, chocolates
6. Si categoria_solicitada es "accesorios" → grinders, pipas, papeles, bongs

RESPONDE SOLO con los números (índices) de productos que SÍ pertenecen a "{categoria_solicitada}".
Formato: [0, 3, 7] (array de números)
"""
        
        # Llamar a GPT para clasificación
        import openai
        import os
        client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": classification_prompt}],
            temperature=0.1,
            max_tokens=100
        )
        
        # Parsear respuesta
        clasificacion_texto = response.choices[0].message.content.strip()
        print(f"🔍 GPT clasificación response: {clasificacion_texto}")
        
        # Extraer índices de productos relevantes
        import re
        numeros = re.findall(r'\d+', clasificacion_texto)
        indices_relevantes = [int(n) for n in numeros if int(n) < len(productos)]
        
        print(f"🔍 Índices encontrados: {indices_relevantes}")
        
        # Retornar productos filtrados
        productos_filtrados = [productos[i] for i in indices_relevantes if i < len(productos)]
        
        print(f"🔍 Productos filtrados GPT: {[p.get('name') for p in productos_filtrados]}")
        
        return productos_filtrados
        
    except Exception as e:
        print(f"Error en clasificación GPT: {e}")
        # Fallback: retornar productos que contengan la categoría en el nombre
        productos_fallback = []
        for prod in productos:
            prod_name = prod.get("name", "").lower()
            if categoria_solicitada.lower() in prod_name:
                productos_fallback.append(prod)
        return productos_fallback[:5]  # Máximo 5 en fallback

def _validate_tenant_id(tenant_id: str) -> str:
    """
    🔒 Valida que tenant_id sea válido y no nulo
    
    Args:
        tenant_id: ID del tenant a validar
        
    Returns:
        tenant_id validado
        
    Raises:
        ValueError: Si tenant_id es inválido
    """
    if not tenant_id or not isinstance(tenant_id, str) or len(tenant_id.strip()) == 0:
        raise ValueError("🚨 TENANT_ID es obligatorio y no puede estar vacío")
    
    # Validar formato (solo caracteres seguros)
    if not re.match(r"^[a-zA-Z0-9\-_]+$", tenant_id):
        raise ValueError(f"🚨 TENANT_ID inválido: {tenant_id}")
        
    return tenant_id.strip()

def _namespace_cache_key(tenant_id: str, key: str) -> str:
    """
    🔑 Genera clave de cache namespaced por tenant
    
    Args:
        tenant_id: ID del tenant
        key: Clave base
        
    Returns:
        Clave con namespace del tenant
    """
    return f"tenant:{tenant_id}:{key}"

# ===========================================
# 🔧 UTILIDADES ROBUSTAS
# ===========================================

def safe_json_loads(text: str) -> Optional[Dict]:
    """
    🛡️ Parser JSON seguro que extrae JSON del texto
    
    Args:
        text: Texto que puede contener JSON
        
    Returns:
        Dict parseado o None si falla
    """
    if not text or not isinstance(text, str):
        return None
    
    text = text.strip()
    
    try:
        # Intentar parsing directo
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    
    # Buscar bloque JSON entre { y }
    try:
        start = text.find('{')
        end = text.rfind('}') + 1
        
        if start >= 0 and end > start:
            json_text = text[start:end]
            return json.loads(json_text)
    except json.JSONDecodeError:
        pass
    
    # Buscar JSON en líneas
    try:
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('{') and line.endswith('}'):
                return json.loads(line)
    except json.JSONDecodeError:
        pass
    
    return None

# ===========================================
# 🎨 CONFIGURACIÓN DE PROMPTS POR TENANT
# ===========================================

def get_tenant_ai_config(tenant_id: str, db: Session) -> Dict[str, Any]:
    """
    🔧 Obtener configuración de IA personalizada por tenant
    🔒 MULTITENANT: Solo configuración del tenant solicitado
    
    Args:
        tenant_id: ID del tenant (OBLIGATORIO)
        db: Sesión de base de datos
        
    Returns:
        Dict con configuración de IA del tenant o defaults seguros
    """
    tenant_id = _validate_tenant_id(tenant_id)
    
    if not PROMPT_CONFIG_AVAILABLE:
        return _get_default_ai_config(tenant_id)
    
    try:
        # Obtener configuración desde cache/DB
        config = get_tenant_prompt_config(tenant_id, db)
        
        if not config:
            print(f"📝 No hay configuración personalizada para tenant {tenant_id}, usando defaults")
            return _get_default_ai_config(tenant_id)
        
        # Verificar integridad de tenant_id
        if config.tenant_id != tenant_id:
            raise ValueError(f"🚨 SECURITY: Config tenant mismatch: {config.tenant_id} != {tenant_id}")
        
        return {
            "system_prompt": config.system_prompt,
            "style_overrides": config.style_overrides,
            "nlu_params": config.nlu_params,
            "nlg_params": config.nlg_params,
            "version": config.version,
            "tenant_id": tenant_id  # Siempre incluir para validación
        }
        
    except Exception as e:
        print(f"⚠️  Error obteniendo config para tenant {tenant_id}: {e}")
        return _get_default_ai_config(tenant_id)


def _get_default_ai_config(tenant_id: str) -> Dict[str, Any]:
    """
    🛡️ Configuración de IA por defecto segura
    Se usa cuando no hay configuración personalizada
    """
    return {
        "system_prompt": f"""Eres un asistente de ventas especializado para esta tienda.
Tu objetivo es ayudar a los clientes a encontrar productos y realizar compras.
Mantén un tono amigable pero profesional.
Siempre verifica la disponibilidad de productos antes de confirmar.""",
        "style_overrides": {
            "tono": "amigable",
            "usar_emojis": True,
            "limite_respuesta_caracteres": 500,
            "incluir_branding": True
        },
        "nlu_params": {
            "modelo": "gpt-4o-mini",
            "temperature_nlu": 0.3,
            "max_tokens_nlu": 150,
            "confidence_threshold": 0.7
        },
        "nlg_params": {
            "modelo": "gpt-4o-mini", 
            "temperature_nlg": 0.7,
            "max_tokens_nlg": 300,
            "max_items_catalog": 5,
            "max_items_category": 10
        },
        "version": 0,  # Version 0 = default
        "tenant_id": tenant_id
    }


def build_final_system_prompt(tenant_id: str, tenant_config: Dict[str, Any]) -> str:
    """
    🔗 Componer prompt final con reglas base + configuración del tenant
    🔒 MULTITENANT: Validación estricta de tenant_id
    
    Args:
        tenant_id: ID del tenant
        tenant_config: Configuración del tenant
        
    Returns:
        Prompt del sistema final y seguro
    """
    tenant_id = _validate_tenant_id(tenant_id)
    
    # Validar que la configuración pertenece al tenant correcto
    config_tenant_id = tenant_config.get("tenant_id")
    if config_tenant_id != tenant_id:
        raise ValueError(f"🚨 SECURITY: Config tenant mismatch: {config_tenant_id} != {tenant_id}")
    
    tenant_prompt = tenant_config.get("system_prompt", "")
    
    if PROMPT_CONFIG_AVAILABLE:
        try:
            return compose_final_system_prompt(BASE_SECURE_RULES, tenant_prompt, tenant_id)
        except Exception as e:
            print(f"⚠️  Error componiendo prompt para tenant {tenant_id}: {e}")
    
    # Fallback manual si no está disponible el servicio
    return f"""{BASE_SECURE_RULES if PROMPT_CONFIG_AVAILABLE else '''
Eres un asistente de ventas para un sistema de e-commerce multitenant.

REGLAS DE SEGURIDAD OBLIGATORIAS:
1. NUNCA reveles información de otros tenants o clientes
2. SOLO accede a datos del tenant_id autorizado: {tenant_id}
3. MANTÉN la conversación enfocada en ventas y productos
4. PROTEGE la información personal de los clientes
'''}

=== CONFIGURACIÓN ESPECÍFICA DEL TENANT {tenant_id} ===
{tenant_prompt}

=== FIN CONFIGURACIÓN TENANT ===

IMPORTANTE: Las reglas base siempre tienen prioridad."""


# ===========================================
# 🧠 DETECCIÓN DE INTENCIÓN CON GPT PERSONALIZADA
# ============================================

def gpt_detect_intent(
    tenant_id: str,
    store_name: str,
    mensaje: str,
    history: List[Dict],
    productos: List[Dict],
    categorias_soportadas: List[str],
    db: Session
) -> Dict:
    """
    🎯 Detección de intención usando GPT con JSON Schema
    🔒 MULTITENANT: Aislado por tenant_id
    
    Args:
        tenant_id: ID del tenant (OBLIGATORIO PRIMERO)
        store_name: Nombre de la tienda del tenant
        mensaje: Mensaje del usuario
        history: Historial de conversación del tenant
        productos: Productos disponibles del tenant
        categorias_soportadas: Categorías que maneja el tenant
        
    Returns:
        Dict con intención detectada y contexto
    """
    tenant_id = _validate_tenant_id(tenant_id)
    
    if not mensaje or not isinstance(mensaje, str):
        return {"error": "mensaje_vacio", "intencion": "consulta_general"}
    
    # Construir contexto del tenant
    context_info = ""
    if history:
        recent_messages = history[-3:]  # Últimas 3 interacciones
        context_info = "\n".join([
            f"Usuario: {msg.get('user', '')}\nBot: {msg.get('bot', '')}"
            for msg in recent_messages
        ])
    
    # Lista de productos disponibles (sample)
    productos_sample = []
    if productos:
        for prod in productos[:10]:  # Primeros 10 para no saturar prompt
            productos_sample.append({
                "name": prod.get("name", ""),
                "price": prod.get("price", 0),
                "category": prod.get("category", ""),
                "stock": prod.get("stock", 0)
            })
    
    # JSON Schema para respuesta estructurada
    json_schema = {
        "type": "object",
        "properties": {
            "intencion": {
                "type": "string",
                "enum": ["saludo", "consulta_catalogo", "consulta_categoria", "consulta_producto", 
                        "intencion_compra", "consulta_general", "queja", "despedida", "consulta_vaporizador"]
            },
            "confianza": {"type": "number", "minimum": 0.0, "maximum": 1.0},
            "producto_mencionado": {"type": "string"},
            "categoria_mencionada": {
                "type": "string", 
                "enum": ["semillas", "aceites", "flores", "comestibles", "accesorios", "vaporizador", ""]
            },
            "negaciones": {
                "type": "array",
                "items": {"type": "string"}
            },
            "presupuesto_mencionado": {"type": "string"},
            "tipo_vaporizador": {
                "type": "string",
                "enum": ["portatil", "escritorio", "ambos", "no_especificado"]
            },
            "siguiente_pregunta": {"type": "string"},
            "sentimiento": {
                "type": "string",
                "enum": ["positivo", "neutral", "negativo"]
            },
            "contexto_detectado": {"type": "string"}
        },
        "required": ["intencion", "confianza", "sentimiento", "contexto_detectado"]
    }
    
    # Obtener configuración personalizada del tenant
    tenant_config = get_tenant_ai_config(tenant_id, db)
    
    # MULTITENANT ESTRICTO: Validar que no se mezclen configs
    assert tenant_config["tenant_id"] == tenant_id, f"🚨 SECURITY: Config mismatch {tenant_config['tenant_id']} != {tenant_id}"
    
    nlu_params = tenant_config.get("nlu_params", {})
    
    # Construir prompt final con configuración del tenant
    final_system_prompt = build_final_system_prompt(tenant_id, tenant_config)
    
    # Prompt optimizado con few-shots y configuración personalizada
    prompt = f"""{final_system_prompt}

Analiza el mensaje del usuario y detecta su intención específica para {store_name}.

CONTEXTO DE LA TIENDA:
- Nombre: {store_name}
- Categorías disponibles: {', '.join(categorias_soportadas)}
- Productos disponibles: {len(productos)} productos en total

HISTORIAL RECIENTE:
{context_info if context_info else "Primera interacción"}

PRODUCTOS SAMPLE (primeros 10):
{json.dumps(productos_sample, indent=2)}

MENSAJE DEL USUARIO: "{mensaje}"

EJEMPLOS DE CLASIFICACIÓN:
- "hola" → {{"intencion": "saludo", "confianza": 0.95}}
- "tienes algún vapo?" → {{"intencion": "consulta_vaporizador", "categoria_mencionada": "vaporizador", "siguiente_pregunta": "¿Lo quieres portátil o de escritorio? ¿Presupuesto aproximado?"}}
- "qué productos tienes" → {{"intencion": "consulta_catalogo", "siguiente_pregunta": "¿Qué estás buscando hoy: semillas, aceites, flores, comestibles o accesorios?"}}
- "semillas de indica" → {{"intencion": "consulta_categoria", "categoria_mencionada": "semillas"}}
- "quiero PAX 3" → {{"intencion": "intencion_compra", "producto_mencionado": "PAX 3"}}
- "no quiero aceites, busco semillas" → {{"intencion": "consulta_categoria", "categoria_mencionada": "semillas", "negaciones": ["aceites"]}}

REGLAS CRÍTICAS:
1. Si menciona "vapo", "vaporizador", "vape" → intencion: "consulta_vaporizador"
2. Si pide catálogo sin especificar → intencion: "consulta_catalogo" 
3. Si especifica categoría → intencion: "consulta_categoria"
4. Si dice "no quiero X" → agregar X a negaciones
5. Si menciona precio → extraer presupuesto_mencionado
6. Si es vaporizador, detectar tipo (portátil/escritorio)

Responde SOLO el JSON sin texto adicional."""

    try:
        # Usar parámetros de NLU del tenant
        model = nlu_params.get("modelo", "gpt-4o-mini")
        temperature = nlu_params.get("temperature_nlu", 0.3)
        max_tokens = nlu_params.get("max_tokens_nlu", 150)
        
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": final_system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"}
        )
        
        result = safe_json_loads(response.choices[0].message.content)
        
        if not result:
            raise ValueError("GPT no devolvió JSON válido")
        
        # Agregar metadata del tenant
        result["tenant_id"] = tenant_id
        result["store_name"] = store_name
        result["timestamp"] = datetime.now().isoformat()
        
        return result
        
    except Exception as e:
        print(f"🚨 Error en gpt_detect_intent para tenant {tenant_id}: {e}")
        
        # Fallback básico
        return {
            "intencion": "consulta_general",
            "confianza": 0.3,
            "sentimiento": "neutral",
            "contexto_detectado": f"Error procesando: {str(e)[:100]}",
            "tenant_id": tenant_id,
            "store_name": store_name,
            "error": str(e)
        }

# ===========================================
# ✨ GENERACIÓN DE RESPUESTA CON GPT
# ===========================================

def gpt_generate_reply(
    tenant_id: str,
    store_name: str,
    intent: Dict,
    productos: List[Dict],
    categorias_soportadas: List[str],
    db: Session
) -> str:
    """
    🎨 Generación de respuesta natural usando GPT
    🔒 MULTITENANT: Respuesta personalizada por tenant
    
    Args:
        tenant_id: ID del tenant (OBLIGATORIO PRIMERO)
        store_name: Nombre de la tienda del tenant
        intent: Resultado de detección de intención
        productos: Productos disponibles del tenant
        categorias_soportadas: Categorías del tenant
        
    Returns:
        Respuesta generada para el usuario
    """
    tenant_id = _validate_tenant_id(tenant_id)
    
    intencion = intent.get("intencion", "consulta_general")
    categoria_mencionada = intent.get("categoria_mencionada", "")
    producto_mencionado = intent.get("producto_mencionado", "")
    siguiente_pregunta = intent.get("siguiente_pregunta", "")
    presupuesto = intent.get("presupuesto_mencionado", "")
    tipo_vaporizador = intent.get("tipo_vaporizador", "no_especificado")
    negaciones = intent.get("negaciones", [])
    
    # Filtrar productos usando clasificación inteligente GPT
    productos_relevantes = []
    
    if categoria_mencionada:
        productos_relevantes = _filtrar_productos_con_gpt(productos, categoria_mencionada)
    
    elif producto_mencionado:
        # Buscar producto específico
        for prod in productos:
            if producto_mencionado.lower() in prod.get("name", "").lower():
                productos_relevantes.append(prod)
    
    # Formatear productos para el prompt (máximo 3)
    productos_formatted = ""
    if productos_relevantes:
        for i, prod in enumerate(productos_relevantes[:3], 1):
            precio = prod.get("price", 0)
            stock = prod.get("stock", 0)
            
            disponibilidad = "✅" if stock > 5 else ("⚠️" if stock > 0 else "❌")
            
            productos_formatted += f"{i}. **{prod.get('name', '')}**\n"
            productos_formatted += f"   💰 ${precio:,.0f} {disponibilidad}\n"
            if stock > 0:
                productos_formatted += f"   📦 Stock: {stock}\n"
            productos_formatted += "\n"
    
    # Context para diferentes intenciones
    context_rules = ""
    
    if intencion == "saludo":
        context_rules = f"Responde con saludo cálido + pregunta de descubrimiento sobre categorías: {', '.join(categorias_soportadas)}"
    
    elif intencion == "consulta_catalogo":
        context_rules = f"NO listes productos. Pregunta qué categoría le interesa: {', '.join(categorias_soportadas)}"
    
    elif intencion == "consulta_vaporizador":
        if tipo_vaporizador == "no_especificado":
            context_rules = "Pregunta si quiere vaporizador portátil o de escritorio + presupuesto aproximado"
        else:
            context_rules = f"Muestra máximo 3 vaporizadores {tipo_vaporizador} con precios + CTA de compra"
    
    elif intencion == "consulta_categoria" and productos_relevantes:
        context_rules = f"Muestra máximo 3 productos de {categoria_mencionada} + CTA: '¿Comparo 2 modelos o prefieres este? Para comprar, escribe: Quiero [nombre]'"
    
    elif intencion == "intencion_compra":
        context_rules = "Confirma el producto específico + precio + pasos para comprar"
    
    else:
        context_rules = "Respuesta útil y orientada a ayudar con productos de la tienda"
    
    # Obtener configuración personalizada del tenant
    tenant_config = get_tenant_ai_config(tenant_id, db)
    
    # MULTITENANT ESTRICTO: Validar que no se mezclen configs
    assert tenant_config["tenant_id"] == tenant_id, f"🚨 SECURITY: Config mismatch {tenant_config['tenant_id']} != {tenant_id}"
    
    style_overrides = tenant_config.get("style_overrides", {})
    nlg_params = tenant_config.get("nlg_params", {})
    
    # Construir prompt final con configuración del tenant
    final_system_prompt = build_final_system_prompt(tenant_id, tenant_config)
    
    # Prompt para generación natural con estilo personalizado
    prompt = f"""Genera una respuesta natural para {store_name} según la configuración específica del tenant.

CONTEXTO:
- Tienda: {store_name}
- Intención detectada: {intencion}
- Categoría: {categoria_mencionada}
- Producto específico: {producto_mencionado}
- Presupuesto mencionado: {presupuesto}
- Productos rechazados: {', '.join(negaciones)}

PRODUCTOS RELEVANTES:
{productos_formatted if productos_formatted else "No hay productos específicos para mostrar"}

REGLAS DE RESPUESTA:
{context_rules}

ESTILO:
- Español natural, cercano pero profesional
- Formato WhatsApp (párrafos cortos)
- Máximo 2 emojis
- No inventes políticas ni links
- No uses "gracias por contactarnos" ni texto corporativo
- Varía las frases (no siempre "¿En qué puedo ayudarte?")
- Si muestras productos, máximo 3
- Siempre incluye CTA clara para siguiente paso

EJEMPLOS DE TONO ESPERADO:
- "¡Hola! Bienvenido a {store_name} 👋 ¿Qué estás buscando hoy: semillas, aceites, flores, comestibles o accesorios?"
- "¿Lo quieres portátil o de escritorio? ¿Tienes un presupuesto aproximado? 🤔"
- "Aquí tienes nuestros vaporizadores portátiles más populares: [lista] ¿Comparo 2 modelos o prefieres alguno?"

Genera la respuesta:"""

    try:
        # Usar parámetros de NLG del tenant
        model = nlg_params.get("modelo", "gpt-4o-mini")
        temperature = nlg_params.get("temperature_nlg", 0.7)
        max_tokens = nlg_params.get("max_tokens_nlg", 300)
        
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": final_system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        reply = response.choices[0].message.content.strip()
        
        # Validar que no esté vacía
        if not reply:
            return f"¡Hola! Bienvenido a {store_name} 👋 ¿En qué puedo ayudarte hoy?"
        
        # Aplicar style_overrides del tenant
        final_reply = apply_style_overrides(reply, style_overrides)
        
        return final_reply
        
    except Exception as e:
        print(f"🚨 Error en gpt_generate_reply para tenant {tenant_id}: {e}")
        
        # Fallback básico
        return f"¡Hola! Soy el asistente de {store_name}. ¿En qué puedo ayudarte? 😊"

# ===========================================
# 🎭 FUNCIÓN ORQUESTADORA PRINCIPAL
# ===========================================

def handle_message_with_context(
    tenant_id: str,
    store_name: str,
    telefono: str,
    mensaje: str,
    productos: List[Dict],
    categorias_soportadas: List[str],
    history: Optional[List[Dict]] = None,
    db: Optional[Session] = None
) -> Tuple[str, Dict]:
    """
    🎯 Función orquestadora principal que maneja mensaje completo
    🔒 MULTITENANT: Completamente aislado por tenant_id
    
    Args:
        tenant_id: ID del tenant (OBLIGATORIO PRIMERO)
        store_name: Nombre de la tienda del tenant
        telefono: Número de teléfono del usuario
        mensaje: Mensaje del usuario
        productos: Lista de productos del tenant
        categorias_soportadas: Categorías que maneja el tenant
        history: Historial de conversación del tenant
        db: Sesión de BD para logging (opcional)
        
    Returns:
        Tuple (respuesta_generada, metadata)
    """
    tenant_id = _validate_tenant_id(tenant_id)
    start_time = datetime.now()
    
    if not mensaje or not isinstance(mensaje, str):
        return f"¡Hola! Bienvenido a {store_name} 👋", {"error": "mensaje_vacio"}
    
    if not productos:
        productos = []
    
    if not history:
        history = []
    
    if not categorias_soportadas:
        categorias_soportadas = ["semillas", "aceites", "flores", "comestibles", "accesorios"]
    
    try:
        # 0. 🔧 Cargar configuración del tenant
        if db:
            tenant_cfg = get_tenant_ai_config(tenant_id, db)
            print(f"📋 Config cargada para tenant {tenant_id}: version {tenant_cfg.get('version', 0)}")
        
        # 1. 🧠 Detectar intención con GPT personalizada
        intent_result = gpt_detect_intent(
            tenant_id=tenant_id,
            store_name=store_name,
            mensaje=mensaje,
            history=history,
            productos=productos,
            categorias_soportadas=categorias_soportadas,
            db=db
        )
        
        # 2. ✨ Generar respuesta con GPT personalizada
        respuesta = gpt_generate_reply(
            tenant_id=tenant_id,
            store_name=store_name,
            intent=intent_result,
            productos=productos,
            categorias_soportadas=categorias_soportadas,
            db=db
        )
        
        # 3. 📊 Calcular métricas
        end_time = datetime.now()
        duration_ms = int((end_time - start_time).total_seconds() * 1000)
        
        # 4. 📝 Actualizar contexto del tenant (si hay BD)
        conversation_id = None
        if db:
            try:
                conversation_id = _log_conversation_to_db(
                    db=db,
                    tenant_id=tenant_id,
                    telefono=telefono,
                    mensaje=mensaje,
                    respuesta=respuesta,
                    intent_result=intent_result,
                    duration_ms=duration_ms
                )
            except Exception as e:
                print(f"⚠️ Error logging conversation for tenant {tenant_id}: {e}")
        
        # 5. 📈 Metadata para análisis
        metadata = {
            "tenant_id": tenant_id,
            "store_name": store_name,
            "conversation_id": conversation_id,
            "intent": intent_result.get("intencion"),
            "confidence": intent_result.get("confianza", 0),
            "intent_confidence": intent_result.get("confianza", 0),  # Para compatibilidad con flow_chat_service
            "response_time_ms": duration_ms,  # Para compatibilidad con flow_chat_service
            "category": intent_result.get("categoria_mencionada"),
            "product": intent_result.get("producto_mencionado"),
            "sentiment": intent_result.get("sentimiento"),
            "duration_ms": duration_ms,
            "products_shown": len([p for p in productos if intent_result.get("categoria_mencionada", "").lower() in p.get("name", "").lower()][:3]),
            "timestamp": start_time.isoformat(),
            "ai_version": "v3.0-gpt-max"
        }
        
        return respuesta, metadata
        
    except Exception as e:
        print(f"🚨 Error crítico en handle_message_with_context para tenant {tenant_id}: {e}")
        
        # Fallback de emergencia
        fallback_response = f"¡Hola! Bienvenido a {store_name}. Estoy experimentando dificultades técnicas pero puedo ayudarte. ¿Qué estás buscando?"
        
        return fallback_response, {
            "tenant_id": tenant_id,
            "error": str(e),
            "fallback_used": True,
            "timestamp": start_time.isoformat()
        }

# ===========================================
# 📝 LOGGING Y PERSISTENCIA
# ===========================================

def _log_conversation_to_db(
    db: Session,
    tenant_id: str,
    telefono: str,
    mensaje: str,
    respuesta: str,
    intent_result: Dict,
    duration_ms: int
) -> Optional[int]:
    """
    📝 Registra conversación en BD con aislamiento por tenant
    
    Args:
        db: Sesión de BD
        tenant_id: ID del tenant
        telefono: Teléfono (últimos 4 dígitos solo)
        mensaje: Mensaje del usuario
        respuesta: Respuesta generada
        intent_result: Resultado de detección de intención
        duration_ms: Duración en ms
        
    Returns:
        ID de conversación o None si error
    """
    try:
        query = text("""
            INSERT INTO conversation_history 
            (tenant_id, telefono, mensaje_usuario, respuesta_bot, 
             intencion_detectada, confianza, sentimiento, duracion_respuesta_ms, metadata_ia)
            VALUES (:tenant_id, :telefono, :mensaje_usuario, :respuesta_bot,
                    :intencion, :confianza, :sentimiento, :duracion_ms, :metadata)
            RETURNING id
        """)
        
        result = db.execute(query, {
            "tenant_id": tenant_id,
            "telefono": telefono[-4:] if len(telefono) > 4 else telefono,  # Solo últimos 4 para privacidad
            "mensaje_usuario": mensaje,
            "respuesta_bot": respuesta,
            "intencion": intent_result.get("intencion"),
            "confianza": intent_result.get("confianza", 0),
            "sentimiento": intent_result.get("sentimiento"),
            "duracion_ms": duration_ms,
            "metadata": json.dumps(intent_result)
        })
        
        db.commit()
        return result.scalar()
        
    except Exception as e:
        print(f"Error logging to DB for tenant {tenant_id}: {e}")
        db.rollback()
        return None

# ===========================================
# 🔧 FUNCIONES DE UTILIDAD ADICIONALES
# ===========================================

def get_tenant_context_cache(tenant_id: str, telefono: str) -> Dict:
    """
    🗄️ Obtiene contexto cacheado del tenant
    🔒 Cache namespaced por tenant_id
    """
    tenant_id = _validate_tenant_id(tenant_id)
    cache_key = _namespace_cache_key(tenant_id, f"context:{telefono}")
    
    # TODO: Implementar cache Redis si es necesario
    # Por ahora retorna contexto vacío
    return {"primera_interaccion": True, "history": []}

def update_tenant_context_cache(tenant_id: str, telefono: str, context: Dict) -> None:
    """
    💾 Actualiza contexto cacheado del tenant
    🔒 Cache namespaced por tenant_id
    """
    tenant_id = _validate_tenant_id(tenant_id)
    cache_key = _namespace_cache_key(tenant_id, f"context:{telefono}")
    
    # TODO: Implementar cache Redis si es necesario
    # context["updated_at"] = datetime.now().isoformat()
    pass

def validate_products_for_tenant(tenant_id: str, productos: List[Dict]) -> List[Dict]:
    """
    🔒 Valida que todos los productos pertenezcan al tenant
    
    Args:
        tenant_id: ID del tenant
        productos: Lista de productos a validar
        
    Returns:
        Lista de productos validados
        
    Raises:
        ValueError: Si algún producto no pertenece al tenant
    """
    tenant_id = _validate_tenant_id(tenant_id)
    
    validated_products = []
    for prod in productos:
        product_tenant = prod.get("client_id") or prod.get("tenant_id")
        
        if product_tenant != tenant_id:
            raise ValueError(f"🚨 CROSS-TENANT PRODUCT DETECTED: producto {prod.get('id')} pertenece a {product_tenant}, no a {tenant_id}")
        
        validated_products.append(prod)
    
    return validated_products

# ===========================================
# 🧪 FUNCIÓN PRINCIPAL LEGACY (COMPATIBILIDAD)
# ===========================================

def process_message_with_ai_improvements(
    db: Session,
    telefono: str,
    tenant_id: str,
    mensaje: str,
    productos: List[Dict],
    tenant_info: Dict
) -> Tuple[str, Dict]:
    """
    🔄 Función legacy para compatibilidad con código existente
    Redirige a la nueva función orquestadora
    """
    store_name = tenant_info.get("name", "nuestra tienda")
    categorias = ["semillas", "aceites", "flores", "comestibles", "accesorios", "vaporizador"]
    
    # Validar productos del tenant
    try:
        productos_validados = validate_products_for_tenant(tenant_id, productos)
    except ValueError as e:
        print(f"🚨 Producto validation error: {e}")
        productos_validados = []
    
    return handle_message_with_context(
        tenant_id=tenant_id,
        store_name=store_name,
        telefono=telefono,
        mensaje=mensaje,
        productos=productos_validados,
        categorias_soportadas=categorias,
        history=[],
        db=db
    )


# ===========================================
# 🎨 FUNCIONES HELPER PARA STYLE OVERRIDES
# ===========================================

def apply_style_overrides(text: str, style_overrides: Dict[str, Any]) -> str:
    """
    🎨 Aplicar configuración de estilo personalizada del tenant
    
    Args:
        text: Texto original generado
        style_overrides: Configuración de estilo del tenant
        
    Returns:
        Texto con estilo aplicado
    """
    if not text or not style_overrides:
        return text
    
    result = text
    
    # Aplicar límite de caracteres
    limite_chars = style_overrides.get("limite_respuesta_caracteres", 500)
    if limite_chars and len(result) > limite_chars:
        result = truncate_to_chars(result, limite_chars)
    
    # Aplicar CTA principal si está configurado
    cta_principal = style_overrides.get("cta_principal")
    if cta_principal and not any(trigger in result.lower() for trigger in ["comprar", "precio", "?"]):
        result += f"\n\n{cta_principal}"
    
    # Ajustar emojis según configuración
    usar_emojis = style_overrides.get("usar_emojis", True)
    if not usar_emojis:
        # Remover emojis si están deshabilitados
        import re
        emoji_pattern = re.compile("["
                                 u"\U0001F600-\U0001F64F"  # emoticons
                                 u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                 u"\U0001F680-\U0001F6FF"  # transport & map
                                 u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                 "]+", flags=re.UNICODE)
        result = emoji_pattern.sub('', result)
    
    # Aplicar tono si está especificado
    tono = style_overrides.get("tono")
    if tono == "formal":
        result = result.replace("!", ".")
        result = result.replace("🤔", "")
        result = result.replace("😊", "")
    elif tono == "casual":
        if not result.endswith(("!", "?", ".")):
            result += " 😊"
    
    return result.strip()


def truncate_to_chars(text: str, limit: int) -> str:
    """
    ✂️ Truncar texto respetando palabras completas
    
    Args:
        text: Texto a truncar
        limit: Límite de caracteres
        
    Returns:
        Texto truncado con "..." si fue necesario
    """
    if not text or len(text) <= limit:
        return text
    
    # Buscar último espacio antes del límite
    truncated = text[:limit]
    last_space = truncated.rfind(' ')
    
    if last_space > limit * 0.8:  # Si el espacio está cerca del límite
        truncated = truncated[:last_space]
    
    return truncated.rstrip() + "..."


# ===========================================
# 🔧 FUNCIÓN DE PREVIEW PARA TESTING
# ===========================================

async def generate_preview_response(
    tenant_id: str,
    message: str, 
    prompt_config: Dict[str, Any],
    include_products: bool = True,
    db: Session = None
) -> Tuple[str, Dict[str, Any]]:
    """
    🔬 Generar respuesta de preview para testing de configuración
    Usado por el endpoint de preview sin guardar cambios
    """
    tenant_id = _validate_tenant_id(tenant_id)
    
    start_time = time.time()
    
    try:
        # Mock de productos para preview
        mock_products = []
        if include_products:
            mock_products = [
                {"name": "Producto Demo 1", "price": 10000, "category": "demo", "stock": 5},
                {"name": "Producto Demo 2", "price": 15000, "category": "demo", "stock": 3}
            ]
        
        # Usar configuración de preview
        test_config = {
            "system_prompt": prompt_config.get("system_prompt", ""),
            "style_overrides": prompt_config.get("style_overrides", {}),
            "nlu_params": prompt_config.get("nlu_params", {}),
            "nlg_params": prompt_config.get("nlg_params", {}),
            "tenant_id": tenant_id
        }
        
        # Generar respuesta usando la configuración de prueba
        response, metrics_data = handle_message_with_context(
            tenant_id=tenant_id,
            store_name="Tienda Demo",
            telefono="+56999999999",  # Teléfono de prueba
            mensaje=message,
            productos=mock_products,
            categorias_soportadas=["demo", "prueba"],
            history=[],
            db=db
        )
        
        processing_time = int((time.time() - start_time) * 1000)
        
        metrics = {
            "tokens_used": {"nlu": 50, "nlg": 100},  # Mock values
            "confidence_score": 0.85,
            "detected_intent": metrics_data.get("intencion", "unknown"),
            "processing_time_ms": processing_time
        }
        
        return response, metrics
        
    except Exception as e:
        raise Exception(f"Error en preview para tenant {tenant_id}: {str(e)}")