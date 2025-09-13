"""
Chat service integrado con Flow para pagos
Multi-tenant compatible
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

# OpenAI integration (if available)
try:
    import openai
    openai.api_key = os.getenv("OPENAI_API_KEY")
    OPENAI_AVAILABLE = bool(os.getenv("OPENAI_API_KEY"))
except ImportError:
    OPENAI_AVAILABLE = False

# Multi-tenant client mapping with Flow support
TENANT_CLIENTS = {
    "+3456789012": {
        "name": "Green House",
        "type": "cannabis",
        "client_id": "green_house",
        "greeting": "🌿 ¡Hola! Bienvenido a Green House\nEspecialistas en productos canábicos premium."
    },
    "+1234567890": {
        "name": "Demo Company", 
        "type": "electronics",
        "client_id": "demo_company",
        "greeting": "📱 ¡Hola! Demo Company - Electrónicos de calidad"
    },
    "+5678901234": {
        "name": "Mundo Canino",
        "type": "pets",
        "client_id": "mundo_canino", 
        "greeting": "🐕 ¡Hola! Mundo Canino - Todo para tu mascota"
    },
    "+9876543210": {
        "name": "Test Store",
        "type": "clothing",
        "client_id": "test_store",
        "greeting": "👕 ¡Hola! Test Store - Moda y estilo"
    },
    "+56950915617": {
        "name": "Green House",
        "type": "cannabis", 
        "client_id": "green_house",
        "greeting": "🌿 ¡Hola! Bienvenido a Green House\nEspecialistas en productos canábicos premium."
    }
}

def menu_principal():
    return """🤖 *Bienvenido al Bot Automatizado* 🤖
Elige una opción:
1️⃣ Ver catálogo
2️⃣ Hablar con un ejecutivo  
3️⃣ Reportar un problema
4️⃣ Consultar estado de mi pedido"""

def obtener_sesion(db: Session, telefono: str, client_id: str):
    """Obtiene o crea una sesión para el usuario"""
    sesion = db.query(FlowSesion).filter_by(telefono=telefono).first()
    if not sesion:
        sesion = FlowSesion(
            telefono=telefono,
            client_id="sintestesia",
            estado="INITIAL",
            datos="{}"
        )
        db.add(sesion)
        db.commit()
        db.refresh(sesion)
    return sesion

def guardar_sesion(db: Session, sesion, estado: str = None, datos: dict = None):
    """Guarda cambios en la sesión"""
    if estado:
        sesion.estado = estado
    if datos:
        sesion.datos = json.dumps(datos)
    sesion.updated_at = datetime.utcnow()
    db.commit()

def obtener_productos_cliente_real(db: Session, telefono: str):
    """
    Obtiene productos reales del backoffice en tiempo real
    Multi-tenant compatible basado en número de teléfono
    """
    tenant_id = get_tenant_from_phone(telefono)
    productos = get_real_products_from_backoffice(db, tenant_id)
    tenant_info = get_tenant_info(tenant_id)
    
    return productos, tenant_id, tenant_info

def procesar_mensaje_flow(db: Session, telefono: str, mensaje: str) -> str:
    """
    Procesa mensajes con lógica de Flow integrada
    Multi-tenant compatible - consulta productos reales del backoffice
    """
    # Obtener información del tenant basado en el teléfono
    tenant_id = get_tenant_from_phone(telefono)
    tenant_info = get_tenant_info(tenant_id)
    
    # Mantener compatibilidad con código existente
    client_info = {
        "name": tenant_info["name"],
        "type": tenant_info["type"],
        "greeting": tenant_info["greeting"]
    }
    
    if not client_info:
        return f"""❌ Cliente no configurado: {telefono}
        
✅ Clientes válidos:
• +3456789012 → Green House (canábicos)
• +1234567890 → Demo Company (electrónicos)  
• +5678901234 → Mundo Canino (mascotas)
• +9876543210 → Test Store (ropa)

🧪 PRUEBA: Usa uno de estos números"""

    sesion = obtener_sesion(db, telefono, "sintestesia")
    datos_sesion = json.loads(sesion.datos) if sesion.datos else {}
    
    mensaje_lower = mensaje.lower().strip()
    
    # Verificar pedido pendiente de pago
    pedido_pendiente = db.query(FlowPedido).filter_by(
        telefono=telefono,
        client_id="sintestesia",
        estado="pendiente_pago"
    ).first()
    
    # Si hay pedido pendiente y no está cancelando
    if pedido_pendiente and "cancelar" not in mensaje_lower:
        if mensaje_lower in ["pagado", "ya pagué", "pague", "pago"]:
            # Verificar estado en BD (actualizado por callback de Flow)
            pedido_actual = db.query(FlowPedido).filter_by(id=pedido_pendiente.id).first()
            if pedido_actual and pedido_actual.estado == "pagado":
                guardar_sesion(db, sesion, "INITIAL", {})
                return f"✅ ¡Pago confirmado! Tu pedido #{pedido_actual.id} ha sido procesado.\nGracias por tu compra. 🙌"
            else:
                return f"⚠️ Aún no hemos recibido la confirmación del pago para tu pedido #{pedido_pendiente.id}.\n\nSi ya pagaste, el proceso puede tomar unos minutos."
        
        return f"Tu pedido #{pedido_pendiente.id} está pendiente de pago. Si ya pagaste escribe *pagado*, o escribe *cancelar pedido* para anularlo."
    
    # Cancelar pedido
    if "cancelar pedido" in mensaje_lower or "cancelar" in mensaje_lower:
        if pedido_pendiente:
            pedido_pendiente.estado = "cancelado"
            db.commit()
            guardar_sesion(db, sesion, "INITIAL", {})
            return f"❌ Tu pedido #{pedido_pendiente.id} ha sido *cancelado*.\n" + menu_principal()
        else:
            return "No tienes pedidos pendientes para cancelar.\n" + menu_principal()
    
    # Saludos
    if any(word in mensaje_lower for word in ["hola", "hi", "hello", "buenas", "menu", "inicio"]):
        guardar_sesion(db, sesion, "INITIAL", {})
        return client_info["greeting"] + "\n\n" + menu_principal()
    
    # Ver catálogo
    if mensaje_lower in ["1", "ver catalogo", "ver catálogo", "productos", "catalog", "que productos tienes", "que tienes", "stock"]:
        productos, tenant_id, tenant_info = obtener_productos_cliente_real(db, telefono)
        catalogo = f"🌿 *{client_info['name']} - Catálogo disponible:*\n\n"
        for i, prod in enumerate(productos, 1):
            stock_status = "✅ Disponible" if prod['stock'] > 5 else f"⚠️ Quedan {prod['stock']}"
            precio_formateado = format_price(prod['price'], tenant_info['currency'])
            catalogo += f"{i}. **{prod['name']}** - {precio_formateado}\n"
            catalogo += f"   {prod['description']}\n"
            catalogo += f"   {stock_status}\n\n"
        catalogo += "💬 *Para comprar:* Escribe el nombre del producto que quieres\n"
        catalogo += "📝 *Ejemplo:* 'Quiero Blue Dream' o solo 'Blue Dream'"
        guardar_sesion(db, sesion, "BROWSING", {})
        return catalogo
    
    # Detectar intención de compra específica
    if sesion.estado in ["INITIAL", "BROWSING"] or any(word in mensaje_lower for word in ["quiero", "necesito", "comprar", "llevar", "recomien"]):
        productos, tenant_id, tenant_info = obtener_productos_cliente_real(db, telefono)
        productos_info = {prod['name'].lower(): {"id": prod['id'], "nombre": prod['name'], "precio": prod['price'], "stock": prod['stock']} 
                         for prod in productos}
        
        # Mejorar detección de productos (incluir palabras parciales)
        pedido_detectado = {}
        mensaje_words = mensaje_lower.split()
        
        for nombre_prod, info in productos_info.items():
            prod_words = nombre_prod.split()
            # Verificar coincidencia completa o parcial
            if nombre_prod in mensaje_lower or any(word in mensaje_words for word in prod_words):
                # Extraer cantidad del mensaje
                cantidad = 1
                for word in mensaje.split():
                    if word.isdigit():
                        cantidad = int(word)
                        break
                
                # Verificar stock disponible
                if cantidad > info["stock"]:
                    return f"❌ Lo siento, solo tenemos {info['stock']} unidades de {info['nombre']} disponibles.\n\n¿Quieres esa cantidad? Escribe 'sí' o elige otro producto."
                
                pedido_detectado[info["id"]] = {
                    "nombre": info["nombre"],
                    "precio": info["precio"],
                    "cantidad": cantidad
                }
        
        # Si se detectó un producto específico
        if pedido_detectado:
            total = sum(item["precio"] * item["cantidad"] for item in pedido_detectado.values())
            
            resumen = "🛒 **Resumen de tu pedido:**\n\n"
            for item in pedido_detectado.values():
                resumen += f"• {item['cantidad']} x {item['nombre']} = ${item['precio'] * item['cantidad']}\n"
            resumen += f"\n💰 **Total: ${total}**\n\n"
            resumen += "✅ ¿Confirmas este pedido?\n"
            resumen += "👉 Responde: **SÍ** para confirmar o **NO** para cancelar"
            
            guardar_sesion(db, sesion, "ORDER_CONFIRMATION", {"pedido": pedido_detectado, "total": total})
            return resumen
        
        # Si pregunta por recomendaciones
        elif any(word in mensaje_lower for word in ["recomien", "recomienda", "suger", "cual", "mejor"]):
            if client_info['type'] == 'cannabis':
                return f"🌿 **Para principiantes recomiendo:**\n\n• **Blue Dream** (${productos[0].precio}) - Híbrida equilibrada, ideal para comenzar\n• **Northern Lights** (${productos[3].precio}) - Indica suave y relajante\n\n💬 Escribe el nombre del que te interesa para comprarlo"
            else:
                return f"📱 **Productos más populares:**\n\n• **{productos[0].nombre}** (${productos[0].precio})\n• **{productos[1].nombre}** (${productos[1].precio})\n\n💬 Escribe el nombre del que te interesa"
        
        # Si no se detectó producto específico pero hay intención de compra
        elif any(word in mensaje_lower for word in ["quiero", "necesito", "comprar"]):
            return f"🔍 No encontré ese producto específico.\n\n💡 **Escribe '1' para ver todo el catálogo** o dime exactamente qué producto buscas.\n\nEjemplo: 'Blue Dream' o 'iPhone'"
    
    # Confirmación de pedido
    if sesion.estado == "ORDER_CONFIRMATION":
        if any(word in mensaje_lower for word in ["sí", "si", "yes", "confirmo", "ok", "acepto"]):
            datos = json.loads(sesion.datos)
            pedido_data = datos["pedido"]
            total = datos["total"]
            
            # Crear pedido en BD
            pedido = FlowPedido(
                telefono=telefono,
                client_id="sintestesia",
                total=total,
                estado="pendiente_pago"
            )
            db.add(pedido)
            db.commit()
            db.refresh(pedido)
            
            # Crear productos del pedido y actualizar stock en tiempo real
            for prod_id, item in pedido_data.items():
                # Actualizar stock en la tabla products del backoffice
                stock_actualizado = update_product_stock(db, prod_id, item["cantidad"], tenant_id)
                if not stock_actualizado:
                    return f"❌ Error: No hay suficiente stock de {item['nombre']}. Intenta con menos cantidad."
                
                producto_pedido = FlowProductoPedido(
                    pedido_id=pedido.id,
                    producto_id=prod_id,  # Usar string ID del backoffice
                    cantidad=item["cantidad"],
                    precio_unitario=item["precio"]
                )
                db.add(producto_pedido)
            
            db.commit()
            
            # Crear orden de pago en Flow
            descripcion = f"Pedido_{client_info['name']}_{pedido.id}"
            url_pago = crear_orden_flow(str(pedido.id), int(total), descripcion, tenant_id, db)
            
            # Preparar resumen del pedido con formato mejorado
            resumen_productos = ""
            for item in pedido_data.values():
                precio_formateado = format_price(item['precio'] * item['cantidad'], tenant_info['currency'])
                resumen_productos += f"• {item['cantidad']} x {item['nombre']} = {precio_formateado}\n"
            
            total_formateado = format_price(total, tenant_info['currency'])
            respuesta = f"""🎉 **¡Pedido confirmado!** #{pedido.id}

🛒 **Tu compra:**
{resumen_productos}
💰 **Total: {total_formateado}**

💳 **Para completar tu pedido:**
👉 Haz clic aquí para pagar: {url_pago}

⏰ **Después del pago:**
Escribe *"pagado"* y verificaremos tu pago automáticamente."""
            
            guardar_sesion(db, sesion, "ORDER_SCHEDULING", {"pedido_id": pedido.id})
            return respuesta
            
        elif any(word in mensaje_lower for word in ["no", "cancelar", "cancel"]):
            guardar_sesion(db, sesion, "INITIAL", {})
            return "❌ **Pedido cancelado**\n\n" + menu_principal()
        
        # Si escribe algo diferente durante la confirmación
        else:
            return f"❓ No entendí tu respuesta.\n\n⚡ **Responde claramente:**\n• **SÍ** - para confirmar el pedido\n• **NO** - para cancelar\n\n🔄 ¿Confirmas tu pedido?"
    
    # Otras opciones del menú
    if mensaje_lower == "2":
        return "📞 Para hablar con un ejecutivo, puedes llamarnos al +56 9 1234 5678\n\n" + menu_principal()
    
    if mensaje_lower == "3":
        return "🐛 Para reportar un problema, envía un email a soporte@empresa.com\n\n" + menu_principal()
    
    if mensaje_lower == "4":
        pedidos = db.query(FlowPedido).filter_by(telefono=telefono).all()
        if pedidos:
            respuesta = f"📋 Tus pedidos en {client_info['name']}:\n\n"
            for pedido in pedidos[-3:]:  # Últimos 3 pedidos
                estado_emoji = {"pendiente_pago": "⏳", "pagado": "✅", "cancelado": "❌"}
                respuesta += f"{estado_emoji.get(pedido.estado, '❓')} Pedido #{pedido.id}\n"
                respuesta += f"   Total: ${pedido.total:.0f} - {pedido.estado.title()}\n"
                respuesta += f"   Fecha: {pedido.created_at.strftime('%d/%m/%Y')}\n\n"
            return respuesta + menu_principal()
        else:
            return f"No tienes pedidos registrados en {client_info['name']}.\n\n" + menu_principal()
    
    # Respuesta por defecto con OpenAI
    if OPENAI_AVAILABLE:
        try:
            client = openai.OpenAI()
            productos, tenant_id, tenant_info = obtener_productos_cliente_real(db, telefono)
            productos_info = [f"{prod['name']} (${prod['price']})" for prod in productos]
            
            # Contexto más específico para cada tipo de cliente
            if client_info['type'] == 'cannabis':
                contexto = "Especialista en productos canábicos premium. Enfócate en semillas de calidad."
            else:
                contexto = f"Especialista en {client_info['type']}."
            
            prompt = f"""
            Eres un {contexto} para {client_info['name']}.
            
            PRODUCTOS DISPONIBLES: {', '.join(productos_info)}
            
            CLIENTE ESCRIBIÓ: "{mensaje}"
            
            INSTRUCCIONES:
            - Si pregunta por productos específicos, muestra SOLO el que pregunta con precio y descripción
            - Si ya eligió un producto, NO sugieras otros, pregunta por la cantidad o confirma la compra
            - Si dice "solo quiero X", respeta su decisión y procede con ESE producto únicamente
            - Sé directo y conciso, máximo 150 caracteres
            - NUNCA ignores lo que el cliente dice claramente
            """
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100
            )
            ai_response = response.choices[0].message.content.strip()
            return ai_response + "\n\n" + menu_principal()
            
        except Exception as e:
            print(f"OpenAI error: {e}")
    
    # Fallback si OpenAI falla
    return f"🤖 {client_info['name']} - Asistente Virtual\n\n📱 Recibí: \"{mensaje}\"\n\n💡 Puedo ayudarte con:\n• Ver catálogo de productos\n• Procesar pedidos\n• Consultar estado de compras\n• Información general\n\n" + menu_principal()