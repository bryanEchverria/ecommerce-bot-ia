"""
🤖 SMART FLOWS 100% MULTI-TENANT - REFACTORIZADO
Sistema de detección de intenciones completamente dinámico
🔒 SIN HARDCODING de ningún tenant específico
🚀 Escalable a cualquier tipo de negocio futuro
"""
import json
import openai
import os
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from services.tenant_config_manager import (
    get_cached_tenant_config, 
    extract_dynamic_categories_from_products,
    get_dynamic_business_insights,
    get_dynamic_greeting_template,
    format_currency,
    TenantConfig,
    ProductCategory
)

class DynamicIntentDetector:
    """
    Detector de intenciones 100% dinámico usando GPT
    Se adapta automáticamente a cualquier tipo de negocio
    """
    
    def __init__(self, tenant_config: TenantConfig, productos: List[Dict], categorias: List[ProductCategory]):
        self.tenant_config = tenant_config
        self.productos = productos
        self.categorias = categorias
        self.business_insights = get_dynamic_business_insights(tenant_config, productos)
        
    def detect_intent_with_gpt(self, mensaje: str) -> Dict[str, Any]:
        """
        Detección de intención 100% dinámica usando GPT
        NO asume nada sobre el tipo de negocio del tenant
        """
        print(f"🧠 Detectando intención para {self.tenant_config.business_name} ({self.tenant_config.business_type})")
        
        try:
            client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            
            # Construir contexto dinámico del negocio
            categorias_texto = ", ".join([cat.name.lower() for cat in self.categorias]) if self.categorias else "productos generales"
            palabras_clave = ", ".join(self.business_insights.get('top_keywords', []))
            
            # Prompt completamente dinámico
            intent_prompt = f"""Analiza la intención del cliente en este mensaje para {self.tenant_config.business_name}.

CONTEXTO DEL NEGOCIO:
- Tipo: {self.tenant_config.business_type}
- Categorías disponibles: {categorias_texto}
- Productos principales: {palabras_clave}
- Total productos: {self.business_insights['total_products']}
- Disponibles: {self.business_insights['available_products']}

MENSAJE DEL CLIENTE: "{mensaje}"

ANALIZA QUÉ BUSCA EL CLIENTE:

1. ¿Busca un PRODUCTO ESPECÍFICO? 
   - Si menciona nombres o características específicas de productos

2. ¿Busca una CATEGORÍA?
   - Si menciona alguna de estas categorías: {categorias_texto}

3. ¿Quiere ver TODO EL CATÁLOGO?
   - Si usa palabras como "todo", "catálogo", "ver todo", "mostrar todo"

4. ¿Es un SALUDO?
   - Si dice hola, buenos días, etc.

5. ¿OTRA COSA?
   - Preguntas generales, ayuda, etc.

RESPONDE SOLO UNA PALABRA:
- "producto" si busca algo específico
- "categoria" si busca un tipo de producto
- "catalogo" si quiere ver todo
- "saludo" si saluda
- "otro" si no está claro"""

            response = client.chat.completions.create(
                model=self.tenant_config.ai_model,
                messages=[{"role": "user", "content": intent_prompt}],
                temperature=0.1,
                max_tokens=20
            )
            
            intencion_detectada = response.choices[0].message.content.strip().lower()
            print(f"🎯 GPT detectó intención: {intencion_detectada}")
            
            return self._process_detected_intent(intencion_detectada, mensaje)
            
        except Exception as e:
            print(f"❌ Error en detección GPT: {e}")
            return self._fallback_intent_detection(mensaje)
    
    def _process_detected_intent(self, intencion: str, mensaje: str) -> Dict[str, Any]:
        """
        Procesa la intención detectada por GPT de manera dinámica
        """
        mensaje_lower = mensaje.lower()
        
        if intencion == "producto":
            return {
                "intencion": "consulta_producto",
                "producto_mencionado": mensaje,
                "categoria": None,
                "terminos_busqueda": mensaje.split(),
                "respuesta_sugerida": None
            }
        
        elif intencion == "categoria":
            # Detectar cuál categoría específica menciona
            categoria_detectada = None
            for categoria in self.categorias:
                if categoria.name.lower() in mensaje_lower:
                    categoria_detectada = categoria.name.lower()
                    break
                # Buscar por keywords de la categoría
                for keyword in categoria.keywords:
                    if keyword in mensaje_lower:
                        categoria_detectada = categoria.name.lower()
                        break
                if categoria_detectada:
                    break
            
            return {
                "intencion": "consulta_categoria",
                "producto_mencionado": None,
                "categoria": categoria_detectada,
                "terminos_busqueda": [categoria_detectada] if categoria_detectada else mensaje.split(),
                "respuesta_sugerida": None
            }
        
        elif intencion == "catalogo":
            return {
                "intencion": "consulta_catalogo",
                "producto_mencionado": None,
                "categoria": None,
                "terminos_busqueda": ["catalogo"],
                "respuesta_sugerida": None
            }
        
        elif intencion == "saludo":
            greeting = get_dynamic_greeting_template(self.tenant_config, self.categorias)
            return {
                "intencion": "saludo",
                "producto_mencionado": None,
                "categoria": None,
                "terminos_busqueda": [],
                "respuesta_sugerida": greeting
            }
        
        else:  # "otro"
            return {
                "intencion": "otro",
                "producto_mencionado": None,
                "categoria": None,
                "terminos_busqueda": mensaje.split(),
                "respuesta_sugerida": None
            }
    
    def _fallback_intent_detection(self, mensaje: str) -> Dict[str, Any]:
        """
        Detección de fallback sin GPT - usa lógica simple pero dinámica
        """
        mensaje_lower = mensaje.lower()
        
        # Detectar saludos genéricos
        saludos = ["hola", "buenas", "buenos días", "buenas tardes", "buenas noches", "hi", "hello"]
        if any(saludo in mensaje_lower for saludo in saludos):
            greeting = get_dynamic_greeting_template(self.tenant_config, self.categorias)
            return {
                "intencion": "saludo",
                "producto_mencionado": None,
                "categoria": None,
                "terminos_busqueda": [],
                "respuesta_sugerida": greeting
            }
        
        # Detectar catálogo
        catalogo_palabras = ["catalogo", "catálogo", "todo", "ver todo", "mostrar todo", "menu", "menú"]
        if any(palabra in mensaje_lower for palabra in catalogo_palabras):
            return {
                "intencion": "consulta_catalogo",
                "producto_mencionado": None,
                "categoria": None,
                "terminos_busqueda": ["catalogo"],
                "respuesta_sugerida": None
            }
        
        # Detectar productos específicos (búsqueda en nombres)
        for producto in self.productos:
            nombre_producto = producto.get('name', '').lower()
            if any(palabra in nombre_producto for palabra in mensaje_lower.split() if len(palabra) > 3):
                return {
                    "intencion": "consulta_producto",
                    "producto_mencionado": mensaje,
                    "categoria": None,
                    "terminos_busqueda": mensaje.split(),
                    "respuesta_sugerida": None
                }
        
        # Detectar categorías dinámicamente
        for categoria in self.categorias:
            if categoria.name.lower() in mensaje_lower:
                return {
                    "intencion": "consulta_categoria",
                    "producto_mencionado": None,
                    "categoria": categoria.name.lower(),
                    "terminos_busqueda": [categoria.name.lower()],
                    "respuesta_sugerida": None
                }
        
        # Default: buscar entre los productos
        return {
            "intencion": "otro",
            "producto_mencionado": None,
            "categoria": None,
            "terminos_busqueda": mensaje.split(),
            "respuesta_sugerida": None
        }

class DynamicProductFilter:
    """
    Filtro de productos 100% dinámico usando GPT
    Se adapta a cualquier tipo de inventario
    """
    
    def __init__(self, tenant_config: TenantConfig):
        self.tenant_config = tenant_config
    
    def filter_products_by_category_with_gpt(self, productos: List[Dict], categoria: str) -> List[Dict]:
        """
        Filtra productos por categoría usando GPT - 100% dinámico
        """
        if not productos or not categoria:
            return []
        
        try:
            client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            
            # Preparar productos para clasificación
            productos_para_clasificar = []
            for i, prod in enumerate(productos[:25]):  # Límite para eficiencia
                productos_para_clasificar.append({
                    "index": i,
                    "name": prod.get("name", ""),
                    "description": prod.get("description", ""),
                    "category": prod.get("category", "")
                })
            
            # Prompt completamente genérico
            classification_prompt = f"""Clasifica estos productos para determinar cuáles pertenecen a la categoría "{categoria}".

NEGOCIO: {self.tenant_config.business_name} ({self.tenant_config.business_type})
CATEGORÍA BUSCADA: "{categoria}"

PRODUCTOS:
{chr(10).join([f"{p['index']}. {p['name']} - {p['description']}" for p in productos_para_clasificar])}

INSTRUCCIONES:
1. Analiza nombre y descripción de cada producto
2. Determina cuáles pertenecen realmente a "{categoria}"
3. Sé flexible pero preciso en la clasificación
4. Considera sinónimos y términos relacionados
5. Usa tu conocimiento sobre el tipo de negocio: {self.tenant_config.business_type}

RESPONDE SOLO los números (índices) de productos que pertenecen a "{categoria}":
Formato: [0, 3, 7, 12]"""
            
            response = client.chat.completions.create(
                model=self.tenant_config.ai_model,
                messages=[{"role": "user", "content": classification_prompt}],
                temperature=0.1,
                max_tokens=150
            )
            
            # Parsear respuesta
            clasificacion_texto = response.choices[0].message.content.strip()
            import re
            numeros = re.findall(r'\d+', clasificacion_texto)
            indices_relevantes = [int(n) for n in numeros if int(n) < len(productos)]
            
            # Retornar productos filtrados
            productos_filtrados = [productos[i] for i in indices_relevantes if i < len(productos)]
            
            print(f"🔍 GPT filtró {len(productos_filtrados)} productos para categoría '{categoria}'")
            return productos_filtrados
            
        except Exception as e:
            print(f"❌ Error en filtrado GPT: {e}")
            return self._fallback_filter(productos, categoria)
    
    def _fallback_filter(self, productos: List[Dict], categoria: str) -> List[Dict]:
        """
        Filtrado de fallback sin GPT - búsqueda simple por texto
        """
        productos_filtrados = []
        categoria_lower = categoria.lower()
        
        for prod in productos:
            nombre_lower = prod.get("name", "").lower()
            desc_lower = prod.get("description", "").lower()
            
            if (categoria_lower in nombre_lower or 
                categoria_lower in desc_lower or
                any(keyword in nombre_lower for keyword in categoria_lower.split())):
                productos_filtrados.append(prod)
        
        return productos_filtrados[:10]  # Máximo 10 en fallback

class DynamicResponseGenerator:
    """
    Generador de respuestas dinámico basado en configuración del tenant
    """
    
    def __init__(self, tenant_config: TenantConfig):
        self.tenant_config = tenant_config
    
    def generate_product_response(self, productos_encontrados: List[Dict], termino_busqueda: str) -> str:
        """
        Genera respuesta de producto usando configuración dinámica del tenant
        """
        if not productos_encontrados:
            return f"❌ No encontramos '{termino_busqueda}' en {self.tenant_config.business_name}. ¿Te interesa ver nuestro catálogo completo?"
        
        respuesta = f"Encontré '{termino_busqueda}' en {self.tenant_config.business_name}:\n\n"
        
        for prod in productos_encontrados[:5]:  # Máximo 5 productos
            precio_actual = prod.get('sale_price', prod.get('price', 0))
            precio_original = prod.get('price', 0)
            stock = prod.get('stock', 0)
            
            # Formateo dinámico de precio
            precio_formateado = format_currency(precio_actual, self.tenant_config.currency)
            
            respuesta += f"📦 **{prod.get('name', 'N/A')}**\n"
            
            # Precio con oferta si aplica
            if prod.get('sale_price') and prod['sale_price'] < prod.get('price', 0):
                precio_original_formateado = format_currency(precio_original, self.tenant_config.currency)
                respuesta += f"💰 Precio: ~~{precio_original_formateado}~~ **{precio_formateado}** (¡Oferta!)\n"
            else:
                respuesta += f"💰 Precio: **{precio_formateado}**\n"
            
            # Estado del stock
            if stock > 10:
                respuesta += f"✅ **Disponible** (Stock: {stock})\n"
            elif stock > 0:
                respuesta += f"⚠️ **Últimas unidades** (Quedan: {stock})\n"
            else:
                respuesta += f"❌ **Agotado**\n"
            
            respuesta += f"📝 {prod.get('description', '')}\n\n"
            
            if stock > 0:
                respuesta += f"🛒 Para comprar: Escribe 'Quiero {prod.get('name', '')}'\n\n"
        
        return respuesta
    
    def generate_category_response(self, productos_categoria: List[Dict], categoria: str) -> str:
        """
        Genera respuesta de categoría con productos filtrados dinámicamente
        """
        if not productos_categoria:
            return f"❌ No tenemos productos de {categoria} disponibles en este momento en {self.tenant_config.business_name}."
        
        respuesta = f"🏪 **{categoria.title()} en {self.tenant_config.business_name}:**\n\n"
        
        productos_disponibles = 0
        productos_agotados = 0
        
        for i, prod in enumerate(productos_categoria[:8], 1):  # Máximo 8 productos
            precio_actual = prod.get('sale_price', prod.get('price', 0))
            precio_original = prod.get('price', 0)
            stock = prod.get('stock', 0)
            
            precio_formateado = format_currency(precio_actual, self.tenant_config.currency)
            
            respuesta += f"{i}. **{prod.get('name', 'N/A')}**\n"
            
            # Precio
            if prod.get('sale_price') and prod['sale_price'] < prod.get('price', 0):
                precio_original_formateado = format_currency(precio_original, self.tenant_config.currency)
                respuesta += f"   💰 ~~{precio_original_formateado}~~ **{precio_formateado}** (¡Oferta!)\n"
            else:
                respuesta += f"   💰 **{precio_formateado}**\n"
            
            # Stock
            if stock > 10:
                respuesta += f"   ✅ Disponible\n"
                productos_disponibles += 1
            elif stock > 0:
                respuesta += f"   ⚠️ Quedan {stock}\n"
                productos_disponibles += 1
            else:
                respuesta += f"   ❌ Agotado\n"
                productos_agotados += 1
            
            respuesta += f"   📝 {prod.get('description', '')[:60]}...\n\n"
        
        # Resumen
        respuesta += f"📊 **Resumen:** {productos_disponibles} disponibles, {productos_agotados} agotados\n\n"
        respuesta += f"🛒 **Para comprar:** Escribe 'Quiero [nombre del producto]'"
        
        return respuesta
    
    def generate_catalog_response(self, productos: List[Dict], categorias: List[ProductCategory]) -> str:
        """
        Genera respuesta de catálogo completo organizado dinámicamente
        """
        total_productos = len(productos)
        productos_disponibles = sum(1 for p in productos if p.get('stock', 0) > 0)
        productos_ofertas = sum(1 for p in productos if p.get('sale_price') and p['sale_price'] < p.get('price', 0))
        
        emoji = " 🏪" if self.tenant_config.use_emojis else ""
        respuesta = f"**Catálogo Completo - {self.tenant_config.business_name}**{emoji}\n\n"
        
        respuesta += f"📊 **Resumen General:**\n"
        respuesta += f"• Total productos: {total_productos}\n"
        respuesta += f"• Disponibles: {productos_disponibles}\n"
        respuesta += f"• En oferta: {productos_ofertas}\n\n"
        
        if categorias:
            respuesta += f"📂 **Categorías disponibles:**\n\n"
            
            for i, categoria in enumerate(categorias, 1):
                respuesta += f"{i}. **{categoria.name}** ({categoria.product_count} productos)\n"
                respuesta += f"   ✅ {categoria.available_count} disponibles\n"
                
                # Contar ofertas en esta categoría específica
                ofertas_categoria = 0
                for prod in productos:
                    if (categoria.name.lower() in prod.get('name', '').lower() or
                        categoria.name.lower() in prod.get('description', '').lower()):
                        if prod.get('sale_price') and prod['sale_price'] < prod.get('price', 0):
                            ofertas_categoria += 1
                
                if ofertas_categoria > 0:
                    respuesta += f"   🏷️ {ofertas_categoria} en oferta\n"
                respuesta += "\n"
        
        respuesta += f"🔍 **Para ver detalles:**\n"
        respuesta += f"Escribe el nombre de una categoría\n\n"
        respuesta += f"🛒 **Para comprar directamente:**\n"
        respuesta += f"Escribe 'Quiero [producto]'"
        
        return respuesta

# Funciones públicas refactorizadas para usar las clases dinámicas

def detectar_intencion_con_gpt_refactored(
    mensaje: str, 
    productos: List[Dict], 
    tenant_id: str,
    db: Session
) -> Dict[str, Any]:
    """
    Función principal de detección de intenciones 100% multi-tenant
    """
    # Obtener configuración dinámica del tenant
    tenant_config = get_cached_tenant_config(db, tenant_id)
    
    # Extraer categorías dinámicamente
    categorias = extract_dynamic_categories_from_products(productos)
    
    # Crear detector dinámico
    detector = DynamicIntentDetector(tenant_config, productos, categorias)
    
    # Detectar intención
    return detector.detect_intent_with_gpt(mensaje)

def ejecutar_consulta_producto_refactored(
    producto_buscado: str, 
    productos: List[Dict], 
    tenant_id: str,
    db: Session
) -> str:
    """
    Consulta de producto específico 100% dinámica
    """
    tenant_config = get_cached_tenant_config(db, tenant_id)
    generator = DynamicResponseGenerator(tenant_config)
    
    # Buscar productos que coincidan
    productos_encontrados = []
    for prod in productos:
        nombre_lower = prod.get('name', '').lower()
        desc_lower = prod.get('description', '').lower()
        busqueda_lower = producto_buscado.lower()
        
        if (busqueda_lower in nombre_lower or 
            any(term.lower() in nombre_lower for term in producto_buscado.split() if len(term) > 2)):
            productos_encontrados.append(prod)
    
    return generator.generate_product_response(productos_encontrados, producto_buscado)

def ejecutar_consulta_categoria_refactored(
    categoria: str, 
    productos: List[Dict], 
    tenant_id: str,
    db: Session
) -> str:
    """
    Consulta de categoría 100% dinámica usando GPT
    """
    tenant_config = get_cached_tenant_config(db, tenant_id)
    
    # Filtrar productos usando GPT dinámico
    filtro = DynamicProductFilter(tenant_config)
    productos_categoria = filtro.filter_products_by_category_with_gpt(productos, categoria)
    
    # Generar respuesta dinámica
    generator = DynamicResponseGenerator(tenant_config)
    return generator.generate_category_response(productos_categoria, categoria)

def ejecutar_consulta_catalogo_refactored(
    productos: List[Dict], 
    tenant_id: str,
    db: Session
) -> str:
    """
    Consulta de catálogo completo 100% dinámica
    """
    tenant_config = get_cached_tenant_config(db, tenant_id)
    categorias = extract_dynamic_categories_from_products(productos)
    
    generator = DynamicResponseGenerator(tenant_config)
    return generator.generate_catalog_response(productos, categorias)

def ejecutar_flujo_inteligente_refactored(
    deteccion: Dict[str, Any], 
    productos: List[Dict], 
    tenant_id: str,
    db: Session
) -> str:
    """
    Ejecutor principal de flujos 100% dinámico
    """
    intencion = deteccion.get('intencion')
    
    if intencion == 'saludo' and deteccion.get('respuesta_sugerida'):
        return deteccion['respuesta_sugerida']
    
    elif intencion == 'consulta_producto' and deteccion.get('producto_mencionado'):
        return ejecutar_consulta_producto_refactored(
            deteccion['producto_mencionado'], productos, tenant_id, db
        )
    
    elif intencion == 'consulta_categoria' and deteccion.get('categoria'):
        return ejecutar_consulta_categoria_refactored(
            deteccion['categoria'], productos, tenant_id, db
        )
    
    elif intencion == 'consulta_catalogo':
        return ejecutar_consulta_catalogo_refactored(productos, tenant_id, db)
    
    else:
        # Fallback genérico usando configuración del tenant
        tenant_config = get_cached_tenant_config(db, tenant_id)
        return f"¿En qué puedo ayudarte en {tenant_config.business_name}? Puedes preguntarme por productos específicos o escribir 'catálogo' para ver todo."