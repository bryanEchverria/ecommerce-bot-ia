import json
import openai
from typing import Dict, List, Any

def detectar_intencion_con_gpt(mensaje: str, productos: list, tenant_info: dict = None) -> Dict:
    """GPT detecta la intención específica del usuario"""
    try:
        client = openai.OpenAI()
        
        productos_nombres = [p['name'] for p in productos]
        
        # Extraer categorías dinámicamente de los productos reales
        categorias_encontradas = set()
        productos_detalle = []
        
        for prod in productos:
            # Usar la categoría real del producto o extraerla del nombre
            categoria = prod.get('category', 'general')
            if not categoria or categoria == '':
                categoria = 'general'
            
            categorias_encontradas.add(categoria)
            
            productos_detalle.append({
                "nombre": prod['name'],
                "categoria": categoria,
                "precio": prod.get('price', 0),
                "stock": prod.get('stock', 0),
                "descripcion": prod.get('description', '')[:100] + ('...' if len(prod.get('description', '')) > 100 else '')
            })
        
        # Crear lista de categorías dinámicas para el prompt
        categorias_dinamicas = '|'.join(sorted(categorias_encontradas)) if categorias_encontradas else 'general'
        
        # Información de la tienda (completamente dinámica)
        if tenant_info:
            nombre_tienda = tenant_info.get('name', 'Tienda')
            tipo_tienda = tenant_info.get('type', 'comercio')
        else:
            nombre_tienda = "Tienda"
            tipo_tienda = "comercio general"
        
        prompt = f"""
        Eres un asistente virtual multitienda. Atiendes a diferentes negocios, por lo que debes utilizar los parámetros {nombre_tienda} y {tipo_tienda} que te proporcionaré. También recibirás una lista de productos (nombre, categoría, precio, stock y descripción) que corresponde a la tienda actual. La lista de categorías disponibles para esta tienda es: {categorias_dinamicas}.

        PRODUCTOS DISPONIBLES:
        {json.dumps(productos_detalle, ensure_ascii=False, indent=2)}

        MENSAJE DEL CLIENTE: "{mensaje}"

        Tu tarea es analizar cada mensaje del cliente y devolver un objeto JSON que describa su intención, el producto solicitado (si coincide exactamente) y, si no existe coincidencia exacta, el producto más parecido de la lista. Sigue estas reglas:

        1. **Reconocer intenciones.** Determina si el cliente quiere:
           - Consultar un producto específico ("tienes X", "qué es X").
           - Consultar una categoría (por ejemplo, "qué [nombre de categoría] tienes", "ver catálogo").
           - Comprar ("quiero X", "lo/la quiero comprar", "quiero dos unidades de X").
        2. **Coincidencia de productos.**
           - Compara el nombre del producto mencionado con la lista de productos. Si coincide exactamente (ignorando mayúsculas/minúsculas), registra el nombre exacto en `producto_mencionado` y deja `producto_sugerido` como `null`.
           - Si no coincide, busca el nombre de producto más parecido según la lista suministrada (puedes basarte en la similitud de caracteres o palabras). Registra `null` en `producto_mencionado` y coloca el nombre más parecido en `producto_sugerido`.
        3. **Devolver siempre un JSON** con la siguiente estructura (y sin texto adicional):
        {{
          "intencion": "consulta_producto|consulta_categoria|consulta_catalogo|intencion_compra|saludo|otro",
          "producto_mencionado": "nombre exacto del producto si coincide, null si no",
          "producto_sugerido": "nombre del producto más parecido si no hay coincidencia exacta, null si no aplica",
          "categoria": "una de {categorias_dinamicas} si se consulta categoría, null si no aplica",
          "cantidad_mencionada": "entero si el cliente indica cantidad (por ejemplo '2'), null si no",
          "terminos_busqueda": ["lista de palabras clave que usa para buscar"],
          "respuesta_sugerida": "breve mensaje en español que siga las reglas de la tienda"
        }}
        4. **Consejos de respuesta.**
           - Si hay un `producto_sugerido` y `producto_mencionado` es null, la `respuesta_sugerida` debe preguntar al cliente si se refería al producto sugerido (por ejemplo: "¿Quizá te refieres a '<producto_sugerido>'? Responde 'sí' para confirmarlo o indícame otro producto.").
           - Si la intención es de compra y se reconoce el producto, la `respuesta_sugerida` debe pedir la cantidad deseada si no se indica o calcular el subtotal si sí se indica.
           - Mantén el tono amable y profesional, responde siempre en español y no inventes productos ni precios.

        Recuerda: no incluyas nada fuera de la estructura JSON. Usa exactamente los nombres de los productos de la lista suministrada, y no sugieras productos que no existan.
        """
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=150
        )
        
        respuesta_raw = response.choices[0].message.content.strip()
        if respuesta_raw.startswith('```json'):
            respuesta_raw = respuesta_raw.replace('```json', '').replace('```', '').strip()
        
        return json.loads(respuesta_raw)
        
    except Exception as e:
        print(f"Error detectando intención: {e}")
        return {
            "intencion": "otro",
            "producto_mencionado": None,
            "categoria": None,
            "cantidad_mencionada": None,
            "terminos_busqueda": []
        }

def ejecutar_consulta_producto(producto_buscado: str, productos: list, tenant_info: dict) -> str:
    """Query específica: busca un producto específico con stock, precio y disponibilidad"""
    productos_encontrados = []
    
    # Búsqueda flexible
    for prod in productos:
        if (producto_buscado.lower() in prod['name'].lower() or 
            any(term.lower() in prod['name'].lower() for term in producto_buscado.split())):
            productos_encontrados.append(prod)
    
    if not productos_encontrados:
        return f"❌ No tenemos '{producto_buscado}' disponible en {tenant_info.get('name', 'nuestra tienda')}.\n\n¿Te interesa ver nuestro catálogo completo?"
    
    # Mostrar detalles específicos de cada producto encontrado
    respuesta = f"Aquí está la información de '{producto_buscado}':\n\n"
    
    for prod in productos_encontrados:
        precio_actual = prod.get('sale_price', prod['price'])
        precio_original = prod['price']
        stock = prod.get('stock', 0)
        
        respuesta += f"📦 **{prod['name']}**\n"
        
        # Precio con descuento si aplica
        if prod.get('sale_price') and prod['sale_price'] < prod['price']:
            respuesta += f"💰 Precio: ~~${precio_original:,.0f}~~ **${precio_actual:,.0f}** (¡Oferta!)\n"
        else:
            respuesta += f"💰 Precio: **${precio_actual:,.0f}**\n"
        
        # Estado del stock
        if stock > 10:
            respuesta += f"✅ **Disponible** (Stock: {stock})\n"
        elif stock > 0:
            respuesta += f"⚠️ **Últimas unidades** (Quedan: {stock})\n"
        else:
            respuesta += f"❌ **Agotado**\n"
        
        respuesta += f"📝 {prod.get('description', '')}\n\n"
        
        if stock > 0:
            respuesta += f"🛒 Para comprar: Escribe 'Quiero {prod['name']}'\n\n"
    
    return respuesta

def ejecutar_consulta_categoria(categoria: str, productos: list, tenant_info: dict) -> str:
    """Query específica: obtiene todos los productos de una categoría con precios y stock"""
    productos_categoria = []
    
    # Usar categorías dinámicas reales de la base de datos
    for prod in productos:
        prod_categoria = prod.get('category', '').lower()
        if categoria.lower() == prod_categoria or categoria.lower() in prod_categoria.lower():
            productos_categoria.append(prod)
    
    if not productos_categoria:
        return f"❌ No tenemos productos de {categoria} disponibles en este momento."
    
    # Mostrar lista detallada con stock y precios reales
    respuesta = f"🏪 **{categoria.title()} en {tenant_info.get('name', 'Green House')}:**\n\n"
    
    productos_disponibles = 0
    productos_agotados = 0
    
    for i, prod in enumerate(productos_categoria, 1):
        precio_actual = prod.get('sale_price', prod['price'])
        precio_original = prod['price']
        stock = prod.get('stock', 0)
        
        respuesta += f"{i}. **{prod['name']}**\n"
        
        # Precio
        if prod.get('sale_price') and prod['sale_price'] < prod['price']:
            respuesta += f"   💰 ~~${precio_original:,.0f}~~ **${precio_actual:,.0f}** (¡Oferta!)\n"
        else:
            respuesta += f"   💰 **${precio_actual:,.0f}**\n"
        
        # Stock detallado
        if stock > 10:
            respuesta += f"   ✅ Disponible\n"
            productos_disponibles += 1
        elif stock > 0:
            respuesta += f"   ⚠️ Quedan {stock}\n"
            productos_disponibles += 1
        else:
            respuesta += f"   ❌ Agotado\n"
            productos_agotados += 1
        
        respuesta += f"   📝 {prod.get('description', '')[:50]}...\n\n"
    
    # Resumen
    respuesta += f"📊 **Resumen:** {productos_disponibles} disponibles, {productos_agotados} agotados\n\n"
    respuesta += f"🛒 **Para comprar:** Escribe 'Quiero [nombre del producto]'"
    
    return respuesta

def ejecutar_consulta_catalogo(productos: list, tenant_info: dict) -> str:
    """Query específica: organiza todo el catálogo por categorías con conteos"""
    categorias = {}
    total_productos = len(productos)
    productos_disponibles = sum(1 for p in productos if p.get('stock', 0) > 0)
    productos_ofertas = sum(1 for p in productos if p.get('sale_price') and p['sale_price'] < p['price'])
    
    # Categorizar usando categorías reales de la base de datos
    for prod in productos:
        # Usar la categoría real del producto
        cat = prod.get('category', 'General')
        if not cat or cat == '':
            cat = 'General'
        
        if cat not in categorias:
            categorias[cat] = {'productos': [], 'disponibles': 0, 'ofertas': 0}
        
        categorias[cat]['productos'].append(prod)
        if prod.get('stock', 0) > 0:
            categorias[cat]['disponibles'] += 1
        if prod.get('sale_price') and prod['sale_price'] < prod['price']:
            categorias[cat]['ofertas'] += 1
    
    respuesta = f"🌿 **Catálogo Completo - {tenant_info.get('name', 'Green House')}**\n\n"
    respuesta += f"📊 **Resumen General:**\n"
    respuesta += f"• Total productos: {total_productos}\n"
    respuesta += f"• Disponibles: {productos_disponibles}\n"
    respuesta += f"• En oferta: {productos_ofertas}\n\n"
    
    respuesta += f"📂 **Categorías disponibles:**\n\n"
    
    for i, (categoria, info) in enumerate(sorted(categorias.items()), 1):
        respuesta += f"{i}. **{categoria}** ({len(info['productos'])} productos)\n"
        respuesta += f"   ✅ {info['disponibles']} disponibles\n"
        if info['ofertas'] > 0:
            respuesta += f"   🏷️ {info['ofertas']} en oferta\n"
        respuesta += "\n"
    
    respuesta += f"🔍 **Para ver detalles:**\n"
    respuesta += f"Escribe el nombre de una categoría (ej: 'flores')\n\n"
    respuesta += f"🛒 **Para comprar directamente:**\n"
    respuesta += f"Escribe 'Quiero [producto]' (ej: 'Quiero Northern Lights')"
    
    return respuesta

def ejecutar_flujo_inteligente(deteccion: dict, productos: list, tenant_info: dict) -> str:
    """Ejecuta el flujo específico basado en la detección de GPT"""
    
    # Si GPT sugirió una respuesta específica para saludos, úsala
    if deteccion['intencion'] == 'saludo' and deteccion.get('respuesta_sugerida'):
        return deteccion['respuesta_sugerida']
    
    # Consulta de producto - manejar coincidencia exacta vs sugerencia
    elif deteccion['intencion'] == 'consulta_producto':
        if deteccion.get('producto_mencionado'):
            # Coincidencia exacta encontrada
            return ejecutar_consulta_producto(deteccion['producto_mencionado'], productos, tenant_info)
        elif deteccion.get('producto_sugerido'):
            # No hay coincidencia exacta, pero hay sugerencia
            if deteccion.get('respuesta_sugerida'):
                return deteccion['respuesta_sugerida']
            else:
                return f"¿Quizá te refieres a '{deteccion['producto_sugerido']}'? Responde 'sí' para confirmarlo o indícame otro producto."
        else:
            return "❌ No encontramos ese producto específico. ¿Podrías ser más específico o ver nuestro catálogo completo?"
    
    elif deteccion['intencion'] == 'consulta_categoria' and deteccion['categoria']:
        return ejecutar_consulta_categoria(deteccion['categoria'], productos, tenant_info)
    
    elif deteccion['intencion'] == 'consulta_catalogo':
        return ejecutar_consulta_catalogo(productos, tenant_info)
    
    elif deteccion['intencion'] == 'intencion_compra':
        # Flujo de compra específico - manejar producto exacto vs sugerido
        if deteccion.get('producto_mencionado'):
            # Producto encontrado exactamente
            if deteccion.get('respuesta_sugerida'):
                return deteccion['respuesta_sugerida']
            else:
                producto_info = ejecutar_consulta_producto(deteccion['producto_mencionado'], productos, tenant_info)
                return f"{producto_info}\n\n🛒 **¿Confirmas que quieres comprarlo?**"
        elif deteccion.get('producto_sugerido'):
            # Producto no exacto, pero hay sugerencia
            if deteccion.get('respuesta_sugerida'):
                return deteccion['respuesta_sugerida']
            else:
                return f"¿Quizá quieres comprar '{deteccion['producto_sugerido']}'? Responde 'sí' para ver los detalles y confirmar la compra."
        else:
            return "¿Qué producto específico quieres comprar? Puedes escribir 'ver catálogo' para ver las opciones."
    
    elif deteccion['intencion'] == 'saludo':
        return f"¡Hola! Soy tu asistente de ventas de {tenant_info.get('name', 'Green House')}. ¿En qué puedo ayudarte hoy?"
    
    else:
        # Usar respuesta sugerida por GPT si está disponible, sino usar por defecto
        if deteccion.get('respuesta_sugerida'):
            return deteccion['respuesta_sugerida']
        else:
            return f"¿En qué puedo ayudarte en {tenant_info.get('name', 'Green House')}? Puedes preguntarme por productos específicos o escribir 'ver catálogo'."