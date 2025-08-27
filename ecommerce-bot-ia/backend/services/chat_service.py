"""
Chat service integrado en el backend
Bot de WhatsApp con respuestas inteligentes y creación de órdenes reales
"""
import os
import json
import httpx
import uuid
from datetime import datetime
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_async_db
import crud_async

# Variables de configuración
OPENAI_AVAILABLE = bool(os.getenv("OPENAI_API_KEY"))

# Sistema de sesiones simple (en producción usar Redis)
user_sessions = {}

# OpenAI integration
if OPENAI_AVAILABLE:
    try:
        import openai
        openai.api_key = os.getenv("OPENAI_API_KEY")
    except ImportError:
        OPENAI_AVAILABLE = False

# Multi-tenant client mapping with database IDs
TENANT_CLIENTS = {
    "+3456789012": {
        "name": "Sintestesia",
        "type": "electronics",
        "client_id": "2ae13937-cbaa-45c5-b7bc-9c73586483de",
        "greeting": "¡Hola! Bienvenido a Sintestesia 📱💻\nTu tienda de tecnología favorita."
    },
    "+1234567890": {
        "name": "Demo Company", 
        "type": "electronics",
        "client_id": "11111111-1111-1111-1111-111111111111",
        "greeting": "¡Hola! Demo Company - Electrónicos 📱💻"
    },
    "+5678901234": {
        "name": "Mundo Canino",
        "type": "pets",
        "client_id": "22222222-2222-2222-2222-222222222222", 
        "greeting": "¡Hola! Mundo Canino - Productos para mascotas 🐕"
    },
    "+9876543210": {
        "name": "Test Store",
        "type": "clothing",
        "client_id": "33333333-3333-3333-3333-333333333333",
        "greeting": "¡Hola! Test Store - Ropa y accesorios 👕"
    },
    "+56950915617": {
        "name": "Sintestesia",
        "type": "electronics",
        "client_id": "2ae13937-cbaa-45c5-b7bc-9c73586483de",
        "greeting": "¡Hola! Bienvenido a Sintestesia 📱💻\nTu tienda de tecnología favorita."
    }
}

def get_client_info(telefono: str) -> Dict[str, Any]:
    """Get client information for the phone number"""
    # Si el número está configurado, usarlo
    if telefono in TENANT_CLIENTS:
        return TENANT_CLIENTS[telefono]
    
    # Para números desconocidos, asignar como cliente general de Sintestesia
    # Esto permitirá que cualquier número funcione cuando pagues Twilio
    return {
        "name": "Sintestesia",
        "type": "electronics", 
        "client_id": "2ae13937-cbaa-45c5-b7bc-9c73586483de",
        "greeting": "¡Hola! Bienvenido a Sintestesia 📱💻\nTu tienda de tecnología favorita."
    }

def get_user_session(telefono: str) -> Dict[str, Any]:
    """Get or create user session"""
    if telefono not in user_sessions:
        user_sessions[telefono] = {
            "stage": "initial",  # initial, selecting_quantity, confirming_purchase
            "selected_product": None,
            "quantity": 0,
            "total": 0.0
        }
    return user_sessions[telefono]

def clear_user_session(telefono: str):
    """Clear user session"""
    if telefono in user_sessions:
        del user_sessions[telefono]

async def create_real_order(customer_phone: str, product_name: str, quantity: int, total: float, client_info: Dict) -> Dict[str, str]:
    """Create a real order in the database directly"""
    try:
        order_data = {
            "customer_name": f"Cliente WhatsApp {customer_phone}",
            "client_id": client_info.get("client_id"),
            "date": datetime.now(),
            "total": total,
            "status": "pending",
            "items": quantity
        }
        
        order_id = str(uuid.uuid4())
        
        # Create order directly using database connection
        async for db in get_async_db():
            try:
                # Import here to avoid circular imports
                import crud_async
                
                # Create order in database
                created_order = await crud_async.create_order_async(
                    db=db, 
                    order=order_data, 
                    order_id=order_id
                )
                
                # Generate order number if not present
                order_number = created_order.order_number or f"WA-{order_id[:8].upper()}"
                
                # Generate Flow payment link
                try:
                    from services.flow_service import crear_orden_flow
                    from database import SessionLocal
                    from models import FlowPedido
                    
                    # Use sync session for Flow service
                    sync_db = SessionLocal()
                    try:
                        # Create FlowPedido entry
                        flow_pedido = FlowPedido(
                            telefono=customer_phone,
                            client_id=client_info.get("client_id", ""),
                            total=total,
                            estado="pendiente_pago"
                        )
                        sync_db.add(flow_pedido)
                        sync_db.flush()  # Get the ID without committing
                        flow_pedido_id = flow_pedido.id
                        sync_db.commit()
                        
                        payment_link = crear_orden_flow(
                            order_id=str(flow_pedido_id),
                            monto=int(total),
                            descripcion=f"{product_name} x{quantity}",
                            client_id=client_info.get("client_id", ""),
                            db=sync_db
                        )
                    finally:
                        sync_db.close()
                    
                    if "Error" in payment_link:
                        # Fallback to basic link if Flow fails
                        payment_link = f"https://app.sintestesia.cl/pay/{order_number}"
                        
                except ImportError:
                    # Fallback if Flow service not available
                    payment_link = f"https://app.sintestesia.cl/pay/{order_number}"
                
                return {
                    "order_id": order_id,
                    "order_number": order_number,
                    "payment_link": payment_link,
                    "status": "success"
                }
                
            except Exception as e:
                return {
                    "status": "error",
                    "message": f"Database error: {str(e)}"
                }
                
    except Exception as e:
        return {
            "status": "error", 
            "message": f"Error creating order: {str(e)}"
        }

async def get_client_products(client_id: str, search_term: str = None, limit: int = 5) -> List[Dict[str, Any]]:
    """Get products from database for a specific client"""
    try:
        async for db in get_async_db():
            # Get products filtered by client_id
            products = await crud_async.get_products_async(
                db, 
                skip=0, 
                limit=limit, 
                status="active", 
                client_id=client_id
            )
            
            # Convert SQLAlchemy objects to dict
            product_list = []
            for product in products:
                product_dict = {
                    "id": product.id,
                    "name": product.name,
                    "price": product.price,
                    "category": product.category,
                    "description": product.description,
                    "status": product.status,
                    "stock": getattr(product, 'stock', 0)
                }
                
                # Filter by search term if provided
                if search_term:
                    search_lower = search_term.lower()
                    if (search_lower in product.name.lower() or 
                        search_lower in product.description.lower() or 
                        search_lower in product.category.lower()):
                        product_list.append(product_dict)
                else:
                    product_list.append(product_dict)
            
            return product_list[:limit]
            
    except Exception as e:
        print(f"Error getting products: {e}")
        return []

async def process_with_openai(mensaje: str, client_info: Dict, products: List[Dict] = None, user_session: Dict = None) -> str:
    """Process message using OpenAI with real product data and purchase flow"""
    if not OPENAI_AVAILABLE:
        return None
    
    try:
        # Build product context
        product_context = ""
        if products:
            product_context = "\nProductos disponibles:\n"
            for product in products:
                product_context += f"- {product['name']}: ${product['price']:,} ({product['category']}) [ID: {product['id']}]\n"
        
        # Build session context
        session_context = ""
        if user_session and user_session.get('stage') != 'initial':
            session_context = f"\nEstado de la sesión: {user_session['stage']}"
            if user_session.get('selected_product'):
                session_context += f"\nProducto seleccionado: {user_session['selected_product']['name']} - ${user_session['selected_product']['price']:,}"
            if user_session.get('quantity', 0) > 0:
                session_context += f"\nCantidad: {user_session['quantity']}"
        
        prompt = f"""Eres un asistente de ventas experto para {client_info['name']}, especializada en {client_info['type']}.

Cliente escribió: "{mensaje}"
{product_context}
{session_context}

INSTRUCCIONES ESPECÍFICAS:
1. Si el cliente muestra interés en comprar un producto específico, pregunta por la cantidad
2. Si el cliente confirma cantidad, genera una respuesta con formato: "COMPRA_CONFIRMADA|product_id|quantity|product_name|price"
3. Si el cliente dice "sí", "confirmo", "comprar", "lo quiero", considera esto como confirmación de compra
4. Recomienda productos específicos de los disponibles
5. Ser muy útil y generar interés de compra

Categoría de productos: {client_info['type']}
Nombre de la tienda: {client_info['name']}

Responde en máximo 300 caracteres. Si detectas intención de compra, usa el formato especial."""

        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=120,
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content.strip()
        return f"🤖 {ai_response}"
        
    except Exception as e:
        print(f"OpenAI error: {e}")
        return None

async def procesar_mensaje(db, telefono: str, mensaje: str) -> str:
    """
    Función principal para procesar mensajes del bot
    """
    mensaje_lower = mensaje.lower().strip()
    client_info = get_client_info(telefono)
    
    # Handle unknown clients
    if client_info["type"] == "unknown":
        return f"""❌ Cliente no configurado: {telefono}

✅ Clientes válidos:
• +3456789012 → Sintestesia (electrónicos)
• +56950915617 → Sintestesia (electrónicos)  
• +1234567890 → Demo Company (electrónicos)
• +5678901234 → Mundo Canino (mascotas)
• +9876543210 → Test Store (ropa)

💡 Ahora uso OpenAI + BD para respuestas inteligentes """

    # Handle greetings
    if any(word in mensaje_lower for word in ["hola", "hi", "hello", "buenas"]):
        # Get some featured products for greeting
        try:
            if client_info.get("client_id"):
                featured_products = await get_client_products(client_info["client_id"], limit=3)
                if featured_products:
                    product_list = "\n".join([f"• {p['name']}: ${p['price']:,}" for p in featured_products])
                    return f"""{client_info['greeting']}

🔥 Productos destacados:
{product_list}

💡 ¿Qué estás buscando hoy?"""
        except Exception as e:
            print(f"Error getting featured products: {e}")
        
        return f"""{client_info['greeting']}

💡 Puedes preguntarme por productos o escribir lo que buscas.
Ejemplo: "vaporizador", "iPhone", "collar para perro", etc."""

    # Get user session for purchase flow
    user_session = get_user_session(telefono)
    
    # Handle purchase confirmations and flow
    compra_keywords = ["comprar", "lo quiero", "si lo quiero", "confirmo", "sí", "si", "compro", "lo llevo"]
    cantidad_keywords = ["1", "2", "3", "4", "5", "uno", "dos", "tres", "cuatro", "cinco", "unidad", "unidades"]
    
    # Check for quantity responses
    if user_session.get('stage') == 'selecting_quantity':
        for keyword in cantidad_keywords:
            if keyword in mensaje_lower:
                try:
                    if keyword.isdigit():
                        quantity = int(keyword)
                    else:
                        quantity_map = {"uno": 1, "dos": 2, "tres": 3, "cuatro": 4, "cinco": 5}
                        quantity = quantity_map.get(keyword, 1)
                    
                    user_session['quantity'] = quantity
                    user_session['total'] = user_session['selected_product']['price'] * quantity
                    user_session['stage'] = 'confirming_purchase'
                    
                    return f"""✅ Perfecto! 

📦 Producto: {user_session['selected_product']['name']}
📊 Cantidad: {quantity} unidad(es)
💰 Total: ${user_session['total']:,}

¿Confirmas la compra? Escribe "sí" para proceder con el pago."""
                
                except (ValueError, KeyError):
                    pass
    
    # Check for purchase confirmation
    if user_session.get('stage') == 'confirming_purchase':
        if any(word in mensaje_lower for word in ["sí", "si", "confirmo", "comprar", "ok", "vale"]):
            # Create the order
            try:
                # Store total before clearing session
                total_amount = user_session['total']
                
                order_result = await create_real_order(
                    telefono,
                    user_session['selected_product']['name'],
                    user_session['quantity'],
                    user_session['total'],
                    client_info
                )
                
                clear_user_session(telefono)
                
                if order_result.get('status') == 'success':
                    return f"""🎉 ¡Compra confirmada!

📦 Orden: {order_result['order_number']}
💰 Total: ${total_amount:,}
🔗 Pagar aquí: {order_result['payment_link']}

¡Gracias por tu compra en {client_info['name']}! 🛍️"""
                else:
                    return f"❌ Error creando la orden: {order_result.get('message', 'Error desconocido')}"
                    
            except Exception as e:
                clear_user_session(telefono)
                return f"❌ Error procesando la compra: {str(e)}"
        elif any(word in mensaje_lower for word in ["no", "cancelar", "cancel"]):
            clear_user_session(telefono)
            return "❌ Compra cancelada. ¿En qué más puedo ayudarte?"

    # Try OpenAI for intelligent responses with real products
    try:
        if client_info.get("client_id"):
            # Search for products based on message keywords
            relevant_products = await get_client_products(
                client_info["client_id"], 
                search_term=mensaje, 
                limit=5
            )
            
            # If no specific products found, get general products
            if not relevant_products:
                relevant_products = await get_client_products(
                    client_info["client_id"], 
                    limit=5
                )
            
            ai_response = await process_with_openai(mensaje, client_info, relevant_products, user_session)
            
            # Check if AI response contains purchase confirmation format
            if ai_response and "COMPRA_CONFIRMADA|" in ai_response:
                parts = ai_response.split("COMPRA_CONFIRMADA|")[1].split("|")
                if len(parts) >= 4:
                    product_id, quantity, product_name, price = parts[0], parts[1], parts[2], parts[3]
                    
                    # Find the actual product
                    selected_product = None
                    for product in relevant_products:
                        if str(product['id']) == product_id or product['name'].lower() in product_name.lower():
                            selected_product = product
                            break
                    
                    if selected_product:
                        user_session['selected_product'] = selected_product
                        user_session['stage'] = 'selecting_quantity'
                        
                        return f"""🛍️ ¡Excelente elección!

📦 Producto: {selected_product['name']}
💰 Precio: ${selected_product['price']:,}

¿Cuántas unidades quieres? (1, 2, 3, etc.)"""
            
            if ai_response:
                return ai_response
                
    except Exception as e:
        print(f"Error in AI processing: {e}")

    # Fallback response con info específica del cliente
    return f"""🤖 {client_info['name']} - Asistente Virtual

📱 Recibí: "{mensaje}"

💡 Puedo ayudarte con:
• Búsqueda de productos
• Información de precios  
• Estado de pedidos
• Recomendaciones

🔥 Productos populares:
{await get_popular_products(client_info)}

¿En qué más te puedo ayudar?"""

async def get_popular_products(client_info: Dict[str, Any]) -> str:
    """Retorna productos populares desde la base de datos"""
    try:
        if client_info.get("client_id"):
            products = await get_client_products(client_info["client_id"], limit=3)
            if products:
                return "\n".join([f"• {p['name']}: ${p['price']:,}" for p in products])
    except Exception as e:
        print(f"Error getting popular products: {e}")
    
    # Fallback to static products
    fallback_products = {
        "cannabis": "• Vaporizadores PAX\n• Aceites CBD\n• Grinders premium",
        "electronics": "• iPhone 15 Pro\n• MacBook Air\n• AirPods Pro",
        "pets": "• Collares antipulgas\n• Alimento premium\n• Juguetes interactivos", 
        "clothing": "• Camisas casuales\n• Jeans premium\n• Zapatos deportivos"
    }
    return fallback_products.get(client_info.get('type'), "• Consulta nuestro catálogo\n• Ofertas especiales\n• Nuevos productos")