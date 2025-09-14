import json
import openai
from typing import Dict, List, Any

def detectar_intencion_con_gpt(mensaje: str, productos: list) -> Dict:
    """GPT detecta la intención específica del usuario"""
    try:
        client = openai.OpenAI()
        
        productos_nombres = [p['name'] for p in productos]
        
        prompt = f"""
        Analiza este mensaje del cliente y detecta exactamente qué quiere:

        PRODUCTOS DISPONIBLES: {', '.join(productos_nombres)}
        
        MENSAJE: "{mensaje}"
        
        Detecta la intención específica:
        - "consulta_producto": Pregunta por UN producto específico (ej: "tienes northern lights?")
        - "consulta_categoria": Pregunta por una categoría (ej: "que flores tienes")  
        - "consulta_catalogo": Quiere ver todo el catálogo
        - "intencion_compra": Quiere comprar algo específico (ej: "quiero aceite cbd")
        - "consulta_precios": Pregunta por precios
        - "consulta_stock": Pregunta por disponibilidad/stock
        - "saludo": Solo saluda
        - "otro": No está claro qué quiere

        RESPONDE SOLO EN JSON:
        {{
            "intencion": "una de las opciones arriba",
            "producto_mencionado": "nombre del producto si menciona uno específico, null si no",
            "categoria": "flores|semillas|aceites|comestibles|accesorios|null",
            "cantidad_mencionada": "número si menciona cantidad, null si no",
            "terminos_busqueda": ["palabras clave que usa para buscar"]
        }}
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
    
    for prod in productos:
        nombre_lower = prod['name'].lower()
        if categoria == 'flores' and any(word in nombre_lower for word in ['northern', 'kush', 'widow', 'flores']):
            productos_categoria.append(prod)
        elif categoria == 'semillas' and 'semilla' in nombre_lower:
            productos_categoria.append(prod)
        elif categoria == 'aceites' and ('aceite' in nombre_lower or 'cbd' in nombre_lower):
            productos_categoria.append(prod)
        elif categoria == 'comestibles' and any(word in nombre_lower for word in ['brownie', 'comestible']):
            productos_categoria.append(prod)
        elif categoria == 'accesorios' and any(word in nombre_lower for word in ['grinder', 'bong', 'papel', 'vaporizador']):
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
    
    # Categorizar y contar
    for prod in productos:
        nombre_lower = prod['name'].lower()
        if any(word in nombre_lower for word in ['northern', 'kush', 'widow']):
            cat = 'Flores'
        elif 'semilla' in nombre_lower:
            cat = 'Semillas'
        elif 'aceite' in nombre_lower or 'cbd' in nombre_lower:
            cat = 'Aceites y CBD'
        elif 'brownie' in nombre_lower:
            cat = 'Comestibles'
        else:
            cat = 'Accesorios'
        
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
    
    if deteccion['intencion'] == 'consulta_producto' and deteccion['producto_mencionado']:
        return ejecutar_consulta_producto(deteccion['producto_mencionado'], productos, tenant_info)
    
    elif deteccion['intencion'] == 'consulta_categoria' and deteccion['categoria']:
        return ejecutar_consulta_categoria(deteccion['categoria'], productos, tenant_info)
    
    elif deteccion['intencion'] == 'consulta_catalogo':
        return ejecutar_consulta_catalogo(productos, tenant_info)
    
    elif deteccion['intencion'] == 'intencion_compra':
        # Flujo de compra específico
        if deteccion['producto_mencionado']:
            producto_info = ejecutar_consulta_producto(deteccion['producto_mencionado'], productos, tenant_info)
            return f"{producto_info}\n\n🛒 **¿Confirmas que quieres comprarlo?**"
        else:
            return "¿Qué producto específico quieres comprar? Puedes escribir 'ver catálogo' para ver las opciones."
    
    elif deteccion['intencion'] == 'saludo':
        return f"¡Hola! Soy tu asistente de ventas de {tenant_info.get('name', 'Green House')}. ¿En qué puedo ayudarte hoy?"
    
    else:
        # Respuesta por defecto
        return f"¿En qué puedo ayudarte en {tenant_info.get('name', 'Green House')}? Puedes preguntarme por productos específicos o escribir 'ver catálogo'."