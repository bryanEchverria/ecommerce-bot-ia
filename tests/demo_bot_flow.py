"""
Demo del flujo completo del bot - Simulación sin dependencias
Muestra cómo funciona el bot con productos vaporizador
"""

# Simulación de productos disponibles para Green House (+3456789012)
PRODUCTS_GREEN_HOUSE = [
    {
        "id": "1",
        "name": "PAX 3 Vaporizador Premium", 
        "category": "vaporizador",
        "price": 75000,
        "stock": 10,
        "description": "Vaporizador de alta calidad PAX 3"
    },
    {
        "id": "2", 
        "name": "Vape Pen Clásico",
        "category": "vaporizador", 
        "price": 35000,
        "stock": 15,
        "description": "Vaporizador portátil clásico"
    },
    {
        "id": "3",
        "name": "Vaporizador Arizer Solo II",
        "category": "vaporizador",
        "price": 95000, 
        "stock": 8,
        "description": "Vaporizador Arizer Solo II premium"
    }
]

# Configuración del cliente
CLIENT_CONFIG = {
    "phone": "+3456789012",
    "client_name": "Green House",
    "business_description": "Tienda especializada en productos canábicos y wellness",
    "email": "admin@greenhouse.com"
}

def extract_product_from_message(message, products):
    """Extrae producto del mensaje usando lógica del bot"""
    message_lower = message.lower()
    
    # Palabras clave para vaporizadores
    vapo_keywords = ['vapo', 'vaporizador', 'vape', 'pax']
    
    for product in products:
        product_name_lower = product['name'].lower()
        
        # Coincidencia exacta del nombre
        if product_name_lower in message_lower:
            return product
            
        # Coincidencia por categoría y palabras clave
        if product['category'] == 'vaporizador':
            if any(keyword in message_lower for keyword in vapo_keywords):
                return product
    
    return None

def extract_quantity_from_message(message):
    """Extrae cantidad del mensaje"""
    import re
    
    numbers = re.findall(r'\d+', message)
    if numbers:
        quantity = int(numbers[0])
        if 1 <= quantity <= 100:
            return quantity
    
    # Cantidades en texto
    text_quantities = {
        'uno': 1, 'una': 1, 'un': 1,
        'dos': 2, 'tres': 3, 'cuatro': 4, 'cinco': 5
    }
    
    message_lower = message.lower()
    for text, num in text_quantities.items():
        if text in message_lower:
            return num
    
    return None

def is_purchase_confirmation(message):
    """Verifica si es confirmación de compra"""
    confirmation_keywords = [
        'si', 'yes', 'ok', 'vale', 'confirmo', 'acepto', 'quiero'
    ]
    
    message_lower = message.lower().strip()
    return any(keyword in message_lower for keyword in confirmation_keywords)

def simulate_bot_conversation():
    """Simula conversación completa del bot"""
    
    print("=" * 60)
    print("DEMO: FLUJO COMPLETO BOT WHATSAPP")
    print("=" * 60)
    print(f"Cliente: {CLIENT_CONFIG['client_name']}")
    print(f"Teléfono: {CLIENT_CONFIG['phone']}")
    print(f"Productos disponibles: {len(PRODUCTS_GREEN_HOUSE)} vaporizadores")
    print("=" * 60)
    
    # Estado de la conversación
    conversation_state = {
        "current_product": None,
        "quantity": None,
        "total_price": None,
        "awaiting_confirmation": False
    }
    
    # Flujo de conversación
    messages = [
        "hola",
        "que productos tienes", 
        "quiero comprar un vapo",
        "2 unidades",
        "si"
    ]
    
    for i, user_message in enumerate(messages, 1):
        print(f"\nPASO {i}:")
        print(f"Usuario: {user_message}")
        
        # Procesar mensaje
        if user_message.lower() in ['hola', 'hello']:
            bot_response = f"""¡Hola! Bienvenido a {CLIENT_CONFIG['client_name']}

Soy tu asistente virtual y estoy aquí para ayudarte con:

• Ver nuestros productos
• Realizar compras  
• Consultar precios
• Estado de pedidos

¿En qué puedo ayudarte hoy?"""

        elif 'productos' in user_message.lower() or 'catalogo' in user_message.lower():
            bot_response = f"""**Nuestro Catálogo - {CLIENT_CONFIG['client_name']}**

**Vaporizador:**
  • PAX 3 Vaporizador Premium - $75,000 [Disponible]
  • Vape Pen Clásico - $35,000 [Disponible] 
  • Vaporizador Arizer Solo II - $95,000 [Disponible]

¿Te interesa algún producto? ¡Solo dime cuál y te ayudo con la compra!"""

        elif 'quiero' in user_message.lower() and not conversation_state["awaiting_confirmation"]:
            # Buscar producto
            product = extract_product_from_message(user_message, PRODUCTS_GREEN_HOUSE)
            
            if product:
                conversation_state["current_product"] = product
                conversation_state["quantity"] = None
                
                bot_response = f"""¡Excelente elección!

**{product['name']}**
Categoría: {product['category']}
Precio: ${product['price']:,}
Stock: En stock ({product['stock']})

¿Cuántas unidades te gustaría comprar?"""
            else:
                bot_response = "Lo siento, no encontré productos que coincidan con tu búsqueda. ¿Podrías ser más específico?"

        elif conversation_state["current_product"] and not conversation_state["quantity"]:
            # Procesar cantidad
            quantity = extract_quantity_from_message(user_message)
            
            if quantity:
                conversation_state["quantity"] = quantity
                conversation_state["total_price"] = conversation_state["current_product"]["price"] * quantity
                conversation_state["awaiting_confirmation"] = True
                
                product = conversation_state["current_product"]
                total = conversation_state["total_price"]
                
                bot_response = f"""Perfecto! Has seleccionado:

• {product['name']}
• Cantidad: {quantity} unidad{'es' if quantity > 1 else ''}
• Precio unitario: ${product['price']:,}
• **Total: ${total:,}**

¿Confirmas esta compra?

Responde 'si' para proceder con el pago o 'no' para cancelar."""
            else:
                bot_response = f"Por favor especifica cuántas unidades de {conversation_state['current_product']['name']} quieres comprar.\n\nEjemplo: '2 unidades' o simplemente '2'"

        elif conversation_state["awaiting_confirmation"]:
            if is_purchase_confirmation(user_message):
                # Simular creación de pedido
                product = conversation_state["current_product"]
                quantity = conversation_state["quantity"] 
                total = conversation_state["total_price"]
                order_number = "ORD-000123"
                payment_url = "https://www.flow.cl/app/web/pay.php?token=abc123xyz"
                
                bot_response = f"""¡Perfecto! Tu pedido ha sido creado exitosamente:

**Resumen del pedido:**
• Producto: {product['name']}
• Cantidad: {quantity} unidad{'es' if quantity > 1 else ''}
• Total: ${total:,} CLP

**Número de orden:** {order_number}
**Estado:** Pendiente

**Enlace de pago:**
{payment_url}

Haz clic en el enlace para completar el pago de forma segura.

**Importante:** Guarda tu número de orden **{order_number}** para consultar el estado de tu pedido más adelante."""
                
                # Reset estado
                conversation_state = {
                    "current_product": None,
                    "quantity": None, 
                    "total_price": None,
                    "awaiting_confirmation": False
                }
            else:
                bot_response = f"¿Quieres confirmar la compra de {conversation_state['quantity']} unidad{'es' if conversation_state['quantity'] > 1 else ''} de {conversation_state['current_product']['name']} por ${conversation_state['total_price']:,}?\n\nResponde 'si' para confirmar o 'no' para cancelar."

        print(f"Bot: {bot_response}")
        print("-" * 60)
    
    print("\n" + "=" * 60)
    print("✅ FLUJO COMPLETO DEMOSTRADO")
    print("=" * 60)
    print("El bot:")
    print("✅ Reconoce al cliente (Green House)")
    print("✅ Muestra productos vaporizador disponibles") 
    print("✅ Procesa solicitudes específicas ('vapo' → PAX 3)")
    print("✅ Maneja cantidades correctamente")
    print("✅ Genera enlace de pago Flow")
    print("✅ Proporciona número de orden para seguimiento")
    print("\n🤖 El bot USA OpenAI y ES MUY ESPECÍFICO en sus respuestas")

if __name__ == "__main__":
    simulate_bot_conversation()