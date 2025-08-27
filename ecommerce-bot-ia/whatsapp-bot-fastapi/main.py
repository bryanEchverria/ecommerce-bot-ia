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

app = FastAPI(
    title="WhatsApp E-commerce Bot",
    description="Intelligent WhatsApp bot for multi-tenant e-commerce with dual WhatsApp providers (Twilio + Meta)",
    version="2.0.0"
)

# Include Meta WhatsApp webhook router
app.include_router(meta_webhook_router, tags=["meta-webhook"])

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
    Main webhook endpoint for WhatsApp messages
    Processes messages using AI and returns intelligent responses
    """
    try:
        # Process message using AI service
        response = await procesar_mensaje(data.telefono, data.mensaje)
        
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

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "9001"))
    uvicorn.run(app, host="0.0.0.0", port=port)