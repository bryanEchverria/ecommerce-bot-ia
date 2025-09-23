"""
Sistema de Configuración Multi-Tenant Dinámico y Centralizado
🔒 100% Multi-tenant - Sin hardcoding de ningún tenant específico
🚀 Escalable para cualquier tipo de negocio futuro
"""
import json
import os
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import text
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta

@dataclass
class TenantConfig:
    """
    Configuración completa de un tenant obtenida dinámicamente de BD
    """
    tenant_id: str
    business_name: str
    business_type: str
    currency: str
    language: str
    timezone: str
    
    # Configuración del bot
    bot_personality: str
    use_emojis: bool
    response_length: str  # 'short', 'medium', 'long'
    greeting_style: str   # 'formal', 'casual', 'friendly'
    
    # Configuración de IA
    ai_model: str
    ai_temperature: float
    max_tokens: int
    
    # Metadatos
    created_at: datetime
    updated_at: datetime

@dataclass
class ProductCategory:
    """
    Categoría de productos extraída dinámicamente por GPT
    """
    name: str
    keywords: List[str]
    product_count: int
    available_count: int

def get_tenant_config_from_db(db: Session, tenant_id: str) -> Optional[TenantConfig]:
    """
    Obtiene configuración completa del tenant desde múltiples tablas de BD
    100% dinámico - no asume nada sobre el tipo de negocio
    """
    try:
        # Consulta principal del tenant
        tenant_query = text("""
            SELECT 
                tc.id as tenant_id,
                tc.name as business_name,
                tc.slug,
                tc.created_at,
                tc.updated_at,
                -- Configuración de negocio (con defaults seguros)
                COALESCE(tc.business_type, 'general') as business_type,
                COALESCE(tc.currency, 'USD') as currency,
                COALESCE(tc.language, 'es') as language,
                COALESCE(tc.timezone, 'UTC') as timezone
            FROM tenant_clients tc 
            WHERE tc.id = :tenant_id
        """)
        
        tenant_result = db.execute(tenant_query, {"tenant_id": tenant_id}).first()
        
        if not tenant_result:
            print(f"⚠️ Tenant {tenant_id} no encontrado en BD")
            return None
        
        # Configuración del bot desde tenant_prompts (si existe)
        bot_config_query = text("""
            SELECT 
                tp.system_prompt,
                tp.style_overrides,
                tp.nlg_params,
                tp.nlu_params,
                tp.version,
                tp.updated_at
            FROM tenant_prompts tp 
            WHERE tp.tenant_id = :tenant_id AND tp.is_active = true
            ORDER BY tp.created_at DESC
            LIMIT 1
        """)
        
        bot_config_result = db.execute(bot_config_query, {"tenant_id": tenant_id}).first()
        
        # Parsear configuración de estilo
        style_config = {}
        ai_config = {}
        
        if bot_config_result and bot_config_result.style_overrides:
            try:
                style_config = json.loads(bot_config_result.style_overrides) if isinstance(bot_config_result.style_overrides, str) else bot_config_result.style_overrides
            except (json.JSONDecodeError, TypeError):
                style_config = {}
        
        if bot_config_result and bot_config_result.nlg_params:
            try:
                ai_config = json.loads(bot_config_result.nlg_params) if isinstance(bot_config_result.nlg_params, str) else bot_config_result.nlg_params
            except (json.JSONDecodeError, TypeError):
                ai_config = {}
        
        # Construir configuración completa con defaults seguros
        config = TenantConfig(
            tenant_id=tenant_result.tenant_id,
            business_name=tenant_result.business_name or f"Tienda {tenant_id}",
            business_type=tenant_result.business_type,
            currency=tenant_result.currency,
            language=tenant_result.language,
            timezone=tenant_result.timezone,
            
            # Bot config con defaults dinámicos
            bot_personality=style_config.get('tono', 'profesional_amigable'),
            use_emojis=style_config.get('usar_emojis', True),
            response_length=style_config.get('longitud_respuesta', 'medium'),
            greeting_style=style_config.get('estilo_saludo', 'friendly'),
            
            # IA config con defaults seguros
            ai_model=ai_config.get('modelo', 'gpt-4o-mini'),
            ai_temperature=float(ai_config.get('temperature_nlg', 0.7)),
            max_tokens=int(ai_config.get('max_tokens_nlg', 300)),
            
            created_at=tenant_result.created_at,
            updated_at=bot_config_result.updated_at if bot_config_result else tenant_result.updated_at
        )
        
        print(f"✅ Configuración cargada para {config.business_name} ({config.business_type})")
        return config
        
    except Exception as e:
        print(f"❌ Error cargando configuración de tenant {tenant_id}: {e}")
        return None

def get_fallback_config(tenant_id: str) -> TenantConfig:
    """
    Configuración de fallback genérica para cualquier tenant
    No asume nada sobre el tipo de negocio
    """
    return TenantConfig(
        tenant_id=tenant_id,
        business_name=f"Tienda {tenant_id}",
        business_type="general",
        currency="USD",
        language="es",
        timezone="UTC",
        
        bot_personality="profesional_amigable",
        use_emojis=True,
        response_length="medium",
        greeting_style="friendly",
        
        ai_model="gpt-4o-mini",
        ai_temperature=0.7,
        max_tokens=300,
        
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

def extract_dynamic_categories_from_products(productos: List[Dict]) -> List[ProductCategory]:
    """
    Extrae categorías dinámicamente de los productos usando GPT
    100% adaptable a cualquier tipo de negocio
    """
    if not productos:
        return []
    
    try:
        import openai
        client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Preparar muestra de productos
        productos_muestra = []
        for i, prod in enumerate(productos[:20]):
            productos_muestra.append(f"{i}. {prod.get('name', '')} - {prod.get('description', '')}")
        
        # Prompt genérico para cualquier tipo de negocio
        categorias_prompt = f"""Analiza estos productos y extrae categorías naturales que un cliente usaría.

PRODUCTOS:
{chr(10).join(productos_muestra)}

INSTRUCCIONES:
1. Identifica 3-6 categorías principales basándote SOLO en los productos mostrados
2. Usa términos que los clientes usarían naturalmente al buscar
3. Cada categoría debe ser una palabra simple (ej: "aceites", "tecnología", "ropa")
4. NO uses categorías predefinidas - analiza lo que realmente vendes
5. Ordena por importancia/frecuencia

RESPONDE solo los nombres de categorías separados por comas:"""
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": categorias_prompt}],
            temperature=0.2,
            max_tokens=80
        )
        
        categorias_texto = response.choices[0].message.content.strip()
        categorias_nombres = [cat.strip().lower() for cat in categorias_texto.split(',') if cat.strip()]
        
        # Construir objetos ProductCategory con conteos
        categorias_resultado = []
        for categoria_nombre in categorias_nombres[:6]:
            # Contar productos que pertenecen a esta categoría
            productos_categoria = []
            disponibles = 0
            
            for producto in productos:
                nombre_lower = producto.get('name', '').lower()
                desc_lower = producto.get('description', '').lower()
                
                # Búsqueda flexible por coincidencias
                if (categoria_nombre in nombre_lower or 
                    categoria_nombre in desc_lower or
                    any(keyword in nombre_lower for keyword in categoria_nombre.split())):
                    productos_categoria.append(producto)
                    if producto.get('stock', 0) > 0:
                        disponibles += 1
            
            if productos_categoria:  # Solo agregar si tiene productos
                categoria = ProductCategory(
                    name=categoria_nombre.title(),
                    keywords=[categoria_nombre],
                    product_count=len(productos_categoria),
                    available_count=disponibles
                )
                categorias_resultado.append(categoria)
        
        print(f"🧠 GPT extrajo {len(categorias_resultado)} categorías dinámicas")
        return categorias_resultado
        
    except Exception as e:
        print(f"❌ Error extrayendo categorías dinámicamente: {e}")
        # Fallback: categoría genérica
        return [ProductCategory(
            name="Productos",
            keywords=["productos"],
            product_count=len(productos),
            available_count=sum(1 for p in productos if p.get('stock', 0) > 0)
        )]

def get_dynamic_business_insights(tenant_config: TenantConfig, productos: List[Dict]) -> Dict[str, Any]:
    """
    Genera insights dinámicos del negocio basado en productos reales
    Útil para personalizar respuestas del bot
    """
    if not productos:
        return {
            "total_products": 0,
            "available_products": 0,
            "avg_price": 0,
            "price_range": "N/A",
            "top_keywords": [],
            "business_focus": "general"
        }
    
    # Calcular estadísticas básicas
    precios = [float(p.get('price', 0)) for p in productos if p.get('price')]
    productos_disponibles = [p for p in productos if p.get('stock', 0) > 0]
    
    # Extraer palabras clave comunes de nombres de productos
    todas_palabras = []
    for producto in productos:
        nombre = producto.get('name', '').lower()
        palabras = [p for p in nombre.split() if len(p) > 3]
        todas_palabras.extend(palabras)
    
    # Contar frecuencia de palabras
    from collections import Counter
    contador_palabras = Counter(todas_palabras)
    top_keywords = [palabra for palabra, count in contador_palabras.most_common(10)]
    
    # Inferir enfoque del negocio basado en palabras clave
    business_focus = "general"
    if any(keyword in ' '.join(top_keywords) for keyword in ['aceite', 'cannabis', 'cbd', 'thc']):
        business_focus = "cannabis"
    elif any(keyword in ' '.join(top_keywords) for keyword in ['tech', 'gaming', 'pc', 'gaming']):
        business_focus = "technology"
    elif any(keyword in ' '.join(top_keywords) for keyword in ['ropa', 'camiseta', 'pantalon']):
        business_focus = "clothing"
    
    return {
        "total_products": len(productos),
        "available_products": len(productos_disponibles),
        "avg_price": sum(precios) / len(precios) if precios else 0,
        "price_range": f"${min(precios):,.0f} - ${max(precios):,.0f}" if precios else "N/A",
        "top_keywords": top_keywords[:5],
        "business_focus": business_focus,
        "currency": tenant_config.currency
    }

def format_currency(amount: float, currency: str) -> str:
    """
    Formatea cantidad según la moneda del tenant
    """
    currency_symbols = {
        'USD': '$',
        'EUR': '€',
        'CLP': '$',
        'MXN': '$',
        'COP': '$',
        'ARS': '$'
    }
    
    symbol = currency_symbols.get(currency, '$')
    return f"{symbol}{amount:,.0f}"

def get_dynamic_greeting_template(tenant_config: TenantConfig, categorias: List[ProductCategory]) -> str:
    """
    Genera template de saludo dinámico basado en configuración y categorías reales
    """
    empresa = tenant_config.business_name
    estilo = tenant_config.greeting_style
    usar_emojis = tenant_config.use_emojis
    
    # Texto de categorías dinámico
    if categorias:
        categorias_texto = ", ".join([cat.name.lower() for cat in categorias[:4]])
    else:
        categorias_texto = "nuestros productos"
    
    # Templates por estilo
    if estilo == "formal":
        emoji = " 🏢" if usar_emojis else ""
        return f"Buenos días. Bienvenido a {empresa}{emoji}. ¿En qué podemos asistirle hoy? Ofrecemos: {categorias_texto}."
    
    elif estilo == "casual":
        emoji = " 😊" if usar_emojis else ""
        return f"¡Hola! Bienvenido a {empresa}{emoji}. ¿Qué necesitas? Tenemos: {categorias_texto}."
    
    else:  # friendly (default)
        emoji = " 👋" if usar_emojis else ""
        return f"¡Hola! Bienvenido a {empresa}{emoji}. ¿Qué estás buscando hoy? Tenemos: {categorias_texto}."

# Cache en memoria para configuraciones (evitar consultas repetidas)
_config_cache: Dict[str, TenantConfig] = {}
_cache_expiry: Dict[str, datetime] = {}
CACHE_TTL_MINUTES = 10

def get_cached_tenant_config(db: Session, tenant_id: str) -> TenantConfig:
    """
    Obtiene configuración con cache para performance
    """
    now = datetime.utcnow()
    
    # Verificar cache
    if (tenant_id in _config_cache and 
        tenant_id in _cache_expiry and 
        _cache_expiry[tenant_id] > now):
        return _config_cache[tenant_id]
    
    # Cargar desde BD
    config = get_tenant_config_from_db(db, tenant_id)
    if not config:
        config = get_fallback_config(tenant_id)
    
    # Guardar en cache
    _config_cache[tenant_id] = config
    _cache_expiry[tenant_id] = now + timedelta(minutes=CACHE_TTL_MINUTES)
    
    return config

def clear_tenant_cache(tenant_id: str = None):
    """
    Limpia cache de configuración (útil después de updates)
    """
    if tenant_id:
        _config_cache.pop(tenant_id, None)
        _cache_expiry.pop(tenant_id, None)
    else:
        _config_cache.clear()
        _cache_expiry.clear()