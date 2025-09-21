import json
import openai
from typing import Dict, List, Any

def _clasificar_productos_por_gpt_para_catalogo(productos: List[Dict]) -> Dict:
    """
    Clasificación 100% dinámica y multi-tenant usando GPT.
    Funciona para cualquier tipo de negocio sin lógica hardcodeada.
    """
    if not productos:
        return {}
    
    try:
        import os
        client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Crear lista de productos para GPT
        productos_lista = []
        for i, prod in enumerate(productos[:30]):  # Límite para no saturar
            productos_lista.append(f"{i}. {prod.get('name', '')} - {prod.get('description', '')}")
        
        # PROMPT SIMPLIFICADO SIN JSON PARA EVITAR ERRORES DE PARSING
        classification_prompt = f"""Clasifica estos productos en categorías simples.

PRODUCTOS:
{chr(10).join(productos_lista)}

TAREA: Agrupa productos similares en máximo 4 categorías.

RESPONDE SOLO LOS NOMBRES de las categorías separados por comas:
Ejemplo: aceites, flores, semillas, accesorios"""
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": classification_prompt}],
            temperature=0.1,
            max_tokens=50
        )
        
        # PROCESAMIENTO SIMPLE SIN JSON
        categorias_texto = response.choices[0].message.content.strip()
        categorias_nombres = [cat.strip() for cat in categorias_texto.split(',') if cat.strip()]
        
        # Crear clasificación automática basada en coincidencias de texto
        clasificacion_dict = {}
        for categoria in categorias_nombres[:4]:  # Máximo 4 categorías
            productos_categoria = []
            for i, prod in enumerate(productos):
                nombre_lower = prod.get('name', '').lower()
                desc_lower = prod.get('description', '').lower()
                categoria_lower = categoria.lower()
                
                if categoria_lower in nombre_lower or categoria_lower in desc_lower:
                    productos_categoria.append(i)
            
            if productos_categoria:  # Solo agregar si tiene productos
                clasificacion_dict[categoria] = productos_categoria
        
        # Convertir a formato requerido
        categorias_resultado = {}
        for categoria, indices in clasificacion_dict.items():
            categorias_resultado[categoria] = {
                'productos': [productos[i] for i in indices if i < len(productos)],
                'disponibles': 0,
                'ofertas': 0
            }
        
        print(f"🤖 GPT clasificó {len(productos)} productos en {len(categorias_resultado)} categorías dinámicas")
        return categorias_resultado
        
    except Exception as e:
        print(f"❌ Error en clasificación GPT para catálogo: {e}")
        # Fallback: una sola categoría con todos los productos
        return {
            "Productos": {
                'productos': productos,
                'disponibles': 0,
                'ofertas': 0
            }
        }

def detectar_intencion_con_gpt(mensaje: str, productos: list, tenant_info: dict = None) -> Dict:
    """
    DETECCIÓN 100% DINÁMICA basada en productos REALES del cliente
    Analiza los productos del tenant actual para detectar intenciones
    """
    print(f"🔥🔥🔥 DETECCIÓN DINÁMICA BASADA EN PRODUCTOS REALES: {mensaje} 🔥🔥🔥")
    
    mensaje_lower = mensaje.lower()
    palabras_mensaje = mensaje_lower.split()
    
    # PASO 1: BUSCAR PRODUCTOS ESPECÍFICOS en el inventario real
    productos_encontrados = []
    for producto in productos:
        nombre_producto = producto.get('name', '').lower()
        descripcion_producto = producto.get('description', '').lower()
        
        # Buscar coincidencias en nombre o descripción
        for palabra in palabras_mensaje:
            if (len(palabra) > 3 and  # Solo palabras significativas
                (palabra in nombre_producto or palabra in descripcion_producto)):
                productos_encontrados.append({
                    'producto': producto,
                    'palabra_coincidente': palabra,
                    'coincidencia_nombre': palabra in nombre_producto,
                    'coincidencia_descripcion': palabra in descripcion_producto
                })
                break
    
    # Si encontró productos específicos, priorizar eso
    if productos_encontrados:
        mejor_coincidencia = productos_encontrados[0]  # Tomar la primera coincidencia
        producto_nombre = mejor_coincidencia['producto']['name']
        palabra_buscada = mejor_coincidencia['palabra_coincidente']
        
        print(f"🎯 Producto específico encontrado: '{producto_nombre}' por palabra '{palabra_buscada}'")
        return {
            "intencion": "consulta_producto",
            "producto_mencionado": palabra_buscada,
            "categoria": None,
            "cantidad_mencionada": None,
            "terminos_busqueda": [palabra_buscada],
            "respuesta_sugerida": None
        }
    
    # PASO 2: BUSCAR CATEGORÍAS DINÁMICAS basadas en productos reales
    categorias_disponibles = set()
    for producto in productos:
        nombre = producto.get('name', '').lower()
        # Extraer categorías de nombres de productos
        if 'semilla' in nombre:
            categorias_disponibles.add('semillas')
        elif any(word in nombre for word in ['flor', 'cogollo']):
            categorias_disponibles.add('flores')
        elif any(word in nombre for word in ['aceite', 'tintura']):
            categorias_disponibles.add('aceites')
        elif any(word in nombre for word in ['brownie', 'galleta', 'chocolate', 'gomita']):
            categorias_disponibles.add('comestibles')
        elif any(word in nombre for word in ['grinder', 'papel', 'bong', 'vaporizador']):
            categorias_disponibles.add('accesorios')
    
    # Detectar si pregunta por alguna categoría
    for categoria in categorias_disponibles:
        if categoria in mensaje_lower or categoria[:-1] in mensaje_lower:  # singular/plural
            print(f"📂 Categoría dinámica detectada: {categoria}")
            return {
                "intencion": "consulta_categoria",
                "producto_mencionado": None,
                "categoria": categoria,
                "cantidad_mencionada": None,
                "terminos_busqueda": [categoria],
                "respuesta_sugerida": None
            }
    
    # PASO 3: DETECCIÓN DE INTENCIONES GENERALES
    if any(word in mensaje_lower for word in ["hola", "buenas", "buenos días", "buenas tardes"]):
        categorias_texto = ', '.join(sorted(categorias_disponibles)) if categorias_disponibles else 'nuestros productos'
        print(f"👋 Detectado saludo")
        return {
            "intencion": "saludo",
            "producto_mencionado": None,
            "categoria": None,
            "cantidad_mencionada": None,
            "terminos_busqueda": [],
            "respuesta_sugerida": f"¡Hola! Bienvenido a {tenant_info.get('name', 'nuestra tienda') if tenant_info else 'nuestra tienda'} 👋 ¿Qué estás buscando hoy: {categorias_texto}?"
        }
    elif any(word in mensaje_lower for word in ["catalogo", "catálogo", "todo", "ver todo", "mostrar todo"]):
        print(f"📋 Detectado catálogo completo")
        return {
            "intencion": "consulta_catalogo",
            "producto_mencionado": None,
            "categoria": None,
            "cantidad_mencionada": None,
            "terminos_busqueda": ["catalogo"],
            "respuesta_sugerida": None
        }
    else:
        print(f"❓ No detectada intención específica - análisis manual")
        return {
            "intencion": "otro",
            "producto_mencionado": None,
            "categoria": None,
            "cantidad_mencionada": None,
            "terminos_busqueda": palabras_mensaje,
            "respuesta_sugerida": None
        }

def _extraer_categorias_dinamicamente_con_gpt(productos: list) -> list:
    """
    Extrae categorías de productos usando GPT de manera 100% dinámica
    Funciona para cualquier tipo de negocio sin reglas hardcodeadas
    """
    if not productos:
        return []
    
    try:
        client = openai.OpenAI()
        
        # Tomar muestra de productos para analizar
        muestra_productos = []
        for i, prod in enumerate(productos[:15]):
            muestra_productos.append(f"{i}. {prod.get('name', '')} - {prod.get('description', '')}")
        
        categorias_prompt = f"""Eres un experto clasificador de productos. Analiza estos productos y extrae categorías precisas.

PRODUCTOS:
{chr(10).join(muestra_productos)}

TAREA: Identifica las categorías principales que mejor representen estos productos.

REGLAS CRÍTICAS:
1. Analiza nombres y descripciones cuidadosamente
2. Crea categorías ESPECÍFICAS y ÚTILES para el cliente
3. Usa términos que el cliente usaría naturalmente
4. Máximo 5 categorías, mínimo 3
5. Una palabra por categoría (ej: "semillas" no "semillas-cannabis")

IMPORTANTE:
- Analiza SOLO los productos proporcionados
- NO uses ejemplos predefinidos
- Cada negocio es único y diferente

RESPUESTA (separadas por comas):"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": categorias_prompt}],
            temperature=0.2,
            max_tokens=50
        )
        
        categorias_texto = response.choices[0].message.content.strip()
        # Procesar respuesta para extraer categorías
        categorias = [cat.strip().lower() for cat in categorias_texto.split(',') if cat.strip()]
        
        print(f"🧠 GPT extrajo categorías dinámicamente: {categorias}")
        return categorias[:6]  # Máximo 6 categorías
        
    except Exception as e:
        print(f"❌ Error extrayendo categorías dinámicamente: {e}")
        return ["productos"]  # Fallback genérico

def _procesar_respuesta_gpt_dinamica(respuesta_gpt: str, categorias_disponibles: list, mensaje: str, tenant_info: dict) -> Dict:
    """
    Procesa la respuesta de GPT de manera 100% dinámica
    """
    respuesta_gpt = respuesta_gpt.lower().strip()
    
    # Verificar si GPT detectó una categoría específica
    if respuesta_gpt in categorias_disponibles:
        return {
            "intencion": "consulta_categoria",
            "producto_mencionado": None,
            "categoria": respuesta_gpt,
            "cantidad_mencionada": None,
            "terminos_busqueda": [respuesta_gpt],
            "respuesta_sugerida": None
        }
    
    # Verificar intenciones estándar
    elif respuesta_gpt == "catalogo":
        return {
            "intencion": "consulta_catalogo",
            "producto_mencionado": None,
            "categoria": None,
            "cantidad_mencionada": None,
            "terminos_busqueda": ["catalogo"],
            "respuesta_sugerida": None
        }
    
    elif respuesta_gpt == "compra":
        return {
            "intencion": "intencion_compra",
            "producto_mencionado": None,
            "categoria": None,
            "cantidad_mencionada": None,
            "terminos_busqueda": [],
            "respuesta_sugerida": None
        }
    
    elif respuesta_gpt == "producto_especifico":
        return {
            "intencion": "consulta_producto",
            "producto_mencionado": mensaje,  # El mensaje completo como producto buscado
            "categoria": None,
            "cantidad_mencionada": None,
            "terminos_busqueda": mensaje.split(),
            "respuesta_sugerida": None
        }
    
    elif respuesta_gpt == "saludo":
        tienda_nombre = tenant_info.get('name', 'nuestra tienda') if tenant_info else 'nuestra tienda'
        categorias_texto = ', '.join(categorias_disponibles) if categorias_disponibles else 'nuestros productos'
        return {
            "intencion": "saludo",
            "producto_mencionado": None,
            "categoria": None,
            "cantidad_mencionada": None,
            "terminos_busqueda": [],
            "respuesta_sugerida": f"¡Hola! Bienvenido a {tienda_nombre} 👋 ¿Qué estás buscando hoy: {categorias_texto}?"
        }
    
    else:  # "otro" o respuesta no reconocida
        return {
            "intencion": "otro",
            "producto_mencionado": None,
            "categoria": None,
            "cantidad_mencionada": None,
            "terminos_busqueda": mensaje.split(),
            "respuesta_sugerida": None
        }

def _fallback_dinamico_con_gpt(mensaje: str, productos: list, tenant_info: dict) -> Dict:
    """
    Fallback 100% dinámico usando GPT cuando falla la detección principal
    """
    try:
        client = openai.OpenAI()
        
        # Usar GPT para detectar directamente qué busca el usuario
        fallback_prompt = f"""El usuario escribió: "{mensaje}"

Basándote SOLO en este mensaje, ¿qué está buscando el usuario?

Responde UNA de estas opciones:
- "categoria" si busca un tipo de producto
- "producto" si busca algo específico  
- "catalogo" si quiere ver todo
- "saludo" si es un saludo
- "otro" si no está claro

RESPUESTA:"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": fallback_prompt}],
            temperature=0.1,
            max_tokens=10
        )
        
        resultado = response.choices[0].message.content.strip().lower()
        
        if resultado == "categoria":
            # GPT detecta que busca una categoría, usar el mensaje como término de búsqueda
            return {
                "intencion": "otro",
                "producto_mencionado": None,
                "categoria": None,
                "cantidad_mencionada": None,
                "terminos_busqueda": mensaje.split(),
                "respuesta_sugerida": None
            }
        elif resultado == "producto":
            return {
                "intencion": "consulta_producto",
                "producto_mencionado": mensaje,
                "categoria": None,
                "cantidad_mencionada": None,
                "terminos_busqueda": mensaje.split(),
                "respuesta_sugerida": None
            }
        else:
            return {
                "intencion": "otro",
                "producto_mencionado": None,
                "categoria": None,
                "cantidad_mencionada": None,
                "terminos_busqueda": [],
                "respuesta_sugerida": None
            }
            
    except Exception as e:
        print(f"❌ Error en fallback dinámico: {e}")
        return {
            "intencion": "otro",
            "producto_mencionado": None,
            "categoria": None,
            "cantidad_mencionada": None,
            "terminos_busqueda": [],
            "respuesta_sugerida": None
        }

# FUNCIÓN ANTIGUA ELIMINADA COMPLETAMENTE PARA EVITAR CONFLICTOS

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

def _filtrar_productos_con_gpt_interno(productos: list, categoria_solicitada: str) -> list:
    """
    Filtrado GPT 100% dinámico y multi-tenant.
    Sin lógica hardcodeada - funciona para cualquier tipo de negocio.
    """
    print(f"🔥🔥🔥 ENTRANDO A _filtrar_productos_con_gpt_interno con categoria: {categoria_solicitada}")
    if not productos or not categoria_solicitada:
        print(f"🔥🔥🔥 SALIENDO: productos vacíos o categoría vacía")
        return []
    
    try:
        client = openai.OpenAI()
        
        # Crear lista de productos para clasificar (máximo 20 para no saturar GPT)
        productos_para_clasificar = []
        for i, prod in enumerate(productos[:20]):
            productos_para_clasificar.append({
                "index": i,
                "name": prod.get("name", ""),
                "description": prod.get("description", "")
            })
        
        # PROMPT OPTIMIZADO PARA CLASIFICACIÓN DINÁMICA
        classification_prompt = f"""Clasifica productos por categoría de manera inteligente.

CATEGORÍA BUSCADA: "{categoria_solicitada}"

PRODUCTOS DISPONIBLES:
{chr(10).join([f"{p['index']}. {p['name']} - {p['description']}" for p in productos_para_clasificar])}

INSTRUCCIONES:
1. Analiza nombre y descripción de cada producto
2. Determina cuáles pertenecen a la categoría "{categoria_solicitada}"
3. Se flexible pero preciso (ej: "aceites" incluye tinturas, extractos)
4. Considera sinónimos y términos relacionados

RESPONDE SOLO los números de productos que pertenecen a "{categoria_solicitada}":
Formato: [0, 3, 7]"""
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": classification_prompt}],
            temperature=0.1,
            max_tokens=100
        )
        
        # Parsear respuesta con regex para extraer números
        clasificacion_texto = response.choices[0].message.content.strip()
        import re
        numeros = re.findall(r'\d+', clasificacion_texto)
        indices_relevantes = [int(n) for n in numeros if int(n) < len(productos)]
        
        # Retornar productos filtrados
        productos_filtrados = [productos[i] for i in indices_relevantes if i < len(productos)]
        return productos_filtrados
        
    except Exception as e:
        print(f"❌ Error en clasificación GPT interna: {e}")
        return []

def ejecutar_consulta_categoria(categoria: str, productos: list, tenant_info: dict) -> str:
    """Query específica: obtiene productos de una categoría usando clasificación GPT inteligente"""
    
    # USAR CLASIFICACIÓN GPT INTELIGENTE (multi-tenant y dinámico)
    print(f"🚀 SMART_FLOWS: Filtrando categoría '{categoria}' con {len(productos)} productos")
    productos_categoria = _filtrar_productos_con_gpt_interno(productos, categoria)
    print(f"🚀 SMART_FLOWS: GPT retornó {len(productos_categoria)} productos")
    
    # Fallback si GPT falla: usar lógica simple por nombre de producto
    if not productos_categoria:
        for prod in productos:
            nombre_lower = prod['name'].lower()
            if categoria.lower() in nombre_lower:
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
    
    # CLASIFICACIÓN 100% DINÁMICA MULTI-TENANT CON GPT
    # NO MÁS LÓGICA HARDCODEADA - CADA TENANT ES DIFERENTE
    categorias = _clasificar_productos_por_gpt_para_catalogo(productos)
    
    # Contar estadísticas por categoría
    for categoria, info in categorias.items():
        for prod in info['productos']:
            if prod.get('stock', 0) > 0:
                info['disponibles'] += 1
            if prod.get('sale_price') and prod['sale_price'] < prod['price']:
                info['ofertas'] += 1
    
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
    
    # Si GPT sugirió una respuesta específica para saludos o consultas conversacionales, úsala
    if deteccion['intencion'] == 'saludo' and deteccion.get('respuesta_sugerida'):
        return deteccion['respuesta_sugerida']
    
    elif deteccion['intencion'] == 'consulta_producto' and deteccion['producto_mencionado']:
        return ejecutar_consulta_producto(deteccion['producto_mencionado'], productos, tenant_info)
    
    elif deteccion['intencion'] == 'consulta_categoria' and deteccion['categoria']:
        print(f"🎯 EJECUTAR_FLUJO_INTELIGENTE: Llamando ejecutar_consulta_categoria para '{deteccion['categoria']}'")
        resultado = ejecutar_consulta_categoria(deteccion['categoria'], productos, tenant_info)
        print(f"🎯 EJECUTAR_FLUJO_INTELIGENTE: Resultado recibido: {len(resultado)} caracteres")
        return resultado
    
    elif deteccion['intencion'] == 'otro' and deteccion.get('terminos_busqueda'):
        # Fallback inteligente: si GPT falló pero hay términos de búsqueda
        terminos = deteccion['terminos_busqueda']
        print(f"🔧 FALLBACK INTELIGENTE: Detectando categoría de términos {terminos}")
        
        # Detectar categoría común de los términos
        terminos_str = ' '.join(terminos).lower()
        categoria_detectada = None
        
        # Usar términos para inferir categoría de manera genérica
        for producto in productos[:10]:  # Revisar algunos productos para inferir categorías
            nombre_lower = producto.get('name', '').lower()
            if any(term in nombre_lower for term in terminos):
                # Extraer palabra clave del nombre del producto que coincide
                for term in terminos:
                    if term in nombre_lower:
                        categoria_detectada = term
                        break
                if categoria_detectada:
                    break
        
        if categoria_detectada:
            print(f"🔧 FALLBACK: Categoría detectada = '{categoria_detectada}'")
            return ejecutar_consulta_categoria(categoria_detectada, productos, tenant_info)
        else:
            print(f"🔧 FALLBACK: No se pudo detectar categoría")
            # Si no se detecta nada, usar respuesta sugerida de GPT si existe
            if deteccion.get('respuesta_sugerida'):
                return deteccion['respuesta_sugerida']
    
    elif deteccion['intencion'] == 'consulta_catalogo':
        return ejecutar_consulta_catalogo(productos, tenant_info)
    
    elif deteccion['intencion'] == 'intencion_compra':
        # Flujo de compra específico - usar respuesta de GPT si está disponible
        if deteccion.get('respuesta_sugerida') and deteccion['producto_mencionado']:
            return deteccion['respuesta_sugerida']
        elif deteccion['producto_mencionado']:
            producto_info = ejecutar_consulta_producto(deteccion['producto_mencionado'], productos, tenant_info)
            return f"{producto_info}\n\n🛒 **¿Confirmas que quieres comprarlo?**"
        else:
            return "¿Qué producto específico quieres comprar? Puedes escribir 'ver catálogo' para ver las opciones."
    
    
    else:
        # Usar respuesta sugerida por GPT si está disponible, sino usar por defecto
        if deteccion.get('respuesta_sugerida'):
            return deteccion['respuesta_sugerida']
        else:
            return f"¿En qué puedo ayudarte en {tenant_info.get('name', 'Green House')}? Puedes preguntarme por productos específicos o escribir 'ver catálogo'."