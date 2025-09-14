"""
VERSIÓN COMPLETA: Sistema de Flujos Inteligentes para Bot WhatsApp
GPT detecta intención → Query específica → Respuesta con datos reales
"""
from services.smart_flows import detectar_intencion_con_gpt, ejecutar_flujo_inteligente
import json
import os
from sqlalchemy.orm import Session
from models import FlowProduct, FlowPedido, FlowProductoPedido, FlowSesion
from services.flow_service import crear_orden_flow, get_client_id_for_phone
from services.backoffice_integration import (
    get_real_products_from_backoffice, 
    update_product_stock,
    get_product_by_name_fuzzy,
    get_tenant_from_phone,
    get_tenant_info,
    format_price
)
from datetime import datetime

# OpenAI integration
try:
    import openai
    openai.api_key = os.getenv("OPENAI_API_KEY")
    OPENAI_AVAILABLE = bool(os.getenv("OPENAI_API_KEY"))
except ImportError:
    OPENAI_AVAILABLE = False

# Client mapping
TENANT_CLIENTS = {
    "+3456789012": {
        "name": "Green House",
        "type": "cannabis",
        "client_id": "green_house",
        "greeting": "🌿 ¡Hola! Bienvenido a Green House\\nEspecialistas en productos canábicos premium."
    },
    "+56950915617": {
        "name": "Green House",
        "type": "cannabis", 
        "client_id": "green_house",
        "greeting": "🌿 ¡Hola! Bienvenido a Green House\\nEspecialistas en productos canábicos premium."
    }
}

def get_client_info(telefono: str):
    """Get client information for the phone number"""
    if telefono in TENANT_CLIENTS:
        return TENANT_CLIENTS[telefono]
    return {
        "name": "Green House",
        "type": "cannabis",
        "client_id": "green_house", 
        "greeting": "🌿 ¡Hola! Bienvenido a Green House\\nEspecialistas en productos canábicos premium."
    }

def obtener_productos_cliente_real(db: Session, telefono: str):
    """Obtiene productos reales del backoffice para el cliente"""
    try:
        tenant_id = get_tenant_from_phone(telefono)
        if not tenant_id:
            tenant_id = "acme-cannabis-2024"
        
        tenant_info = get_tenant_info(tenant_id)
        productos = get_real_products_from_backoffice(tenant_id)
        
        return productos, tenant_id, tenant_info
    except Exception as e:
        print(f"Error obteniendo productos: {e}")
        return [], "acme-cannabis-2024", {"name": "Green House", "type": "cannabis", "currency": "CLP"}

def guardar_sesion(db: Session, sesion, estado: str = None, datos: dict = None):
    """Guarda cambios en la sesión"""
    if estado:
        sesion.estado = estado
    if datos:
        sesion.datos = json.dumps(datos)
    sesion.updated_at = datetime.utcnow()
    db.commit()

def obtener_sesion(db: Session, telefono: str):
    """Obtiene o crea una sesión para el usuario"""
    sesion = db.query(FlowSesion).filter_by(telefono=telefono).first()
    if not sesion:
        sesion = FlowSesion(
            telefono=telefono,
            estado="INITIAL",
            datos="{}"
        )
        db.add(sesion)
        db.commit()
        db.refresh(sesion)
    return sesion

def procesar_mensaje_flow_completo(db: Session, telefono: str, mensaje: str, client_info: dict) -> str:
    """
    FUNCIÓN PRINCIPAL - Sistema de Flujos Inteligentes Completo
    1. GPT detecta intención del usuario
    2. Ejecuta query específica con datos reales  
    3. Responde con información precisa del backoffice
    """
    print(f"🔄 Procesando mensaje: '{mensaje}' para {telefono}")
    
    # 1. OBTENER DATOS REALES DEL BACKOFFICE
    productos, tenant_id, tenant_info = obtener_productos_cliente_real(db, telefono)
    sesion = obtener_sesion(db, telefono)
    print(f"📊 Productos disponibles: {len(productos)}")
    
    # 2. SISTEMA DE FLUJOS INTELIGENTES - MÁXIMA PRIORIDAD
    if OPENAI_AVAILABLE and productos:
        try:
            print("🧠 Iniciando detección con GPT...")
            
            # GPT detecta la intención específica
            deteccion = detectar_intencion_con_gpt(mensaje, productos)
            print(f"🎯 GPT detectó: {deteccion}")
            
            # Ejecutar flujo específico según detección
            if deteccion["intencion"] in ["consulta_producto", "consulta_categoria", "consulta_catalogo", "intencion_compra"]:
                print(f"✅ Ejecutando flujo específico para: {deteccion['intencion']}")
                
                respuesta_inteligente = ejecutar_flujo_inteligente(deteccion, productos, tenant_info)
                print(f"📝 Respuesta generada: {len(respuesta_inteligente)} caracteres")
                
                # Actualizar sesión según el tipo de consulta
                if deteccion["intencion"] in ["consulta_categoria", "consulta_catalogo"]:
                    guardar_sesion(db, sesion, "BROWSING", {})
                elif deteccion["intencion"] == "intencion_compra":
                    datos_compra = {"deteccion": deteccion, "productos": productos}
                    guardar_sesion(db, sesion, "ASKING_QUANTITY", datos_compra)
                
                print("🎉 Flujo inteligente completado exitosamente")
                return respuesta_inteligente
            
            elif deteccion["intencion"] == "saludo":
                print("👋 Procesando saludo")
                nombre_tienda = tenant_info.get('name', client_info.get('name', 'nuestra tienda'))
                return f"¡Hola! Soy tu asistente de ventas de {nombre_tienda}. ¿En qué puedo ayudarte hoy?"
                
        except Exception as e:
            print(f"❌ Error en flujos inteligentes: {e}")
            import traceback
            traceback.print_exc()
    
    # 3. MANEJO DE ESTADOS DE SESIÓN
    mensaje_lower = mensaje.lower().strip()
    
    # Confirmaciones de pedidos
    if sesion.estado == "ORDER_CONFIRMATION":
        if any(word in mensaje_lower for word in ["sí", "si", "yes", "confirmo", "ok"]):
            return "✅ ¡Pedido confirmado! Te enviaré el link de pago en un momento."
        else:
            guardar_sesion(db, sesion, "INITIAL", {})
            return f"Pedido cancelado. ¿Hay algo más en lo que pueda ayudarte?"
    
    # Pidiendo cantidad
    if sesion.estado == "ASKING_QUANTITY":
        try:
            cantidad = int(''.join(filter(str.isdigit, mensaje)))
            if cantidad > 0:
                return f"Perfecto, {cantidad} unidades. ¿Confirmas tu pedido? (SÍ o NO)"
        except:
            pass
        return "Por favor indica cuántas unidades quieres (ejemplo: '2' o 'dos')"
    
    # 4. RESPUESTA POR DEFECTO INTELIGENTE
    if not productos:
        return "Lo siento, no hay productos disponibles en este momento."
    
    # Usar IA para respuesta conversacional si no se detectó intención específica
    if OPENAI_AVAILABLE:
        try:
            client = openai.OpenAI()
            productos_muestra = [f"{p['name']} (${p['price']:.0f})" for p in productos[:3]]
            
            prompt = f"""
            Eres un asistente de ventas de {tenant_info.get('name', 'Green House')}.
            
            Cliente escribió: "{mensaje}"
            Productos disponibles: {', '.join(productos_muestra)}
            
            Responde de manera útil y natural:
            - Si no entiendes qué busca, pregunta específicamente
            - Si busca algo que no tenemos, sugiérelo ver el catálogo
            - Mantén 2-3 frases máximo
            - Tono amigable y profesional
            """
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4,
                max_tokens=100
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error en respuesta IA: {e}")
    
    # Fallback final
    nombre_tienda = tenant_info.get('name', 'nuestra tienda')
    return f"¿En qué puedo ayudarte en {nombre_tienda}? Puedes preguntarme por productos específicos o escribir 'ver catálogo'."