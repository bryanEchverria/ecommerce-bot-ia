"""
Chat service integrado con Flow para pagos
Multi-tenant compatible
"""
import json
import os
from sqlalchemy.orm import Session
from models import FlowProduct, FlowPedido, FlowProductoPedido, FlowSesion, Product
from services.flow_service import crear_orden_flow
from datetime import datetime

# OpenAI integration (if available)
try:
    import openai
    openai.api_key = os.getenv("OPENAI_API_KEY")
    OPENAI_AVAILABLE = bool(os.getenv("OPENAI_API_KEY"))
except ImportError:
    OPENAI_AVAILABLE = False

# Configuración simplificada sin multi-tenant
STORE_CONFIG = {
    "name": "Sintestesia",
    "type": "electronics", 
    "greeting": "📱 ¡Hola! Bienvenido a Sintestesia 📱💻\nTu tienda de tecnología favorita."
}

def menu_principal():
    return """🤖 *Bienvenido al Bot Automatizado* 🤖
Elige una opción:
1️⃣ Ver catálogo
2️⃣ Hablar con un ejecutivo  
3️⃣ Reportar un problema
4️⃣ Consultar estado de mi pedido"""

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

def guardar_sesion(db: Session, sesion, estado: str = None, datos: dict = None):
    """Guarda cambios en la sesión"""
    if estado:
        sesion.estado = estado
    if datos:
        sesion.datos = json.dumps(datos)
    sesion.updated_at = datetime.utcnow()
    db.commit()

def obtener_productos_disponibles(db: Session):
    """Obtiene productos disponibles consultando ambas tablas y validando stock"""
    # Consultar productos principales con stock
    productos_principales = db.query(Product).filter(
        Product.status.in_(["Active", "active"]),
        Product.stock > 0
    ).all()
    
    # Consultar productos Flow
    productos_flow = db.query(FlowProduct).all()
    
    # Sincronizar: crear productos Flow que no existen pero sí en principales
    flow_nombres = {p.nombre for p in productos_flow}
    
    for producto in productos_principales:
        if producto.name not in flow_nombres:
            # Crear producto Flow correspondiente
            precio = float(producto.sale_price) if producto.sale_price else float(producto.price)
            flow_product = FlowProduct(
                nombre=producto.name,
                precio=precio,
                descripcion=producto.description or f"{producto.name} - {producto.category}"
            )
            db.add(flow_product)
            print(f"🔄 Sincronizando: {producto.name} -> FlowProduct")
    
    # Commit cambios de sincronización
    db.commit()
    
    # Obtener productos Flow actualizados con información de stock
    productos_flow = db.query(FlowProduct).all()
    productos_disponibles = []
    
    for flow_prod in productos_flow:
        # Buscar producto principal correspondiente para verificar stock
        producto_principal = db.query(Product).filter(
            Product.name == flow_prod.nombre,
            Product.status.in_(["Active", "active"])
        ).first()
        
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

def obtener_productos(db: Session):
    """Función legacy que mantiene compatibilidad"""
    return obtener_productos_disponibles(db)

def procesar_mensaje_flow(db: Session, telefono: str, mensaje: str) -> str:
    """
    Procesa mensajes con lógica de Flow integrada
    Sistema simplificado sin multi-tenant
    """
    # Usar configuración única de tienda
    store_info = STORE_CONFIG
    
    sesion = obtener_sesion(db, telefono)
    datos_sesion = json.loads(sesion.datos) if sesion.datos else {}
    
    mensaje_lower = mensaje.lower().strip()
    
    # Verificar pedido pendiente de pago
    pedido_pendiente = db.query(FlowPedido).filter_by(
        telefono=telefono,
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
        return store_info["greeting"] + "\n\n" + menu_principal()
    
    # Ver catálogo
    if mensaje_lower in ["1", "ver catalogo", "ver catálogo", "productos", "catalog"]:
        productos = obtener_productos_disponibles(db)
        catalogo = f"📦 *Catálogo de {store_info['name']}:*\n"
        for prod in productos:
            stock_info = f" (Stock: {getattr(prod, 'stock_disponible', '?')})" if hasattr(prod, 'stock_disponible') else ""
            catalogo += f"- {prod.nombre} (${prod.precio:.0f}){stock_info}\n"
        
        if not productos:
            catalogo += "❌ No hay productos disponibles en este momento.\n"
        else:
            catalogo += "\n👉 ¿Quieres comprar algo? Escríbeme qué necesitas."
            
        guardar_sesion(db, sesion, "BROWSING", {})
        return catalogo
    
    # Procesamiento con OpenAI para extraer productos
    if sesion.estado in ["INITIAL", "BROWSING"] or any(word in mensaje_lower for word in ["quiero", "necesito", "comprar", "llevar"]):
        productos = obtener_productos(db)
        
        if OPENAI_AVAILABLE and productos:
            # Usar OpenAI para interpretar el pedido
            productos_lista = "\n".join([f"- {prod.nombre} (ID: {prod.id}, Precio: ${prod.precio})" for prod in productos])
            
            prompt = f"""
            Eres un asistente de ventas ESTRICTO. Analiza este mensaje del cliente y extrae SOLO los productos que existen en la lista.
            
            PRODUCTOS DISPONIBLES (SOLO ESTOS EXISTEN):
            {productos_lista}
            
            Mensaje del cliente: "{mensaje}"
            
            REGLAS ESTRICTAS:
            1. NUNCA menciones productos que NO estén en la lista disponible
            2. NUNCA inventes productos como "VapoTech", "Valotech", etc.
            3. Si el cliente pide algo que NO existe, marca intencion como "no_disponible"
            4. Solo usa nombres EXACTOS de la lista
            5. Si no especifica cantidad, asumir 1
            
            Responde SOLO en formato JSON válido:
            {{
                "productos": [
                    {{"id": <id_producto>, "nombre": "<nombre_exacto>", "cantidad": <cantidad>, "precio": <precio>}}
                ],
                "intencion": "comprar" | "consulta" | "no_disponible" | "otro"
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
                elif result["intencion"] == "no_disponible":
                    return f"""❌ Lo siento, el producto que buscas no está disponible en nuestro catálogo actual.
                    
📦 *Productos disponibles en {store_info['name']}:*
{chr(10).join([f"- {prod.nombre} (${prod.precio:.0f})" for prod in productos])}

👉 ¿Te interesa alguno de estos productos?"""
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
                
                # Si no encontró nada, mostrar catálogo
                if not pedido_detectado:
                    return f"""🤔 No entendí bien qué producto buscas.
                    
📦 *Productos disponibles en {store_info['name']}:*
{chr(10).join([f"- {prod.nombre} (${prod.precio:.0f})" for prod in productos])}

👉 ¿Podrías ser más específico sobre qué producto quieres?"""
        else:
            pedido_detectado = {}
        
        if pedido_detectado:
            # VALIDAR STOCK DISPONIBLE
            productos_sin_stock = []
            pedido_validado = {}
            
            for prod_id, item in pedido_detectado.items():
                # Buscar producto principal para verificar stock
                producto_principal = db.query(Product).filter(Product.name == item["nombre"]).first()
                
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
            
            resumen = "🔎 Esto es lo que entendí:\n"
            for item in pedido_validado.values():
                resumen += f"{item['cantidad']} x {item['nombre']}\n"
            resumen += f"Total: ${total:.0f}\n👉 ¿Confirmas tu pedido? (sí o no)"
            
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
                
                # ACTUALIZAR STOCK EN EL BACKOFFICE
                producto_principal = db.query(Product).filter(Product.name == item["nombre"]).first()
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
            url_pago = crear_orden_flow(str(pedido.id), int(total), descripcion, db)
            
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
            return "❌ Pedido cancelado.\n" + menu_principal()
    
    # Otras opciones del menú
    if mensaje_lower == "2":
        return "📞 Para hablar con un ejecutivo, puedes llamarnos al +56 9 1234 5678\n\n" + menu_principal()
    
    if mensaje_lower == "3":
        return "🐛 Para reportar un problema, envía un email a soporte@empresa.com\n\n" + menu_principal()
    
    if mensaje_lower == "4":
        pedidos = db.query(FlowPedido).filter_by(telefono=telefono).all()
        if pedidos:
            respuesta = f"📋 Tus pedidos en {store_info['name']}:\n\n"
            for pedido in pedidos[-3:]:  # Últimos 3 pedidos
                estado_emoji = {"pendiente_pago": "⏳", "pagado": "✅", "cancelado": "❌"}
                respuesta += f"{estado_emoji.get(pedido.estado, '❓')} Pedido #{pedido.id}\n"
                respuesta += f"   Total: ${pedido.total:.0f} - {pedido.estado.title()}\n"
                respuesta += f"   Fecha: {pedido.created_at.strftime('%d/%m/%Y')}\n\n"
            return respuesta + menu_principal()
        else:
            return f"No tienes pedidos registrados en {store_info['name']}.\n\n" + menu_principal()
    
    # Respuesta por defecto mejorada
    return f"🤖 {store_info['name']} - Asistente Virtual\n\n📱 Recibí: \"{mensaje}\"\n\n💡 Puedo ayudarte con:\n• Ver catálogo de productos\n• Procesar pedidos\n• Consultar estado de compras\n• Información general\n\n" + menu_principal()