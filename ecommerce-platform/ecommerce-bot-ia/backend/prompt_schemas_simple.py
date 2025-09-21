"""
Esquemas Pydantic simplificados para configuración de prompts por tenant
Compatible con versiones anteriores de Pydantic
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class StyleOverrides(BaseModel):
    tono: Optional[str] = "amigable"
    usar_emojis: Optional[bool] = True
    limite_respuesta_caracteres: Optional[int] = Field(default=300, ge=50, le=1000)
    incluir_contexto_empresa: Optional[bool] = True


class NLUParams(BaseModel):
    modelo: Optional[str] = "gpt-4o-mini"
    temperature_nlu: Optional[float] = Field(default=0.3, ge=0.0, le=1.0)
    max_tokens_nlu: Optional[int] = Field(default=150, ge=50, le=500)


class NLGParams(BaseModel):
    modelo: Optional[str] = "gpt-4o-mini"
    temperature_nlg: Optional[float] = Field(default=0.7, ge=0.0, le=1.0)
    max_tokens_nlg: Optional[int] = Field(default=300, ge=100, le=1000)


class TenantPromptBase(BaseModel):
    system_prompt: str = Field(..., min_length=50, max_length=4000)
    style_overrides: Optional[StyleOverrides] = None
    nlu_params: Optional[NLUParams] = None
    nlg_params: Optional[NLGParams] = None


class TenantPromptCreate(TenantPromptBase):
    pass


class TenantPromptUpdate(BaseModel):
    system_prompt: Optional[str] = Field(None, min_length=50, max_length=4000)
    style_overrides: Optional[StyleOverrides] = None
    nlu_params: Optional[NLUParams] = None
    nlg_params: Optional[NLGParams] = None


class TenantPromptResponse(TenantPromptBase):
    id: str
    tenant_id: str
    version: int
    is_active: bool
    updated_by: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class TenantPromptPreviewRequest(BaseModel):
    prompt_config: Dict[str, Any]
    test_message: str
    include_products: bool = True


class TenantPromptPreviewResponse(BaseModel):
    bot_response: str
    processing_time_ms: Optional[float]
    tokens_used: Optional[Dict[str, int]]
    detected_intent: Optional[str]
    confidence_score: Optional[float]


class TenantPromptRollbackRequest(BaseModel):
    target_version: int
    reason: Optional[str] = "Rollback solicitado por administrador"


class TenantPromptVersionsResponse(BaseModel):
    versions: List[TenantPromptResponse]
    current_version: int
    total_versions: int


class TenantPromptAuditLogResponse(BaseModel):
    id: str
    tenant_id: str
    action: str
    changes_diff: Dict[str, Any]
    previous_version: Optional[int]
    new_version: Optional[int]
    performed_by: Optional[str]
    performed_at: datetime
    ip_address: Optional[str]

    class Config:
        from_attributes = True


class TenantPromptError(BaseModel):
    error_code: str
    message: str
    details: Optional[Dict[str, Any]] = None