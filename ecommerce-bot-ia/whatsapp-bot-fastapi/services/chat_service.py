"""
Chat service with OpenAI integration for intelligent responses
Multi-tenant aware with backend API integration
"""
import os
import asyncio
import httpx
from typing import Dict, Any

# OpenAI integration (if available)
try:
    import openai
    openai.api_key = os.getenv("OPENAI_API_KEY")
    OPENAI_AVAILABLE = bool(os.getenv("OPENAI_API_KEY"))
except ImportError:
    OPENAI_AVAILABLE = False

BACKEND_URL = os.getenv("BACKEND_URL", "https://api.sintestesia.cl" if os.getenv("ENVIRONMENT") == "production" else "http://localhost:8002")

# Multi-tenant client mapping
TENANT_CLIENTS = {
    "+3456789012": {
        "name": "Green House",
        "type": "cannabis",
        "greeting": "¡Hola! Bienvenido a Green House 🌿\nEspecialistas en productos canábicos."
    },
    "+1234567890": {
        "name": "Demo Company", 
        "type": "electronics",
        "greeting": "¡Hola! Demo Company - Electrónicos 📱💻"
    },
    "+5678901234": {
        "name": "Mundo Canino",
        "type": "pets",
        "greeting": "¡Hola! Mundo Canino - Productos para mascotas 🐕"
    },
    "+9876543210": {
        "name": "Test Store",
        "type": "clothing", 
        "greeting": "¡Hola! Test Store - Ropa y accesorios 👕"
    },
    "+56950915617": {
        "name": "Green House",
        "type": "cannabis",
        "greeting": "¡Hola! Bienvenido a Green House 🌿\nEspecialistas en productos canábicos premium."
    }
}

async def get_client_info(telefono: str) -> Dict[str, Any]:
    """Get client information for the phone number"""
    return TENANT_CLIENTS.get(telefono, {
        "name": "Cliente no configurado",
        "type": "unknown",
        "greeting": "Cliente no configurado en el sistema"
    })

async def search_products_backend(query: str, client_phone: str) -> list:
    """Search products using backend API"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BACKEND_URL}/api/bot/products/search",
                params={"query": query, "limit": 3},
                headers={"Authorization": f"Bearer {client_phone}"}  # Simple auth for demo
            )
            if response.status_code == 200:
                return response.json()
            return []
    except Exception as e:
        print(f"Error searching products: {e}")
        return []

async def process_with_openai(mensaje: str, client_info: Dict) -> str:
    """Process message using OpenAI (if available)"""
    if not OPENAI_AVAILABLE:
        return None
    
    try:
        prompt = f"""
        Eres un asistente de ventas para {client_info['name']}, una tienda de {client_info['type']}.
        Cliente escribió: "{mensaje}"
        
        Responde de manera amigable y útil, sugiriendo productos relevantes.
        Máximo 200 caracteres.
        """
        
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"OpenAI error: {e}")
        return None

async def procesar_mensaje(telefono: str, mensaje: str) -> str:
    """
    Main message processing function
    Integrates with Flow payment system for multi-tenant e-commerce
    """
    # Import Flow service here to avoid circular imports
    import sys
    import os
    from pathlib import Path
    
    # Add current directory to Python path for imports
    current_dir = Path(__file__).parent
    app_dir = current_dir.parent
    sys.path.insert(0, str(current_dir))
    sys.path.insert(0, str(app_dir))
    
    try:
        from flow_chat_service import procesar_mensaje_flow
        from database import SessionLocal
        
        # Create database session
        db = SessionLocal()
        try:
            # Use the integrated Flow chat service
            response = procesar_mensaje_flow(db, telefono, mensaje)
            return response
        finally:
            db.close()
            
    except ImportError as e:
        print(f"Error importing Flow service: {e}")
        # Fallback to original logic if Flow service fails
        mensaje_lower = mensaje.lower().strip()
        client_info = await get_client_info(telefono)
        
        # Handle unknown clients
        if client_info["type"] == "unknown":
            return f"""❌ Cliente no configurado: {telefono}

✅ Clientes válidos:
• +3456789012 → Green House (canábicos)
• +1234567890 → Demo Company (electrónicos)  
• +5678901234 → Mundo Canino (mascotas)
• +9876543210 → Test Store (ropa)

🧪 PRUEBA: Usa uno de estos números"""

        # Simple greeting response
        if any(word in mensaje_lower for word in ["hola", "hi", "hello", "buenas"]):
            return f"""{client_info['greeting']}

🔧 Sistema Flow en mantenimiento - usando modo básico
💡 Escribe "productos" para ver el catálogo"""

        # Fallback response
        return f"""🤖 {client_info['name']} - Asistente Virtual

📱 Recibí: "{mensaje}"

⚠️ Sistema de pagos Flow en configuración
💡 Funcionalidad completa estará disponible pronto

¿En qué más te puedo ayudar?"""
    
    except Exception as e:
        print(f"Error in Flow processing: {e}")
        return f"⚠️ Error interno. Intenta de nuevo en unos momentos."