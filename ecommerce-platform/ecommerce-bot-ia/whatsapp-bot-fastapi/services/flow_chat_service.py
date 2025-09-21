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

# Smart flows integration
try:
    from services.smart_flows import detectar_intencion_con_gpt, ejecutar_flujo_inteligente
    SMART_FLOWS_AVAILABLE = True
except ImportError:
    SMART_FLOWS_AVAILABLE = False

# AI Improvements integration (TEMPORALMENTE DESHABILITADO)
try:
    from services.ai_improvements import process_message_with_ai_improvements
    AI_IMPROVEMENTS_AVAILABLE = False  # Force disable para que smart_flows funcione
except ImportError:
    AI_IMPROVEMENTS_AVAILABLE = False

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
}

def menu_principal(client_info, productos):
    """Muestra el catálogo de productos directamente en lugar de un menú genérico"""
    catalogo = f"🌿 *{client_info['name']} - Catálogo disponible:*\n\n"
    for i, prod in enumerate(productos, 1):
        stock_status = "✅ Disponible" if prod['stock'] > 5 else f"⚠️ Quedan {prod['stock']}"
        catalogo += f"{i}. **{prod['name']}** - ${prod['price']:,.0f}\n"
        catalogo += f"   {prod['description']}\n"
        catalogo += f"   {stock_status}\n\n"
    catalogo += "💬 *Para comprar:* Escribe el nombre del producto que quieres\n"
    catalogo += "📝 *Ejemplo:* 'Quiero Northern Lights' o solo 'Northern Lights'"
    return catalogo

def obtener_sesion(db: Session, telefono: str, tenant_id: str):
    """Obtiene o crea una sesión para el usuario"""
    sesion = db.query(FlowSesion).filter_by(telefono=telefono).first()
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

def guardar_sesion(db: Session, sesion, estado: str = None, datos: dict = None):
    """Guarda cambios en la sesión"""
    if estado:
        sesion.estado = estado
    if datos:
        sesion.datos = json.dumps(datos)
    sesion.updated_at = datetime.utcnow()
    db.commit()

def obtener_productos_cliente_real(db: Session, telefono: str, tenant_id: str = None):
    """
    Obtiene productos reales del backoffice en tiempo real
    COMPLETAMENTE DINÁMICO - Multi-tenant compatible
    Puede usar número de teléfono o tenant_id directamente
    """
    # Si no se proporciona tenant_id, obtenerlo del teléfono
    if tenant_id is None:
        tenant_id = get_tenant_from_phone(telefono, db)
    
    productos = get_real_products_from_backoffice(db, tenant_id)
    tenant_info = get_tenant_info(tenant_id, db)
    
    return productos, tenant_id, tenant_info

def procesar_mensaje_flow(db: Session, telefono: str, mensaje: str, tenant_id: str = None) -> str:
    """
    Procesa mensajes con lógica de Flow integrada
    Multi-tenant compatible - consulta productos reales del backoffice
    """
    print(f"🚀🚀🚀 ENTRANDO A PROCESAR_MENSAJE_FLOW: '{mensaje}' para tenant: {tenant_id}")
    # Si se proporciona tenant_id directamente (webhooks dinámicos), usarlo
    # Si no, obtener información del tenant basado en el teléfono (DINÁMICO)
    if tenant_id is None:
        tenant_id = get_tenant_from_phone(telefono, db)
    
    tenant_info = get_tenant_info(tenant_id, db)
    
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

    sesion = obtener_sesion(db, telefono, tenant_id)
    datos_sesion = json.loads(sesion.datos) if sesion.datos else {}
    
    mensaje_lower = mensaje.lower().strip()
    
    # ========================================
    # PRIORIDAD ABSOLUTA: CONFIRMACIÓN DE PEDIDOS
    # ========================================
    if sesion.estado == "ORDER_CONFIRMATION":
        print(f"⚠️ Estado ORDER_CONFIRMATION detectado, mensaje: '{mensaje}'")
        if any(word in mensaje_lower for word in ["sí", "si", "yes", "confirmo", "ok", "acepto"]):
            print(f"✅ Confirmación detectada!")
            datos = json.loads(sesion.datos)
            pedido_data = datos["pedido"]
            total = datos["total"]
            
            # Obtener datos del tenant para el pedido
            productos, tenant_id, tenant_info = obtener_productos_cliente_real(db, telefono, tenant_id)
            
            # Crear pedido en BD
            pedido = FlowPedido(
                telefono=telefono,
                tenant_id=tenant_id,
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
            return "❌ **Pedido cancelado**\n\n¿En qué más puedo ayudarte?"
        
        # Si escribe algo diferente durante la confirmación
        else:
            return f"❓ No entendí tu respuesta.\n\n⚡ **Responde claramente:**\n• **SÍ** - para confirmar el pedido\n• **NO** - para cancelar\n\n🔄 ¿Confirmas tu pedido?"
    
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
            productos, tenant_id, tenant_info = obtener_productos_cliente_real(db, telefono, tenant_id)
            return f"❌ Tu pedido #{pedido_pendiente.id} ha sido *cancelado*.\n" + menu_principal(tenant_info, productos)
        else:
            productos, tenant_id, tenant_info = obtener_productos_cliente_real(db, telefono, tenant_id)
            return "No tienes pedidos pendientes para cancelar.\n" + menu_principal(tenant_info, productos)
    
    # ========================================
    # ELIMINADA DETECCIÓN HARDCODEADA - AHORA TODO ES DINÁMICO CON GPT
    # El sistema GPT completamente dinámico maneja todas las intenciones
    # ========================================

    # ========================================
    # PRIORIDAD 2: SISTEMA DE IA MEJORADO CON CONTEXTO  
    # ========================================
    if AI_IMPROVEMENTS_AVAILABLE and OPENAI_AVAILABLE:
        try:
            print(f"🤖 Iniciando sistema IA mejorado para: '{mensaje}'")
            
            # Obtener productos para el contexto
            productos, tenant_id, tenant_info = obtener_productos_cliente_real(db, telefono, tenant_id)
            
            if productos:
                # Procesar mensaje con IA mejorada
                respuesta_ia, metadata_ia = process_message_with_ai_improvements(
                    db, telefono, tenant_id, mensaje, productos, tenant_info
                )
                
                print(f"✅ IA Mejorada respondió (confianza: {metadata_ia.get('intent_confidence', 0):.2f}, tiempo: {metadata_ia.get('response_time_ms', 0)}ms)")
                
                # Si la confianza es alta, usar la respuesta de IA (umbral reducido para testing)
                if metadata_ia.get('intent_confidence', 0) > 0.3:
                    return respuesta_ia
                
                # Si la confianza es media, continuar con smart flows como backup
                print(f"⚠️ Confianza media, continuando con smart flows...")
                
        except Exception as e:
            print(f"❌ Error en sistema IA mejorado: {e}")
            # Continuar con smart flows como fallback
    
    # ========================================
    # PRIORIDAD 3: SISTEMA DE FLUJOS INTELIGENTES (FALLBACK)
    # ========================================
    if SMART_FLOWS_AVAILABLE and OPENAI_AVAILABLE:
        try:
            print(f"🧠 Iniciando detección inteligente para: '{mensaje}'")
            
            # MANEJO DINÁMICO DE CONTEXTO DE CONVERSACIÓN USANDO GPT
            # GPT decide si el mensaje es una continuación de conversación basándose en el contexto
            contexto_conversacion = _manejar_contexto_dinamico_con_gpt(
                db, sesion, mensaje, datos_sesion, telefono, tenant_id
            )
            
            if contexto_conversacion:
                print(f"🔄 GPT detectó continuación de conversación: {contexto_conversacion['accion']}")
                return contexto_conversacion['respuesta']
            
            # Obtener productos para el contexto
            productos, tenant_id, tenant_info = obtener_productos_cliente_real(db, telefono, tenant_id)
            
            if productos:
                # GPT detecta la intención específica
                deteccion = detectar_intencion_con_gpt(mensaje, productos, tenant_info)
                print(f"🎯 GPT detectó: {deteccion}")
                
                # Ejecutar flujo específico según detección
                if deteccion["intencion"] in ["saludo", "consulta_producto", "consulta_categoria", "consulta_catalogo", "intencion_compra"]:
                    print(f"✅ Ejecutando flujo específico para: {deteccion['intencion']}")
                    
                    print(f"🚀 Ejecutando flujo inteligente para: {deteccion['intencion']}")
                    respuesta_inteligente = ejecutar_flujo_inteligente(deteccion, productos, tenant_info)
                    print(f"✅ Flujo inteligente retornó: {respuesta_inteligente[:100]}...")
                    print(f"📝 Respuesta generada: {len(respuesta_inteligente)} caracteres")
                    
                    # Actualizar sesión según el tipo de consulta
                    if deteccion["intencion"] == "consulta_categoria":
                        # Guardar la categoría consultada para mantener contexto
                        categoria_consultada = deteccion.get("categoria")
                        if categoria_consultada:
                            guardar_sesion(db, sesion, "BROWSING", {"ultima_categoria": categoria_consultada})
                        else:
                            guardar_sesion(db, sesion, "BROWSING", {})
                    elif deteccion["intencion"] == "consulta_catalogo":
                        guardar_sesion(db, sesion, "BROWSING", {})
                    elif deteccion["intencion"] == "intencion_compra":
                        # No actualizar sesión aquí, se maneja en la lógica de compras más abajo
                        pass
                    
                    print("🎉 Flujo inteligente completado exitosamente")
                    return respuesta_inteligente
                    
        except Exception as e:
            print(f"❌ Error en flujos inteligentes: {e}")
            import traceback
            traceback.print_exc()
    
    # SOLO SISTEMA GPT - Sin condiciones hardcodeadas
    # El sistema GPT debe manejar todos los casos: saludos, consultas de productos, etc.
    
    # Si llegamos aquí, el sistema GPT no manejó el mensaje, usar fallback GPT
    
    # ========================================
    # SISTEMA DINÁMICO ESCALABLE CON CONFIGURACIÓN DE TENANT
    # ========================================
    
    print(f"🔄 Activando sistema dinámico escalable para tenant: {tenant_id}")
    
    try:
        # Importar sistema dinámico
        from services.dynamic_tenant_bot import process_message_with_dynamic_ai
        
        # Obtener productos y información del tenant
        productos, tenant_id, tenant_info = obtener_productos_cliente_real(db, telefono, tenant_id)
        
        # Procesar con IA dinámica personalizada
        respuesta_dinamica = process_message_with_dynamic_ai(
            db=db,
            telefono=telefono,
            mensaje=mensaje,
            tenant_id=tenant_id,
            productos=productos,
            tenant_info=tenant_info
        )
        
        print(f"✅ Sistema dinámico respondió para {tenant_id}")
        return respuesta_dinamica
        
    except Exception as e:
        print(f"❌ Error en sistema dinámico para {tenant_id}: {e}")
        import traceback
        traceback.print_exc()
        
        # Fallback seguro con información real del tenant
        productos, tenant_id, tenant_info = obtener_productos_cliente_real(db, telefono, tenant_id)
        from services.dynamic_tenant_bot import get_dynamic_greeting_with_products
        
        return get_dynamic_greeting_with_products(tenant_info, productos)

def _manejar_contexto_dinamico_con_gpt(db: Session, sesion, mensaje: str, datos_sesion: dict, telefono: str, tenant_id: str):
    """
    Maneja el contexto de conversación de manera 100% dinámica usando GPT
    Sin lógica hardcodeada - GPT decide si el mensaje es una continuación
    """
    if not OPENAI_AVAILABLE:
        return None
    
    try:
        import openai
        client = openai.OpenAI()
        
        # Obtener información del contexto actual
        estado_sesion = sesion.estado
        contexto_anterior = datos_sesion.get('ultima_categoria', '')
        ultima_respuesta = datos_sesion.get('ultima_respuesta', '')
        
        # Solo procesar si hay contexto previo
        if not contexto_anterior and estado_sesion != "BROWSING":
            return None
        
        # PROMPT DINÁMICO PARA ANÁLISIS DE CONTEXTO
        contexto_prompt = f"""Analiza si este mensaje continúa una conversación previa.

CONVERSACIÓN PREVIA:
- Estado: {estado_sesion}
- Categoría anterior: {contexto_anterior or 'ninguna'}
- Última respuesta: {ultima_respuesta[:100] if ultima_respuesta else 'ninguna'}

MENSAJE ACTUAL: "{mensaje}"

TAREA: ¿Es este mensaje una continuación de la conversación anterior?

ANÁLISIS:
- Si el usuario responde afirmativamente → puede ser continuación
- Si cambia de tema completamente → nueva conversación
- Si hace seguimiento al tema anterior → continuación

RESPONDE UNA de estas opciones:
- "continuar_categoria" - continuar con la categoría que se consultó antes
- "continuar_catalogo" - mostrar catálogo general
- "nueva_conversacion" - iniciar nueva conversación

RESPUESTA:"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": contexto_prompt}],
            temperature=0.1,
            max_tokens=20
        )
        
        decision_gpt = response.choices[0].message.content.strip().lower()
        print(f"🧠 GPT decisión de contexto: '{decision_gpt}'")
        
        # Procesar decisión de GPT
        if decision_gpt == "continuar_categoria" and contexto_anterior:
            print(f"🔄 GPT: Continuando con categoría '{contexto_anterior}'")
            
            # Obtener productos y ejecutar consulta de categoría
            productos, _, tenant_info = obtener_productos_cliente_real(db, telefono, tenant_id)
            from services.smart_flows import ejecutar_consulta_categoria
            respuesta = ejecutar_consulta_categoria(contexto_anterior, productos, tenant_info)
            
            # Mantener contexto
            guardar_sesion(db, sesion, "BROWSING", {
                "ultima_categoria": contexto_anterior,
                "ultima_respuesta": respuesta[:200]
            })
            
            return {
                "accion": "continuar_categoria",
                "respuesta": respuesta
            }
            
        elif decision_gpt == "continuar_catalogo":
            print(f"🔄 GPT: Continuando con catálogo completo")
            
            # Mostrar catálogo completo
            productos, _, tenant_info = obtener_productos_cliente_real(db, telefono, tenant_id)
            from services.smart_flows import ejecutar_consulta_catalogo
            respuesta = ejecutar_consulta_catalogo(productos, tenant_info)
            
            # Actualizar contexto
            guardar_sesion(db, sesion, "BROWSING", {
                "ultima_respuesta": respuesta[:200]
            })
            
            return {
                "accion": "continuar_catalogo", 
                "respuesta": respuesta
            }
        
        else:
            print(f"🔄 GPT: Nueva conversación - no hay continuación")
            return None
            
    except Exception as e:
        print(f"❌ Error en manejo dinámico de contexto: {e}")
        return None