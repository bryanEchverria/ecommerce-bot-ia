"""
Chat service con IA mejorada - Usa GPT para respuestas más naturales
"""
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

def obtener_productos_cliente_real(db: Session, telefono: str):
    """Obtiene productos reales del backoffice para el cliente"""
    try:
        tenant_id = get_tenant_from_phone(telefono)
        if not tenant_id:
            tenant_id = "acme-cannabis-2024"  # Default
        
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

def usar_ia_para_responder(mensaje: str, productos: list, tenant_info: dict, contexto_sesion: dict) -> dict:
    """Usa GPT para interpretar el mensaje y generar respuesta inteligente"""
    if not OPENAI_AVAILABLE:
        return {"tipo": "error", "respuesta": "IA no disponible"}
    
    try:
        client = openai.OpenAI()
        productos_lista = "\n".join([f"- {prod['name']} (${prod['price']}): {prod['description']}" for prod in productos])
        
        prompt = f"""
        Eres un asistente de ventas multitienda especializado. Atiendes en nombre de {tenant_info['name']}, una tienda especializada en {tenant_info.get('type', 'productos')}.

        PRODUCTOS DISPONIBLES:
        {productos_lista}

        MENSAJE DEL CLIENTE: "{mensaje}"
        
        CONTEXTO DE LA SESIÓN: {json.dumps(contexto_sesion)}

        INSTRUCCIONES:
        1. Si es un saludo (hola, buenas, etc.), responde cordialmente con el nombre de la tienda y pregunta en qué puedes ayudar.
        2. Si pide "ver catálogo" o pregunta por productos en general, NO muestres todo. Mejor pregunta qué tipo específico busca.
        3. Si menciona un producto específico, verifica si existe en la lista y responde con detalles (nombre, precio, disponibilidad).
        4. Si confirma compra, pregunta cantidad específica.
        5. Para confirmaciones (sí/no), procesa según el contexto.
        6. Mantén respuestas concisas (máximo 3 frases).

        RESPONDE EN FORMATO JSON:
        {{
            "tipo": "saludo|consulta_catalogo|producto_especifico|confirmacion|otro",
            "respuesta": "tu respuesta natural y conversacional",
            "accion": "ninguna|mostrar_producto|procesar_pedido|pedir_cantidad",
            "producto_mencionado": "nombre del producto si aplica",
            "cantidad": numero si se menciona cantidad
        }}
        """
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=300
        )
        
        respuesta_json = response.choices[0].message.content.strip()
        
        # Limpiar si viene con markdown
        if respuesta_json.startswith("```json"):
            respuesta_json = respuesta_json.replace("```json", "").replace("```", "").strip()
        
        return json.loads(respuesta_json)
        
    except Exception as e:
        print(f"Error con IA: {e}")
        return {
            "tipo": "error",
            "respuesta": f"No entendí tu mensaje. ¿Puedes ser más específico sobre qué necesitas en {tenant_info['name']}?",
            "accion": "ninguna"
        }

def procesar_mensaje_con_ia(db: Session, telefono: str, mensaje: str, client_info: dict) -> str:
    """Función principal que usa IA para procesar mensajes de manera más natural"""
    
    # Obtener datos necesarios
    productos, tenant_id, tenant_info = obtener_productos_cliente_real(db, telefono)
    sesion = obtener_sesion(db, telefono)
    contexto_sesion = json.loads(sesion.datos) if sesion.datos else {}
    
    # Usar IA para interpretar el mensaje
    respuesta_ia = usar_ia_para_responder(mensaje, productos, tenant_info, contexto_sesion)
    
    # Procesar según el tipo de respuesta
    if respuesta_ia["tipo"] == "saludo":
        guardar_sesion(db, sesion, "INITIAL", {})
        return respuesta_ia["respuesta"]
    
    elif respuesta_ia["tipo"] == "consulta_catalogo":
        # Mostrar categorías en lugar de productos completos
        categorias = set()
        for prod in productos:
            if 'aceite' in prod['name'].lower() or 'cbd' in prod['name'].lower():
                categorias.add('Aceites y CBD')
            elif 'semilla' in prod['name'].lower():
                categorias.add('Semillas')
            elif any(word in prod['name'].lower() for word in ['flores', 'northern', 'kush']):
                categorias.add('Flores')
            elif 'brownie' in prod['name'].lower() or 'comestible' in prod['name'].lower():
                categorias.add('Comestibles')
            else:
                categorias.add('Accesorios')
        
        catalogo = f"Estas son nuestras categorías en {tenant_info['name']}:\n\n"
        for i, cat in enumerate(sorted(categorias), 1):
            catalogo += f"{i}. {cat}\n"
        catalogo += "\n¿Qué tipo de producto te interesa?"
        
        guardar_sesion(db, sesion, "BROWSING", {})
        return catalogo
    
    elif respuesta_ia["tipo"] == "producto_especifico" and respuesta_ia.get("producto_mencionado"):
        # Buscar producto específico
        producto_encontrado = None
        for prod in productos:
            if respuesta_ia["producto_mencionado"].lower() in prod['name'].lower():
                producto_encontrado = prod
                break
        
        if producto_encontrado:
            if respuesta_ia.get("cantidad"):
                # Ya tiene cantidad, proceder a confirmar
                total = float(producto_encontrado['price']) * int(respuesta_ia["cantidad"])
                contexto_pedido = {
                    "producto": producto_encontrado,
                    "cantidad": int(respuesta_ia["cantidad"]),
                    "total": total
                }
                guardar_sesion(db, sesion, "CONFIRMACION", contexto_pedido)
                
                return f"🛒 **Resumen:**\n• {respuesta_ia['cantidad']} x {producto_encontrado['name']} = ${total:.0f}\n\n¿Confirmas este pedido? Responde **SÍ** para confirmar o **NO** para cancelar"
            else:
                # Preguntar cantidad
                contexto_pedido = {"producto": producto_encontrado}
                guardar_sesion(db, sesion, "PIDIENDO_CANTIDAD", contexto_pedido)
                
                return f"Perfecto! Tenemos {producto_encontrado['name']} por ${producto_encontrado['price']:.0f}.\n\n¿Cuántas unidades deseas?"
        else:
            return f"No encontré ese producto en {tenant_info['name']}. ¿Podrías ser más específico o escribir 'ver catálogo'?"
    
    elif respuesta_ia["tipo"] == "confirmacion" and sesion.estado == "CONFIRMACION":
        if any(word in mensaje.lower() for word in ["sí", "si", "yes", "confirmo", "ok"]):
            # Procesar pedido
            datos_pedido = json.loads(sesion.datos)
            # Aquí iría la lógica de crear el pedido real
            guardar_sesion(db, sesion, "INITIAL", {})
            return "✅ ¡Pedido confirmado! Te enviaré el link de pago en un momento."
        else:
            guardar_sesion(db, sesion, "INITIAL", {})
            return f"Pedido cancelado. ¿Hay algo más en lo que pueda ayudarte en {tenant_info['name']}?"
    
    elif sesion.estado == "PIDIENDO_CANTIDAD":
        # Verificar si menciona una cantidad
        try:
            cantidad = int(''.join(filter(str.isdigit, mensaje)))
            if cantidad > 0:
                datos_pedido = json.loads(sesion.datos)
                producto = datos_pedido["producto"]
                total = float(producto['price']) * cantidad
                
                contexto_pedido = {
                    "producto": producto,
                    "cantidad": cantidad,
                    "total": total
                }
                guardar_sesion(db, sesion, "CONFIRMACION", contexto_pedido)
                
                return f"🛒 **Resumen:**\n• {cantidad} x {producto['name']} = ${total:.0f}\n\n¿Confirmas este pedido? Responde **SÍ** para confirmar o **NO** para cancelar"
        except:
            pass
        
        return "Por favor, indica cuántas unidades deseas (ejemplo: '2' o 'dos unidades')"
    
    # Respuesta por defecto usando IA
    return respuesta_ia["respuesta"]