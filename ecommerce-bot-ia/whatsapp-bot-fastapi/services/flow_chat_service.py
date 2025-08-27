"""
Chat service integrado con Flow para pagos
Multi-tenant compatible
"""
import json
import os
from sqlalchemy.orm import Session
from models import FlowProduct, FlowPedido, FlowProductoPedido, FlowSesion
from services.flow_service import crear_orden_flow, get_client_id_for_phone
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
            client_id=client_id,
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

def obtener_productos_cliente(db: Session, client_id: str):
    """Obtiene los productos disponibles para un cliente"""
    productos = db.query(FlowProduct).filter_by(client_id=client_id).all()
    if not productos:
        # Crear productos de ejemplo si no existen
        productos_ejemplo = [
            {"nombre": "Pan", "precio": 1000, "descripcion": "Pan fresco artesanal"},
            {"nombre": "Bebida", "precio": 1500, "descripcion": "Bebida refrescante natural"}
        ]
        
        for prod_data in productos_ejemplo:
            producto = FlowProduct(
                nombre=prod_data["nombre"],
                precio=prod_data["precio"], 
                descripcion=prod_data["descripcion"],
                client_id=client_id
            )
            db.add(producto)
        
        db.commit()
        productos = db.query(FlowProduct).filter_by(client_id=client_id).all()
    
    return productos

def procesar_mensaje_flow(db: Session, telefono: str, mensaje: str) -> str:
    """
    Procesa mensajes con lógica de Flow integrada
    Multi-tenant compatible
    """
    # Obtener información del cliente
    client_info = TENANT_CLIENTS.get(telefono)
    if not client_info:
        return f"""❌ Cliente no configurado: {telefono}
        
✅ Clientes válidos:
• +3456789012 → Green House (canábicos)
• +1234567890 → Demo Company (electrónicos)  
• +5678901234 → Mundo Canino (mascotas)
• +9876543210 → Test Store (ropa)

🧪 PRUEBA: Usa uno de estos números"""

    client_id = client_info["client_id"]
    sesion = obtener_sesion(db, telefono, client_id)
    datos_sesion = json.loads(sesion.datos) if sesion.datos else {}
    
    mensaje_lower = mensaje.lower().strip()
    
    # Verificar pedido pendiente de pago
    pedido_pendiente = db.query(FlowPedido).filter_by(
        telefono=telefono,
        client_id=client_id,
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
    if mensaje_lower in ["1", "ver catalogo", "ver catálogo", "productos", "catalog"]:
        productos = obtener_productos_cliente(db, client_id)
        catalogo = f"📦 *Catálogo de {client_info['name']}:*\n"
        for prod in productos:
            catalogo += f"- {prod.nombre} (${prod.precio:.0f})\n"
        catalogo += "\n👉 ¿Quieres comprar algo? Escríbeme qué necesitas."
        guardar_sesion(db, sesion, "BROWSING", {})
        return catalogo
    
    # Procesamiento con OpenAI para extraer productos
    if sesion.estado in ["INITIAL", "BROWSING"] or any(word in mensaje_lower for word in ["quiero", "necesito", "comprar", "llevar"]):
        # Usar OpenAI para procesar el pedido
        productos = obtener_productos_cliente(db, client_id)
        productos_info = {prod.nombre.lower(): {"id": prod.id, "nombre": prod.nombre, "precio": prod.precio} 
                         for prod in productos}
        
        # Lógica simple de procesamiento de pedidos
        pedido_detectado = {}
        for nombre_prod, info in productos_info.items():
            if nombre_prod in mensaje_lower:
                # Buscar cantidad
                cantidad = 1
                for word in mensaje.split():
                    if word.isdigit():
                        cantidad = int(word)
                        break
                
                pedido_detectado[info["id"]] = {
                    "nombre": info["nombre"],
                    "precio": info["precio"],
                    "cantidad": cantidad
                }
        
        if pedido_detectado:
            total = sum(item["precio"] * item["cantidad"] for item in pedido_detectado.values())
            
            resumen = "🔎 Esto es lo que entendí:\n"
            for item in pedido_detectado.values():
                resumen += f"{item['cantidad']} x {item['nombre']}\n"
            resumen += f"Total: ${total:.0f}\n👉 ¿Confirmas tu pedido? (sí o no)"
            
            guardar_sesion(db, sesion, "ORDER_CONFIRMATION", {"pedido": pedido_detectado, "total": total})
            return resumen
    
    # Confirmación de pedido
    if sesion.estado == "ORDER_CONFIRMATION":
        if any(word in mensaje_lower for word in ["sí", "si", "yes", "confirmo", "ok"]):
            datos = json.loads(sesion.datos)
            pedido_data = datos["pedido"]
            total = datos["total"]
            
            # Crear pedido en BD
            pedido = FlowPedido(
                telefono=telefono,
                client_id=client_id,
                total=total,
                estado="pendiente_pago"
            )
            db.add(pedido)
            db.commit()
            db.refresh(pedido)
            
            # Crear productos del pedido
            for prod_id, item in pedido_data.items():
                producto_pedido = FlowProductoPedido(
                    pedido_id=pedido.id,
                    producto_id=int(prod_id),
                    cantidad=item["cantidad"],
                    precio_unitario=item["precio"]
                )
                db.add(producto_pedido)
            
            db.commit()
            
            # Crear orden de pago en Flow
            descripcion = f"Pedido_{client_info['name']}_{pedido.id}"
            url_pago = crear_orden_flow(str(pedido.id), int(total), descripcion, client_id, db)
            
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
        pedidos = db.query(FlowPedido).filter_by(telefono=telefono, client_id=client_id).all()
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
    
    # Respuesta por defecto mejorada
    return f"🤖 {client_info['name']} - Asistente Virtual\n\n📱 Recibí: \"{mensaje}\"\n\n💡 Puedo ayudarte con:\n• Ver catálogo de productos\n• Procesar pedidos\n• Consultar estado de compras\n• Información general\n\n" + menu_principal()