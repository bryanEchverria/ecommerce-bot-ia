"""
WhatsApp Bot with FastAPI - Multi-tenant E-commerce Bot
Integrates with OpenAI and backend API for intelligent responses
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import sys
from pathlib import Path

# Add the services directory to the path
current_dir = Path(__file__).parent
services_dir = current_dir / "services"
sys.path.append(str(services_dir))

from services.chat_service import procesar_mensaje
from services.health_service import health_check
from api.webhook_meta import router as meta_webhook_router
from api.webhook_twilio import router as twilio_webhook_router
from database import Base, engine, SessionLocal # Importar Base, engine y SessionLocal

app = FastAPI(
    title="WhatsApp E-commerce Bot",
    description="Intelligent WhatsApp bot for multi-tenant e-commerce with dual WhatsApp providers (Twilio + Meta)",
    version="2.0.0"
)

# Crear tablas en la base de datos al iniciar la aplicación
@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)

# Include Meta WhatsApp webhook router
app.include_router(meta_webhook_router, tags=["meta-webhook"])

# Include Twilio WhatsApp webhook router
app.include_router(twilio_webhook_router, tags=["twilio-webhook"])

class WebhookMessage(BaseModel):
    telefono: str
    mensaje: str

@app.get("/")
def home():
    return {
        "status": "WhatsApp Bot Online",
        "version": "1.0.0",
        "services": ["OpenAI", "Multi-tenant", "E-commerce"]
    }

@app.get("/health")
def health():
    """Health check endpoint for Docker"""
    return health_check()

@app.get("/status")
async def status():
    """Status endpoint showing WhatsApp provider configuration"""
    try:
        from settings import get_available_providers
        providers_info = get_available_providers()
        
        return {
            "status": "WhatsApp Bot Online",
            "version": "2.0.0",
            "providers": providers_info,
            "endpoints": {
                "webhook_legacy": "/webhook (JSON format)",
                "webhook_meta": "/webhook/meta (Meta WhatsApp Cloud API)",
                "webhook_meta_verify": "/webhook/meta (GET with hub.* params)"
            }
        }
    except Exception as e:
        return {
            "status": "Error retrieving provider status",
            "error": str(e)
        }

@app.post("/webhook")
async def webhook(data: WebhookMessage):
    """
    Legacy webhook endpoint for WhatsApp messages
    For backwards compatibility only - use tenant-specific endpoints instead
    """
    try:
        # Process message using AI service with default tenant
        # For backoffice testing, use default tenant (acme-cannabis-2024)
        default_tenant_id = "acme-cannabis-2024"
        response = await procesar_mensaje(data.telefono, data.mensaje, default_tenant_id)
        
        return {
            "telefono": data.telefono,
            "mensaje_usuario": data.mensaje,
            "respuesta": response,
            "status": "success"
        }
    except Exception as e:
        return {
            "telefono": data.telefono,
            "mensaje_usuario": data.mensaje,
            "error": str(e),
            "status": "error"
        }

# ================================
# DYNAMIC MULTI-TENANT WEBHOOK SYSTEM
# ================================

@app.post("/webhook/{tenant_slug}")
async def webhook_tenant_dynamic(tenant_slug: str, data: WebhookMessage):
    """
    Dynamic webhook endpoint for any tenant
    URL format: /webhook/{tenant_slug}
    Examples:
    - /webhook/acme → processes for acme-cannabis-2024
    - /webhook/bravo → processes for bravo-gaming-2024  
    - /webhook/mundo-canino → processes for mundo-canino-2024
    - /webhook/nueva-tienda → processes for nueva-tienda-2024
    """
    try:
        # Get tenant info from database using slug
        from services.backoffice_integration import get_tenant_from_slug
        from services.flow_chat_service import procesar_mensaje_flow
        from database import SessionLocal
        
        db = SessionLocal()
        try:
            # Get full tenant_id from slug
            tenant_info = get_tenant_from_slug(db, tenant_slug)
            
            if not tenant_info:
                return {
                    "telefono": data.telefono,
                    "mensaje_usuario": data.mensaje,
                    "error": f"Tenant '{tenant_slug}' not found",
                    "available_tenants": "Check /tenants endpoint for valid slugs",
                    "status": "error"
                }
            
            tenant_id = tenant_info.get('id') or tenant_info.get('slug')
            
            # Process message with specific tenant context
            response = procesar_mensaje_flow(db, data.telefono, data.mensaje, tenant_id)
            
            return {
                "telefono": data.telefono,
                "mensaje_usuario": data.mensaje,
                "respuesta": response,
                "tenant_slug": tenant_slug,
                "tenant_id": tenant_id,
                "tenant_name": tenant_info.get('name'),
                "status": "success"
            }
            
        finally:
            db.close()
        
    except Exception as e:
        return {
            "telefono": data.telefono,
            "mensaje_usuario": data.mensaje,
            "error": str(e),
            "tenant_slug": tenant_slug,
            "status": "error"
        }

@app.get("/tenants")
async def list_available_tenants():
    """
    Lists all available tenants and their webhook URLs
    Useful for configuration and debugging
    """
    try:
        from database import SessionLocal
        from auth_models import TenantClient
        
        db = SessionLocal()
        try:
            tenants = db.query(TenantClient).all()
            
            tenant_list = []
            for tenant in tenants:
                # Extract slug from full ID (e.g., "acme-cannabis-2024" → "acme")
                slug = tenant.slug if tenant.slug else tenant.id.split('-')[0]
                
                tenant_list.append({
                    "id": tenant.id,
                    "name": tenant.name, 
                    "slug": slug,
                    "webhook_url": f"/webhook/{slug}",
                    "full_webhook_url": f"http://localhost:9001/webhook/{slug}",
                    "status": "active"
                })
            
            return {
                "status": "success",
                "total_tenants": len(tenant_list),
                "tenants": tenant_list,
                "usage": "POST to /webhook/{slug} with {telefono, mensaje}"
            }
            
        finally:
            db.close()
            
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "Could not retrieve tenant list"
        }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "9001"))
    uvicorn.run(app, host="0.0.0.0", port=port)