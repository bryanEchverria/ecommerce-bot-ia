"""
Esquemas Pydantic para configuración de prompts por tenant
Incluye validación completa, límites de seguridad y sanitización
"""
from pydantic import BaseModel, Field, validator, root_validator
from typing import Optional, Dict, Any, List, Literal, Union
from datetime import datetime
import re


class StyleOverrides(BaseModel):
    """Configuración de estilo para respuestas del bot"""
    tono: Optional[Literal["formal", "casual", "amigable", "profesional"]] = "amigable"
    usar_emojis: Optional[bool] = True
    emojis_permitidos: Optional[List[str]] = Field(default_factory=lambda: ["👋", "🌿", "✅", "❌", "🛒", "💰"])
    cta_principal: Optional[str] = Field(None, max_length=100)  # Call-to-action principal
    limite_respuesta_caracteres: Optional[int] = Field(500, ge=100, le=2000)
    incluir_branding: Optional[bool] = True
    incluir_contexto_empresa: Optional[bool] = True  # Alias for compatibility
    
    @validator('emojis_permitidos')
    def validate_emojis(cls, v):
        if v and len(v) > 20:
            raise ValueError("Máximo 20 emojis permitidos")
        return v
    
    @validator('cta_principal')
    def validate_cta(cls, v):
        if v:
            # Sanitizar CTA - no permitir HTML, scripts o caracteres maliciosos
            sanitized = re.sub(r'[<>"\'\{\}]', '', v.strip())
            if len(sanitized) != len(v.strip()):
                raise ValueError("CTA contiene caracteres no permitidos")
            return sanitized
        return v


class NLUParams(BaseModel):
    """Parámetros para Natural Language Understanding"""
    modelo: Optional[Literal["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"]] = "gpt-4o-mini"
    temperature_nlu: Optional[float] = Field(0.3, ge=0.0, le=1.0)
    max_tokens_nlu: Optional[int] = Field(150, ge=50, le=500)
    confidence_threshold: Optional[float] = Field(0.7, ge=0.1, le=1.0)
    enable_intent_detection: Optional[bool] = True
    enable_entity_extraction: Optional[bool] = True


class DatabaseQuery(BaseModel):
    """Configuración de consulta SQL dinámica para el bot"""
    name: str = Field(..., min_length=1, max_length=50, description="Nombre descriptivo de la query")
    description: Optional[str] = Field(None, max_length=200, description="Descripción de qué información proporciona")
    sql_template: str = Field(..., min_length=10, max_length=1000, description="Template SQL con placeholders")
    parameters: Optional[List[str]] = Field(default_factory=list, description="Parámetros que acepta la query")
    max_results: Optional[int] = Field(10, ge=1, le=100, description="Máximo número de resultados")
    cache_ttl_seconds: Optional[int] = Field(300, ge=0, le=3600, description="TTL del cache en segundos")
    is_active: Optional[bool] = Field(True, description="Si la query está activa")
    
    @validator('sql_template')
    def validate_sql_template(cls, v):
        # Validaciones básicas de seguridad SQL
        forbidden_keywords = ['drop', 'delete', 'update', 'insert', 'alter', 'create', 'truncate', '--', ';']
        v_lower = v.lower()
        for keyword in forbidden_keywords:
            if keyword in v_lower:
                raise ValueError(f"SQL template no puede contener '{keyword}' por seguridad")
        
        # Debe empezar con SELECT
        if not v_lower.strip().startswith('select'):
            raise ValueError("SQL template debe empezar con SELECT")
            
        return v.strip()

class DatabaseQueries(BaseModel):
    """Conjunto de queries SQL dinámicas configurables"""
    products_query: Optional[DatabaseQuery] = Field(
        default=DatabaseQuery(
            name="productos_catalogo",
            description="Consulta productos disponibles por categoría",
            sql_template="SELECT name, description, price, sale_price, stock, category FROM products WHERE client_id = $client_id AND status = 'active' AND category ILIKE $category ORDER BY name LIMIT $limit",
            parameters=["client_id", "category", "limit"],
            max_results=20
        ),
        description="Query para consultar productos"
    )
    
    campaigns_query: Optional[DatabaseQuery] = Field(
        default=DatabaseQuery(
            name="campanas_activas",
            description="Consulta campañas publicitarias activas",
            sql_template="SELECT name, start_date, end_date, budget, status FROM campaigns WHERE client_id = $client_id AND status = 'active' AND end_date > NOW() ORDER BY start_date LIMIT $limit",
            parameters=["client_id", "limit"],
            max_results=10
        ),
        description="Query para consultar campañas"
    )
    
    discounts_query: Optional[DatabaseQuery] = Field(
        default=DatabaseQuery(
            name="descuentos_vigentes",
            description="Consulta descuentos y promociones vigentes",
            sql_template="SELECT name, type, value, target, category FROM discounts WHERE client_id = $client_id AND is_active = true ORDER BY value DESC LIMIT $limit",
            parameters=["client_id", "limit"],
            max_results=15
        ),
        description="Query para consultar descuentos"
    )
    
    custom_queries: Optional[List[DatabaseQuery]] = Field(
        default_factory=list,
        max_items=5,
        description="Queries personalizadas adicionales"
    )

class NLGParams(BaseModel):
    """Parámetros para Natural Language Generation"""
    modelo: Optional[Literal["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"]] = "gpt-4o-mini" 
    temperature_nlg: Optional[float] = Field(0.7, ge=0.0, le=1.0)
    max_tokens_nlg: Optional[int] = Field(300, ge=100, le=1000)
    max_items_catalog: Optional[int] = Field(5, ge=1, le=20)
    max_items_category: Optional[int] = Field(10, ge=1, le=50)
    include_prices: Optional[bool] = True
    include_stock: Optional[bool] = True


class TenantPromptBase(BaseModel):
    """Esquema base para configuración de prompts"""
    system_prompt: str = Field(..., min_length=50, max_length=4000)
    style_overrides: Optional[StyleOverrides] = None
    nlu_params: Optional[NLUParams] = None
    nlg_params: Optional[NLGParams] = None
    database_queries: Optional[DatabaseQueries] = Field(default_factory=DatabaseQueries, description="Queries SQL dinámicas para consultar BD")
    
    @validator('system_prompt')
    def validate_system_prompt(cls, v):
        """Validar y sanitizar el prompt del sistema"""
        # Lista de frases prohibidas por seguridad
        prohibited_phrases = [
            "ignore", "override", "jailbreak", "pretend", "act as",
            "olvidate", "ignora", "simula ser", "eres ahora",
            "<script>", "</script>", "javascript:", "eval(",
            "exec(", "import ", "from ", "__", "getattr"
        ]
        
        v_lower = v.lower()
        for phrase in prohibited_phrases:
            if phrase in v_lower:
                raise ValueError(f"Prompt contiene frase prohibida: '{phrase}'")
        
        # Verificar que no contenga instrucciones maliciosas
        malicious_patterns = [
            r'ignore\s+previous\s+instructions',
            r'forget\s+everything\s+above',
            r'you\s+are\s+now\s+a',
            r'act\s+as\s+if\s+you\s+are',
            r'pretend\s+to\s+be'
        ]
        
        for pattern in malicious_patterns:
            if re.search(pattern, v_lower):
                raise ValueError("Prompt contiene instrucciones potencialmente maliciosas")
        
        # Verificar longitud de líneas (evitar prompts muy largos en una sola línea)
        lines = v.split('\n')
        for line in lines:
            if len(line) > 200:
                raise ValueError("Líneas del prompt no pueden exceder 200 caracteres")
        
        return v.strip()
    
    @root_validator(skip_on_failure=True)
    def validate_complete_config(cls, values):
        """Validar que la configuración completa sea coherente"""
        style = values.get('style_overrides')
        nlg = values.get('nlg_params')
        
        if style and nlg:
            # Si se limita respuesta por caracteres, ajustar tokens
            if style.limite_respuesta_caracteres and nlg.max_tokens_nlg:
                # Aproximadamente 3-4 caracteres por token (ser más flexible)
                estimated_tokens = style.limite_respuesta_caracteres // 3
                if nlg.max_tokens_nlg > estimated_tokens * 2:  # Más tolerante
                    raise ValueError(f"max_tokens_nlg ({nlg.max_tokens_nlg}) muy alto para límite de {style.limite_respuesta_caracteres} caracteres. Máximo recomendado: {estimated_tokens * 2}")
        
        return values


class TenantPromptCreate(TenantPromptBase):
    """Esquema para crear nueva configuración de prompt"""
    pass


class TenantPromptUpdate(BaseModel):
    """Esquema para actualizar configuración existente"""
    system_prompt: Optional[str] = Field(None, min_length=50, max_length=4000)
    style_overrides: Optional[StyleOverrides] = None
    nlu_params: Optional[NLUParams] = None
    nlg_params: Optional[NLGParams] = None
    
    @validator('system_prompt')
    def validate_system_prompt(cls, v):
        if v is not None:
            return TenantPromptBase.__validators__['system_prompt'](v)
        return v


class TenantPromptResponse(TenantPromptBase):
    """Esquema de respuesta para configuración de prompt"""
    id: str
    tenant_id: str
    version: int
    is_active: bool
    updated_by: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TenantPromptPreviewRequest(BaseModel):
    """Esquema para request de preview de respuesta"""
    prompt_config: TenantPromptBase
    test_message: str = Field(..., min_length=1, max_length=500)
    include_products: Optional[bool] = True
    
    @validator('test_message')
    def validate_test_message(cls, v):
        # Sanitizar mensaje de prueba
        sanitized = re.sub(r'[<>"\'\{\}]', '', v.strip())
        if not sanitized:
            raise ValueError("Mensaje de prueba no puede estar vacío después de sanitización")
        return sanitized


class TenantPromptPreviewResponse(BaseModel):
    """Esquema de respuesta para preview"""
    bot_response: str
    processing_time_ms: int
    tokens_used: Dict[str, int]  # {nlu: X, nlg: Y}
    confidence_score: Optional[float] = None
    detected_intent: Optional[str] = None
    warnings: Optional[List[str]] = None


class TenantPromptAuditLogResponse(BaseModel):
    """Esquema para logs de auditoría"""
    id: str
    tenant_id: str
    action: str
    changes_diff: Optional[Dict[str, Any]] = None
    previous_version: Optional[int] = None
    new_version: Optional[int] = None
    performed_by: str
    performed_at: datetime
    ip_address: Optional[str] = None
    
    class Config:
        from_attributes = True


class TenantPromptRollbackRequest(BaseModel):
    """Esquema para solicitud de rollback"""
    target_version: int = Field(..., ge=1)
    reason: str = Field(..., min_length=10, max_length=500)
    
    @validator('reason')
    def validate_reason(cls, v):
        # Sanitizar razón del rollback
        sanitized = re.sub(r'[<>"\'\{\}]', '', v.strip())
        return sanitized


class TenantPromptVersionsResponse(BaseModel):
    """Esquema para listar versiones de configuración"""
    versions: List[TenantPromptResponse]
    current_version: int
    total_versions: int


# Esquemas de error
class ValidationError(BaseModel):
    """Esquema para errores de validación"""
    field: str
    message: str
    code: str


class TenantPromptError(BaseModel):
    """Esquema para errores específicos de prompts"""
    error: str
    details: Optional[List[ValidationError]] = None
    tenant_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Constantes de seguridad
MAX_PROMPT_LENGTH = 4000
MAX_VERSIONS_PER_TENANT = 50
ALLOWED_MODELS = ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"]
PROHIBITED_PROMPT_PHRASES = [
    "ignore", "override", "jailbreak", "pretend", "act as",
    "olvidate", "ignora", "simula ser", "eres ahora"
]