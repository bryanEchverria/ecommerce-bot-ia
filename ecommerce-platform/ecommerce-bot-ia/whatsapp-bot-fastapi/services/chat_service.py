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
        # FIX: Updated to OpenAI v1.x API syntax
        client = openai.AsyncOpenAI()
        prompt = f"""
        Eres un asistente de ventas para {client_info['name']}, una tienda de {client_info['type']}.
        Cliente escribió: "{mensaje}"
        
        Responde de manera amigable y útil, sugiriendo productos relevantes.
        Máximo 200 caracteres.
        """
        
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"OpenAI error: {e}")
        return None

async def procesar_mensaje_con_contexto(telefono: str, mensaje: str, tenant_id: str = None, historial: list = None) -> str:
    """
    Message processing with conversation history support
    """
    print(f"🎯 CONTEXTO: Procesando mensaje '{mensaje}' con historial de {len(historial) if historial else 0} mensajes")
    try:
        # Import Flow service and AI improvements
        import sys
        import os
        from pathlib import Path
        
        current_dir = Path(__file__).parent
        app_dir = current_dir.parent
        sys.path.insert(0, str(current_dir))
        sys.path.insert(0, str(app_dir))
        
        print(f"🔧 About to import flow_chat_service...")
        from flow_chat_service import procesar_mensaje_flow_inteligente
        print(f"🔧 About to import database...")
        from database import SessionLocal
        print(f"🔧 About to import backoffice_integration...")  
        from backoffice_integration import get_real_products_from_backoffice, get_tenant_info
        print(f"🔧 All imports successful!")
        
        # Create database session
        db = SessionLocal()
        try:
            # Convert frontend history format to AI format
            ai_history = []
            if historial:
                for msg in historial[-5:]:  # Last 5 messages for context
                    ai_history.append({
                        "user" if msg.get("role") == "user" else "bot": msg.get("content", "")
                    })
            
            print(f"🔧 Calling procesar_mensaje_flow_inteligente with {len(ai_history)} history messages...")
            
            # Use Flow chat service with intelligence and context
            response = procesar_mensaje_flow_inteligente(db, telefono, mensaje, tenant_id, ai_history)
            
            print(f"🔧 Got response from flow service: {response[:50]}...")
            
            return response
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"🚨 ERROR in context processing: {e}")
        import traceback
        traceback.print_exc()
        # Fallback to regular processing
        return await procesar_mensaje(telefono, mensaje, tenant_id)

async def procesar_mensaje(telefono: str, mensaje: str, tenant_id: str = None) -> str:
    """
    Main message processing function
    Integrates with Flow payment system for multi-tenant e-commerce
    """
    try:
        # Import Flow service here to avoid circular imports
        import sys
        import os
        from pathlib import Path
        
        # Add current directory to Python path for imports
        current_dir = Path(__file__).parent
        app_dir = current_dir.parent
        sys.path.insert(0, str(current_dir))
        sys.path.insert(0, str(app_dir))
        
        from flow_chat_service import procesar_mensaje_flow_inteligente
        from database import SessionLocal
        
        # Create database session
        db = SessionLocal()
        try:
            # Use the integrated Flow chat service with intelligence (no context)
            response = procesar_mensaje_flow_inteligente(db, telefono, mensaje, tenant_id, [])
            return response
        finally:
            db.close()
            
    except Exception as e:
        print(f"Error in Flow processing: {e}")
        # Fallback to original logic if Flow service fails
        mensaje_lower = mensaje.lower().strip()
        client_info = await get_client_info(telefono)
        
        # Handle unknown clients
        if client_info["type"] == "unknown":
            return f"""🌿 ¡Hola! Bienvenido a Green House

Lo siento, estoy experimentando algunos problemas técnicos en este momento.

Nuestro equipo está trabajando para solucionarlo.

🕐 Intenta de nuevo en unos minutos, por favor.

¡Gracias por tu paciencia! 😊"""

        # Simple greeting response
        if any(word in mensaje_lower for word in ["hola", "hi", "hello", "buenas"]):
            return f"""{client_info['greeting']}

¿Cómo puedo ayudarte hoy? 😊

💡 Puedes preguntarme sobre:
• Productos disponibles
• Precios y ofertas  
• Información de la tienda"""

        # Fallback response with AI if available
        if OPENAI_AVAILABLE:
            ai_response = await process_with_openai(mensaje, client_info)
            if ai_response:
                return ai_response
        
        return f"""🤖 {client_info['name']} - Asistente Virtual

📱 Recibí: "{mensaje}"

¡Gracias por tu mensaje! En este momento nuestro sistema está procesando muchas consultas.

🔄 Estamos trabajando para darte una respuesta más completa.

¿Hay algo específico en lo que te pueda ayudar mientras tanto?"""
    
    except Exception as e:
        print(f"Error in Flow processing: {e}")
        return f"⚠️ Error interno. Intenta de nuevo en unos momentos."