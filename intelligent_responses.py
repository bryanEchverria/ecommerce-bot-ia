import json
import openai

def usar_gpt_para_detectar_y_responder(mensaje, productos, tenant_info):
    """GPT detecta la intención y devuelve respuesta específica con productos reales"""
    try:
        client = openai.OpenAI()
        
        # Crear lista de productos para el contexto
        productos_context = []
        for prod in productos:
            precio = prod.get('sale_price', prod['price'])
            productos_context.append({
                'nombre': prod['name'],
                'precio': precio,
                'descripcion': prod.get('description', ''),
                'stock': prod.get('stock', 0)
            })
        
        productos_json = json.dumps(productos_context, ensure_ascii=False)
        
        prompt = f"""
        Eres un asistente inteligente de {tenant_info.get('name', 'la tienda')}.

        PRODUCTOS REALES DISPONIBLES:
        {productos_json}

        MENSAJE DEL CLIENTE: "{mensaje}"

        INSTRUCCIONES:
        - Si pregunta por una CATEGORÍA específica (flores, semillas, aceites, etc.), devuelve TODOS los productos de esa categoría con formato de lista
        - Si pide el CATÁLOGO completo, organiza por categorías
        - Si menciona un PRODUCTO específico, confirma si está disponible y muestra detalles
        - Si es un SALUDO, responde cordialmente
        - Si quiere COMPRAR algo, procesa la intención de compra

        RESPONDE EN FORMATO JSON:
        {{
            "intencion": "consulta_categoria|catalogo_completo|producto_especifico|compra|saludo|otro",
            "categoria": "flores|semillas|aceites|comestibles|accesorios|null",
            "producto_mencionado": "nombre exacto del producto o null",
            "cantidad": "número si menciona cantidad o null",
            "respuesta_tipo": "lista_detallada|respuesta_conversacional",
            "productos_mostrar": ["array con nombres de productos a mostrar o empty"]
        }}
        """
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=300
        )
        
        respuesta_raw = response.choices[0].message.content.strip()
        if respuesta_raw.startswith('```json'):
            respuesta_raw = respuesta_raw.replace('```json', '').replace('```', '').strip()
        
        return json.loads(respuesta_raw)
        
    except Exception as e:
        print(f"Error GPT detection: {e}")
        return {
            "intencion": "otro",
            "categoria": None,
            "producto_mencionado": None,
            "cantidad": None,
            "respuesta_tipo": "respuesta_conversacional",
            "productos_mostrar": []
        }

def generar_respuesta_especifica(deteccion, productos, tenant_info):
    """Genera respuesta específica basada en lo que GPT detectó"""
    
    if deteccion['intencion'] == 'consulta_categoria' and deteccion['categoria']:
        # Filtrar productos por categoría
        productos_categoria = []
        categoria = deteccion['categoria']
        
        for prod in productos:
            nombre_lower = prod['name'].lower()
            if categoria == 'flores' and any(word in nombre_lower for word in ['northern', 'kush', 'widow', 'flores']):
                productos_categoria.append(prod)
            elif categoria == 'semillas' and 'semilla' in nombre_lower:
                productos_categoria.append(prod)
            elif categoria == 'aceites' and ('aceite' in nombre_lower or 'cbd' in nombre_lower):
                productos_categoria.append(prod)
            elif categoria == 'comestibles' and 'brownie' in nombre_lower:
                productos_categoria.append(prod)
            elif categoria == 'accesorios' and any(word in nombre_lower for word in ['grinder', 'bong', 'papel', 'vaporizador']):
                productos_categoria.append(prod)
        
        if productos_categoria:
            respuesta = f"{categoria.title()} disponibles en {tenant_info.get('name', 'Green House')}:\n\n"
            for i, prod in enumerate(productos_categoria, 1):
                precio = prod.get('sale_price', prod['price'])
                respuesta += f"{i}. *{prod['name']}* - ${precio:,.0f}\n"
                respuesta += f"   {prod.get('description', '')}\n"
                respuesta += f"   Disponible\n\n"
            respuesta += "Para comprar: Escribe 'Quiero [nombre del producto]'\n"
            respuesta += "Ejemplo: 'Quiero Northern Lights'"
            return respuesta
        else:
            return f"No tenemos {categoria} disponibles en este momento."
    
    elif deteccion['intencion'] == 'catalogo_completo':
        # Mostrar catálogo organizado
        categorias = {}
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
                categorias[cat] = []
            categorias[cat].append(prod)
        
        respuesta = f"Estas son nuestras categorías disponibles en {tenant_info.get('name', 'Green House')}:\n\n"
        for i, categoria in enumerate(sorted(categorias.keys()), 1):
            respuesta += f"{i}. {categoria}\n"
        respuesta += "\n¿Qué tipo de producto te interesa?"
        return respuesta
    
    elif deteccion['intencion'] == 'saludo':
        return f"¡Hola! Soy tu asistente de ventas de {tenant_info.get('name', 'Green House')}. ¿En qué puedo ayudarte hoy?"
    
    else:
        # Respuesta conversacional por defecto
        return f"¿En qué puedo ayudarte en {tenant_info.get('name', 'Green House')}? Puedes preguntarme por nuestros productos o escribir 'ver catálogo'."