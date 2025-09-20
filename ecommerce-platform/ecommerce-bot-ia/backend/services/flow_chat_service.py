"""
Chat service integrado con Flow para pagos
Multi-tenant compatible
"""
import json
import os
from sqlalchemy.orm import Session
from models import FlowProduct, FlowPedido, FlowProductoPedido, FlowSesion, Product
from services.flow_service import crear_orden_flow
from datetime import datetime, timedelta

# OpenAI integration (if available)
try:
    import openai
    openai.api_key = os.getenv("OPENAI_API_KEY")
    OPENAI_AVAILABLE = bool(os.getenv("OPENAI_API_KEY"))
except ImportError:
    OPENAI_AVAILABLE = False

# Función para obtener configuración por tenant
def get_store_config(db: Session, tenant_id: str):
    """Obtiene configuración de tienda basada en tenant_id"""
    from auth_models import TenantClient
    
    tenant = db.query(TenantClient).filter_by(id=tenant_id).first()
    if not tenant:
        # Configuración por defecto
        return {
            "name": "Tienda Online",
            "type": "productos",
            "greeting": "¡Hola! Bienvenido a nuestra tienda online."
        }
    
    # Configuración dinámica basada en el tenant
    return {
        "name": tenant.name,
        "type": "productos", 
        "greeting": f"¡Hola! Bienvenido a {tenant.name}."
    }

def menu_principal(store_name: str):
    return f"""¡Hola! Soy tu asistente de ventas de {store_name}. 

¿En qué puedo ayudarte hoy?

Puedes escribir:
• "ver catálogo" para conocer nuestros productos
• El nombre de algún producto específico
• "mi pedido" para consultar tu estado"""

def obtener_sesion(db: Session, telefono: str, tenant_id: str = None):
    """Obtiene o crea una sesión para el usuario - multi-tenant aware"""
    # Import here to avoid circular dependencies
    from tenant_middleware import get_tenant_id
    
    # Get tenant_id from middleware context if not provided
    if not tenant_id:
        try:
            tenant_id = get_tenant_id()
        except Exception:
            # Fallback to default tenant if middleware context not available
            tenant_id = "default-tenant-000"
    
    sesion = db.query(FlowSesion).filter_by(telefono=telefono, tenant_id=tenant_id).first()
    if not sesion:
        sesion = FlowSesion(
            telefono=telefono,
            tenant_id=tenant_id,
            estado="INITIAL",
            datos="{}"
        )
        db.add(sesion)
        db.commit()
        db.refresh(sesion)
    return sesion

def guardar_sesion(db: Session, sesion, estado: str = None, datos: dict = None, update_last_message: bool = True):
    """Guarda cambios en la sesión"""
    if estado:
        sesion.estado = estado
    if datos:
        sesion.datos = json.dumps(datos)
    if update_last_message:
        sesion.last_message_at = datetime.utcnow()
        sesion.timeout_warning_sent = False  # Reset warning cuando hay nuevo mensaje
    sesion.updated_at = datetime.utcnow()
    db.commit()

def check_conversation_timeout(db: Session, sesion) -> str:
    """
    Verifica si la conversación ha expirado y maneja timeouts
    Returns: mensaje de timeout si aplica, None si no hay timeout
    """
    if not sesion.conversation_active:
        return None
        
    now = datetime.utcnow()
    time_since_last = now - sesion.last_message_at
    
    # 30 segundos sin respuesta - primera advertencia (PRUEBA)
    if time_since_last >= timedelta(seconds=30) and not sesion.timeout_warning_sent:
        sesion.timeout_warning_sent = True
        db.commit()
        return """⏰ *Seguimiento de Conversación*
        
¡Hola! Veo que ha pasado un tiempo desde tu último mensaje.

¿Sigues interesado en completar tu compra o necesitas más información?

👉 Escribe *continuar* para seguir, o *finalizar* para terminar la conversación.

⏳ Si no respondes en 30 minutos más, finalizaré automáticamente la sesión."""

    # 60 segundos sin respuesta - finalizar conversación (PRUEBA)
    elif time_since_last >= timedelta(seconds=60):
        sesion.conversation_active = False
        sesion.estado = "FINALIZADA"
        db.commit()
        return """🔚 *Conversación Finalizada*

Por tu seguridad y para optimizar nuestro servicio, he finalizado esta conversación por inactividad.

Si necesitas ayuda nuevamente, envía *hola* para iniciar una nueva sesión.

¡Gracias por contactar Sintestesia! 🙏"""
    
    return None

def obtener_productos_disponibles(db: Session, tenant_id: str = None):
    """Obtiene productos disponibles consultando ambas tablas y validando stock - filtrado por tenant"""
    # Consultar productos principales con stock filtrado por tenant
    query = db.query(Product).filter(
        Product.status.in_(["Active", "active"]),
        Product.stock > 0
    )
    
    if tenant_id:
        query = query.filter(Product.client_id == tenant_id)
    
    productos_principales = query.all()
    
    # Consultar productos Flow filtrados por tenant
    productos_flow = db.query(FlowProduct).filter_by(tenant_id=tenant_id).all() if tenant_id else db.query(FlowProduct).all()
    
    # Sincronizar: crear productos Flow que no existen pero sí en principales
    flow_nombres = {p.nombre for p in productos_flow}
    
    for producto in productos_principales:
        if producto.name not in flow_nombres:
            # Crear producto Flow correspondiente
            precio = float(producto.sale_price) if producto.sale_price else float(producto.price)
            flow_product = FlowProduct(
                nombre=producto.name,
                precio=precio,
                descripcion=producto.description or f"{producto.name} - {producto.category}",
                tenant_id=tenant_id or "default-tenant"
            )
            db.add(flow_product)
            print(f"🔄 Sincronizando: {producto.name} -> FlowProduct")
    
    # Commit cambios de sincronización
    db.commit()
    
    # Obtener productos Flow actualizados con información de stock filtrados por tenant
    productos_flow = db.query(FlowProduct).filter_by(tenant_id=tenant_id).all() if tenant_id else db.query(FlowProduct).all()
    productos_disponibles = []
    
    for flow_prod in productos_flow:
        # Buscar producto principal correspondiente para verificar stock (tenant-aware)
        query = db.query(Product).filter(
            Product.name == flow_prod.nombre,
            Product.status.in_(["Active", "active"])
        )
        
        if tenant_id:
            query = query.filter(Product.client_id == tenant_id)
            
        producto_principal = query.first()
        
        if producto_principal and producto_principal.stock > 0:
            # Actualizar precio si cambió
            precio_actual = float(producto_principal.sale_price) if producto_principal.sale_price else float(producto_principal.price)
            if flow_prod.precio != precio_actual:
                flow_prod.precio = precio_actual
                print(f"💰 Precio actualizado: {flow_prod.nombre} -> ${precio_actual}")
            
            # Agregar información de stock al producto Flow
            flow_prod.stock_disponible = producto_principal.stock
            productos_disponibles.append(flow_prod)
    
    # Commit actualizaciones de precios
    db.commit()
    
    return productos_disponibles

def obtener_productos(db: Session, tenant_id: str = None):
    """Función legacy que mantiene compatibilidad"""
    return obtener_productos_disponibles(db, tenant_id)

def procesar_mensaje_flow(db: Session, telefono: str, mensaje: str, tenant_id: str = None) -> str:
    """
    Procesa mensajes con lógica de Flow integrada - Prompt multitienda
    Compatible con sistema multi-tenant
    """
    # Obtener configuración dinámica de la tienda
    store_info = get_store_config(db, tenant_id)
    
    sesion = obtener_sesion(db, telefono, tenant_id)
    
    # Manejar comandos especiales de timeout
    mensaje_lower = mensaje.lower().strip()
    if mensaje_lower == "continuar":
        guardar_sesion(db, sesion, "INITIAL", {})
        return f"✅ ¡Perfecto! Continuemos donde estábamos.\n\n{menu_principal(store_info['name'])}"
    elif mensaje_lower == "finalizar":
        sesion.conversation_active = False
        sesion.estado = "FINALIZADA"
        db.commit()
        return f"👋 Conversación finalizada. ¡Gracias por contactar {store_info['name']}! Envía *hola* cuando necesites ayuda nuevamente."
    
    # Verificar timeout de conversación ANTES de procesar mensaje
    timeout_message = check_conversation_timeout(db, sesion)
    if timeout_message:
        return timeout_message
    
    # Si la conversación no está activa, reactivar con saludo
    if not sesion.conversation_active:
        guardar_sesion(db, sesion, "INITIAL", {}, True)
        sesion.conversation_active = True
        db.commit()
        return f"{store_info['greeting']}\n\n{menu_principal(store_info['name'])}"
    datos_sesion = json.loads(sesion.datos) if sesion.datos else {}
    
    mensaje_lower = mensaje.lower().strip()
    
    # Verificar pedido pendiente de pago (tenant-aware)
    pedido_pendiente = db.query(FlowPedido).filter_by(
        telefono=telefono,
        tenant_id=sesion.tenant_id,
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
    
    # Saludos - Saludo inicial con nombre de tienda
    if any(word in mensaje_lower for word in ["hola", "hi", "hello", "buenas", "menu", "inicio"]):
        guardar_sesion(db, sesion, "INITIAL", {})
        return f"¡Hola! Soy tu asistente de ventas de {store_info['name']}. ¿En qué puedo ayudarte hoy?"
    
    # Ver catálogo - Mostrar categorías primero, no todo el catálogo
    if mensaje_lower in ["ver catalogo", "ver catálogo", "productos", "catalog", "catálogo"]:
        productos = obtener_productos_disponibles(db, tenant_id)
        
        if not productos:
            return "Lo siento, no tenemos productos disponibles en este momento."
        
        # Obtener categorías únicas
        categorias = list(set([prod.descripcion.split(' - ')[1] if ' - ' in prod.descripcion else 'General' for prod in productos]))
        
        respuesta = f"Estas son nuestras categorías disponibles en {store_info['name']}:\n\n"
        for i, categoria in enumerate(categorias, 1):
            respuesta += f"{i}. {categoria}\n"
        
        respuesta += "\n¿Qué tipo de producto te interesa?"
        guardar_sesion(db, sesion, "BROWSING", {})
        return respuesta
    
    # Procesamiento con OpenAI para extraer productos
    if sesion.estado in ["INITIAL", "BROWSING"] or any(word in mensaje_lower for word in ["quiero", "necesito", "comprar", "llevar"]):
        productos = obtener_productos(db, tenant_id)
        
        if OPENAI_AVAILABLE and productos:
            # Usar OpenAI para interpretar el pedido
            productos_lista = "\n".join([f"- {prod.nombre} (ID: {prod.id}, Precio: ${prod.precio})" for prod in productos])
            
            prompt = f"""
            Eres un asistente de ventas multitienda. Atiendes en nombre de {store_info['name']}, una tienda especializada en {store_info['type']}. Tu misión es ayudar al cliente a comprar de forma sencilla y agradable.
            
            PRODUCTOS DISPONIBLES EN {store_info['name']}:
            {productos_lista}
            
            MENSAJE DEL CLIENTE: "{mensaje}"
            
            ANÁLISIS REQUERIDO:
            1. Si menciona un producto ESPECÍFICO de la lista → marca "comprar"
            2. Si consulta es GENERAL ("quiero comprar algo", "qué tienes") → marca "consulta_general"  
            3. Si pide algo que NO existe en {store_info['name']} → marca "no_disponible"
            4. Si hace preguntas sobre productos → marca "consulta"
            
            REGLAS:
            - NUNCA inventes productos no listados en {store_info['name']}
            - Solo usa nombres EXACTOS del inventario
            - Si no existe, informa que no lo tienes y sugiere un producto similar de {store_info['type']}
            
            RESPUESTA JSON:
            {{
                "productos": [
                    {{"id": <id_producto>, "nombre": "<nombre_exacto>", "cantidad": <cantidad>, "precio": <precio>}}
                ],
                "intencion": "comprar" | "consulta" | "consulta_general" | "no_disponible" | "otro"
            }}
            """
            
            try:
                import openai
                client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1
                )
                
                content = response.choices[0].message.content.strip()
                print(f"🤖 OpenAI respuesta: {content}")
                
                # Limpiar respuesta si tiene markdown
                if content.startswith("```json"):
                    content = content.replace("```json", "").replace("```", "").strip()
                
                result = json.loads(content)
                
                if result["intencion"] == "comprar" and result["productos"]:
                    pedido_detectado = {}
                    for item in result["productos"]:
                        pedido_detectado[item["id"]] = {
                            "nombre": item["nombre"],
                            "precio": item["precio"],
                            "cantidad": item["cantidad"]
                        }
                elif result["intencion"] == "consulta_general":
                    # Para consultas generales, ofrecer las categorías disponibles
                    categorias = list(set([prod.descripcion.split(' - ')[1] if ' - ' in prod.descripcion else 'General' for prod in productos]))
                    
                    respuesta = f"Estas son las categorías de productos que tenemos en {store_info['name']}:\n\n"
                    for i, categoria in enumerate(categorias, 1):
                        respuesta += f"{i}. {categoria}\n"
                    
                    respuesta += "\n¿Qué tipo de producto te interesa?"
                    return respuesta
                
                elif result["intencion"] == "no_disponible":
                    # Informar que no se tiene el producto y sugerir similares
                    return f"""Lo siento, el producto que buscas no está disponible en {store_info['name']}.
                    
¿Te interesa algún producto similar de {store_info['type']}? 

Escribe "ver catálogo" para conocer nuestros productos disponibles."""
                else:
                    pedido_detectado = {}
                    
            except Exception as e:
                print(f"Error con OpenAI: {e}")
                # Fallback a lógica simple mejorada
                pedido_detectado = {}
                productos_info = {prod.nombre.lower(): {"id": prod.id, "nombre": prod.nombre, "precio": prod.precio} 
                                for prod in productos}
                
                # Buscar productos mencionados
                for nombre_prod, info in productos_info.items():
                    # Buscar variaciones del nombre
                    palabras_producto = nombre_prod.split()
                    if any(palabra in mensaje_lower for palabra in palabras_producto if len(palabra) > 3):
                        pedido_detectado[info["id"]] = {
                            "nombre": info["nombre"],
                            "precio": info["precio"],
                            "cantidad": 1
                        }
                
                # Si no encontró nada, pedir más específico
                if not pedido_detectado:
                    return f"""No entendí bien qué producto buscas en {store_info['name']}.

¿Podrías ser más específico? Escribe "ver catálogo" para conocer nuestros productos disponibles."""
        else:
            pedido_detectado = {}
        
        if pedido_detectado:
            # VALIDAR STOCK DISPONIBLE
            productos_sin_stock = []
            pedido_validado = {}
            
            for prod_id, item in pedido_detectado.items():
                # Buscar producto principal para verificar stock (tenant-aware)
                query = db.query(Product).filter(Product.name == item["nombre"])
                if tenant_id:
                    query = query.filter(Product.client_id == tenant_id)
                producto_principal = query.first()
                
                if producto_principal:
                    if producto_principal.stock >= item["cantidad"]:
                        pedido_validado[prod_id] = item
                    else:
                        productos_sin_stock.append({
                            "nombre": item["nombre"], 
                            "solicitado": item["cantidad"],
                            "disponible": producto_principal.stock
                        })
                else:
                    productos_sin_stock.append({
                        "nombre": item["nombre"],
                        "solicitado": item["cantidad"], 
                        "disponible": 0
                    })
            
            # Si hay productos sin stock suficiente
            if productos_sin_stock:
                mensaje_stock = "⚠️ *Problemas de stock:*\n"
                for item in productos_sin_stock:
                    if item["disponible"] == 0:
                        mensaje_stock += f"- {item['nombre']}: Sin stock\n"
                    else:
                        mensaje_stock += f"- {item['nombre']}: Solo quedan {item['disponible']} (pediste {item['solicitado']})\n"
                
                if pedido_validado:
                    mensaje_stock += "\n✅ *Productos disponibles:*\n"
                    for item in pedido_validado.values():
                        mensaje_stock += f"- {item['cantidad']} x {item['nombre']}\n"
                    mensaje_stock += "\n👉 ¿Quieres confirmar solo los productos disponibles? (sí o no)"
                else:
                    mensaje_stock += "\n❌ Ningún producto está disponible en las cantidades solicitadas."
                    return mensaje_stock
                
                total = sum(item["precio"] * item["cantidad"] for item in pedido_validado.values())
                guardar_sesion(db, sesion, "ORDER_CONFIRMATION", {"pedido": pedido_validado, "total": total})
                return mensaje_stock
            
            # Todo el pedido tiene stock suficiente
            total = sum(item["precio"] * item["cantidad"] for item in pedido_validado.values())
            
            resumen = f"Perfecto! He encontrado este producto en {store_info['name']}:\n\n"
            for item in pedido_validado.values():
                resumen += f"• {item['nombre']} - ${item['precio']:.0f}\n"
                resumen += f"  Cantidad: {item['cantidad']}\n"
            resumen += f"\n**Total: ${total:.0f}**\n\n¿Deseas confirmar la compra? Responde SÍ para confirmar o NO para cancelar."
            
            guardar_sesion(db, sesion, "ORDER_CONFIRMATION", {"pedido": pedido_validado, "total": total})
            return resumen
    
    # Confirmación de pedido
    if sesion.estado == "ORDER_CONFIRMATION":
        # Usar OpenAI para interpretar confirmación
        confirmacion = False
        if OPENAI_AVAILABLE:
            try:
                import openai
                client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                
                prompt = f"""
                Analiza si este mensaje es una confirmación positiva (sí) o negativa (no).
                
                Mensaje: "{mensaje}"
                
                Responde SOLO con "si", "no" o "incierto"
                """
                
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0
                )
                
                respuesta_ai = response.choices[0].message.content.strip().lower()
                confirmacion = respuesta_ai == "si"
                
            except Exception as e:
                print(f"Error interpretando confirmación: {e}")
                confirmacion = any(word in mensaje_lower for word in ["sí", "si", "yes", "confirmo", "ok"])
        else:
            confirmacion = any(word in mensaje_lower for word in ["sí", "si", "yes", "confirmo", "ok"])
            
        if confirmacion:
            datos = json.loads(sesion.datos)
            pedido_data = datos["pedido"]
            total = datos["total"]
            
            # Crear pedido en BD
            pedido = FlowPedido(
                telefono=telefono,
                tenant_id=sesion.tenant_id,
                total=total,
                estado="pendiente_pago"
            )
            db.add(pedido)
            db.commit()
            db.refresh(pedido)
            
            # Crear productos del pedido y ACTUALIZAR STOCK
            for prod_id, item in pedido_data.items():
                # Crear registro del producto en el pedido
                producto_pedido = FlowProductoPedido(
                    pedido_id=pedido.id,
                    producto_id=int(prod_id),
                    cantidad=item["cantidad"],
                    precio_unitario=item["precio"]
                )
                db.add(producto_pedido)
                
                # ACTUALIZAR STOCK EN EL BACKOFFICE (tenant-aware)
                query = db.query(Product).filter(Product.name == item["nombre"])
                if tenant_id:
                    query = query.filter(Product.client_id == tenant_id)
                producto_principal = query.first()
                if producto_principal:
                    stock_anterior = producto_principal.stock
                    producto_principal.stock -= item["cantidad"]
                    
                    # Evitar stock negativo
                    if producto_principal.stock < 0:
                        producto_principal.stock = 0
                    
                    # Cambiar estado si se queda sin stock
                    if producto_principal.stock == 0:
                        producto_principal.status = "OutOfStock"
                        print(f"📦 {item['nombre']}: Stock agotado - Estado cambiado a OutOfStock")
                    
                    print(f"📊 Stock actualizado: {item['nombre']} - {stock_anterior} → {producto_principal.stock}")
            
            db.commit()
            
            # Crear orden de pago en Flow
            descripcion = f"Pedido_{store_info['name']}_{pedido.id}"
            url_pago = crear_orden_flow(str(pedido.id), int(total), descripcion, db, sesion.tenant_id)
            
            # Preparar resumen del pedido
            resumen_productos = "\n".join([f"{item['cantidad']} x {item['nombre']}" 
                                         for item in pedido_data.values()])
            
            respuesta = f"""✅ Pedido confirmado #{pedido.id}: {resumen_productos}
Total: ${total:.0f}
👉 Para continuar, realiza el pago aquí:
{url_pago}

Cuando termines el pago, escribe *pagado* para confirmar."""
            
            guardar_sesion(db, sesion, "ORDER_SCHEDULING", {"pedido_id": pedido.id})
            return respuesta
            
        elif any(word in mensaje_lower for word in ["no", "cancelar", "cancel"]):
            guardar_sesion(db, sesion, "INITIAL", {})
            return f"Pedido cancelado. ¿Hay algo más en lo que pueda ayudarte en {store_info['name']}?"
    
    # Consulta estado de pedido
    if mensaje_lower in ["mi pedido", "estado pedido", "pedido", "mis pedidos"]:
        pedidos = db.query(FlowPedido).filter_by(telefono=telefono, tenant_id=sesion.tenant_id).all()
        if pedidos:
            respuesta = f"Estos son tus pedidos en {store_info['name']}:\n\n"
            for pedido in pedidos[-3:]:  # Últimos 3 pedidos
                estado_emoji = {"pendiente_pago": "⏳ Pendiente de pago", "pagado": "✅ Pagado", "cancelado": "❌ Cancelado"}
                respuesta += f"Pedido #{pedido.id}\n"
                respuesta += f"Estado: {estado_emoji.get(pedido.estado, '❓ ' + pedido.estado)}\n"
                respuesta += f"Total: ${pedido.total:.0f}\n"
                respuesta += f"Fecha: {pedido.created_at.strftime('%d/%m/%Y')}\n\n"
            return respuesta
        else:
            return f"No tienes pedidos registrados en {store_info['name']}."
    
    # Respuesta por defecto - mantener concisa según el prompt
    return f"No entendí tu mensaje. ¿Puedes ser más específico sobre qué necesitas en {store_info['name']}? Puedes escribir 'ver catálogo' o el nombre de algún producto."