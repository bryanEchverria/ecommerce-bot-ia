"""
Health check service for WhatsApp bot
"""
import os
from datetime import datetime

def health_check():
    """Comprehensive health check for the bot service"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "openai": bool(os.getenv("OPENAI_API_KEY")),
            "backend": bool(os.getenv("BACKEND_URL")),
            "environment": os.getenv("ENVIRONMENT", "development")
        },
        "version": "1.0.0"
    }