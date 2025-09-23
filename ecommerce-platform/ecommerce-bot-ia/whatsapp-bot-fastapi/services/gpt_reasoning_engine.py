"""
🧠 MOTOR DE RAZONAMIENTO GPT 100% DINÁMICO
Sistema donde GPT toma TODAS las decisiones sin condicionales hardcodeados
🔒 Multi-tenant puro - GPT razona según el contexto del negocio
🚀 Escalable automáticamente a cualquier tipo de negocio
"""
import json
import os
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
import openai
from services.tenant_config_manager import (
    get_cached_tenant_config,
    extract_dynamic_categories_from_products,
    get_dynamic_business_insights,
    format_currency,
    TenantConfig
)

# Configuración OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

class GPTReasoningEngine:
    """
    Motor de razonamiento donde GPT toma TODAS las decisiones
    Sin condicionales hardcodeados - GPT analiza y decide dinámicamente
    """
    
    def __init__(self, db: Session, tenant_id: str, productos: List[Dict]):
        self.db = db
        self.tenant_id = tenant_id
        self.productos = productos
        
        # Cargar contexto dinámico del tenant
        self.tenant_config = get_cached_tenant_config(db, tenant_id)
        self.categorias = extract_dynamic_categories_from_products(productos)
        self.business_insights = get_dynamic_business_insights(self.tenant_config, productos)
        
        print(f"🧠 GPT Reasoning Engine inicializado para {self.tenant_config.business_name}")
    
    def process_message_with_pure_gpt_reasoning(self, telefono: str, mensaje: str) -> str:
        """
        Procesamiento 100% con razonamiento GPT - SIN CONDICIONALES
        GPT decide qué hacer basándose en el contexto del negocio
        """
        # 1. GPT analiza el mensaje y decide qué acción tomar
        action_decision = self._ask_gpt_what_to_do(mensaje)
        
        # 2. GPT ejecuta la acción decidida
        response = self._ask_gpt_to_execute_action(action_decision, mensaje)
        
        # 3. GPT post-procesa la respuesta según el tenant
        final_response = self._ask_gpt_to_format_response(response)
        
        return final_response
    
    def _ask_gpt_what_to_do(self, mensaje: str) -> Dict[str, Any]:
        """
        GPT decide qué acción tomar basándose en el mensaje y contexto del negocio
        """
        try:
            client = openai.OpenAI()
            
            # Construir contexto completo del negocio para GPT
            business_context = self._build_complete_business_context()
            
            decision_prompt = f"""Eres el cerebro de decisiones para {self.tenant_config.business_name}.

{business_context}

MENSAJE DEL CLIENTE: "{mensaje}"

ANALIZA el mensaje y DECIDE qué hacer. Considera:
- El tipo de negocio ({self.tenant_config.business_type})
- Los productos disponibles
- Las categorías existentes
- El contexto del cliente

OPCIONES DE ACCIÓN DISPONIBLES:
1. "respuesta_directa" - Responder directamente usando GPT sin consultar productos específicos
2. "buscar_productos" - Buscar productos específicos que coincidan con la consulta
3. "mostrar_categoria" - Mostrar productos de una categoría específica
4. "mostrar_catalogo" - Mostrar el catálogo completo organizado
5. "consulta_compleja" - Manejar consultas que requieren análisis profundo de múltiples productos

PARA CADA ACCIÓN, TAMBIÉN DECIDE:
- Qué información específica necesitas
- Qué productos o categorías son relevantes
- Cómo debes estructurar la respuesta
- Qué tono usar según el negocio

RESPONDE EN JSON:
{{
    "accion_elegida": "una_de_las_opciones",
    "razonamiento": "por qué elegiste esta acción",
    "informacion_necesaria": ["que información específica necesitas"],
    "productos_relevantes": ["términos para buscar productos"],
    "categorias_relevantes": ["categorías a explorar"],
    "estructura_respuesta": "cómo estructurar la respuesta",
    "tono_requerido": "qué tono usar",
    "contexto_negocio": "consideraciones específicas del tipo de negocio"
}}"""

            response = client.chat.completions.create(
                model=self.tenant_config.ai_model,
                messages=[{"role": "user", "content": decision_prompt}],
                temperature=0.3,
                max_tokens=500
            )
            
            decision_text = response.choices[0].message.content.strip()
            decision_data = self._parse_gpt_json_safe(decision_text)
            
            print(f"🧠 GPT decidió acción: {decision_data.get('accion_elegida', 'unknown')}")
            return decision_data
            
        except Exception as e:
            print(f"❌ Error en decisión GPT: {e}")
            return {"accion_elegida": "respuesta_directa", "razonamiento": "fallback por error"}
    
    def _ask_gpt_to_execute_action(self, action_decision: Dict[str, Any], mensaje: str) -> str:
        """
        GPT ejecuta la acción decidida anteriormente
        """
        accion = action_decision.get('accion_elegida', 'respuesta_directa')
        
        # GPT decide cómo ejecutar la acción específica
        return self._delegate_action_to_gpt(accion, action_decision, mensaje)
    
    def _delegate_action_to_gpt(self, accion: str, action_decision: Dict, mensaje: str) -> str:
        """
        Delega la ejecución específica a GPT según la acción decidida
        """
        try:
            client = openai.OpenAI()
            
            # Preparar contexto específico para la acción
            execution_context = self._build_execution_context(accion, action_decision)
            
            execution_prompt = f"""Ejecuta la acción "{accion}" para {self.tenant_config.business_name}.

CONTEXTO DE EJECUCIÓN:
{execution_context}

DECISIÓN PREVIA:
- Acción: {accion}
- Razonamiento: {action_decision.get('razonamiento', '')}
- Información necesaria: {action_decision.get('informacion_necesaria', [])}
- Estructura deseada: {action_decision.get('estructura_respuesta', '')}
- Tono requerido: {action_decision.get('tono_requerido', '')}

MENSAJE ORIGINAL: "{mensaje}"

INSTRUCCIONES:
1. Ejecuta la acción decidida usando toda la información disponible
2. Usa SOLO productos reales de la lista proporcionada
3. Incluye precios exactos en {self.tenant_config.currency}
4. Verifica stock antes de recomendar
5. Adapta el tono al tipo de negocio: {self.tenant_config.business_type}
6. {'Usa emojis' if self.tenant_config.use_emojis else 'No uses emojis'}
7. Mantén la respuesta {self.tenant_config.response_length}

EJECUTA LA ACCIÓN Y GENERA LA RESPUESTA:"""

            response = client.chat.completions.create(
                model=self.tenant_config.ai_model,
                messages=[{"role": "user", "content": execution_prompt}],
                temperature=self.tenant_config.ai_temperature,
                max_tokens=self.tenant_config.max_tokens
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"❌ Error ejecutando acción {accion}: {e}")
            return self._get_safe_fallback_response(mensaje)
    
    def _build_complete_business_context(self) -> str:
        """
        Construye contexto completo del negocio para GPT
        """
        # Información del negocio
        business_info = f"""INFORMACIÓN DEL NEGOCIO:
- Empresa: {self.tenant_config.business_name}
- Tipo: {self.tenant_config.business_type}
- Moneda: {self.tenant_config.currency}
- Personalidad del bot: {self.tenant_config.bot_personality}
- Estilo de saludo: {self.tenant_config.greeting_style}"""

        # Estadísticas de productos
        stats_info = f"""ESTADÍSTICAS DE INVENTARIO:
- Total productos: {self.business_insights['total_products']}
- Productos disponibles: {self.business_insights['available_products']}
- Rango de precios: {self.business_insights['price_range']}
- Palabras clave del negocio: {', '.join(self.business_insights['top_keywords'][:5])}"""

        # Categorías disponibles
        if self.categorias:
            categorias_info = f"""CATEGORÍAS DISPONIBLES:
{chr(10).join([f"- {cat.name} ({cat.product_count} productos, {cat.available_count} disponibles)" for cat in self.categorias])}"""
        else:
            categorias_info = "CATEGORÍAS: No hay categorías específicas definidas"

        # Productos destacados (top por stock y precio)
        productos_destacados = sorted(
            self.productos, 
            key=lambda p: (p.get('stock', 0) > 0, -float(p.get('price', 0))), 
            reverse=True
        )[:10]
        
        productos_info = f"""PRODUCTOS DESTACADOS (top 10):
{chr(10).join([f"- {p.get('name', 'N/A')} - {format_currency(float(p.get('price', 0)), self.tenant_config.currency)} (Stock: {p.get('stock', 0)})" for p in productos_destacados])}"""

        return f"{business_info}\n\n{stats_info}\n\n{categorias_info}\n\n{productos_info}"
    
    def _build_execution_context(self, accion: str, action_decision: Dict) -> str:
        """
        Construye contexto específico para ejecutar la acción
        """
        # Información relevante según lo que GPT decidió que necesita
        productos_relevantes = action_decision.get('productos_relevantes', [])
        categorias_relevantes = action_decision.get('categorias_relevantes', [])
        
        context = f"ACCIÓN A EJECUTAR: {accion}\n\n"
        
        # Si GPT pidió productos específicos, buscarlos
        if productos_relevantes:
            productos_encontrados = self._find_products_by_terms(productos_relevantes)
            if productos_encontrados:
                context += f"PRODUCTOS ENCONTRADOS PARA LOS TÉRMINOS {productos_relevantes}:\n"
                for prod in productos_encontrados[:15]:
                    precio = format_currency(float(prod.get('price', 0)), self.tenant_config.currency)
                    context += f"- {prod.get('name', 'N/A')} - {precio} (Stock: {prod.get('stock', 0)}) - {prod.get('description', '')}\n"
                context += "\n"
        
        # Si GPT pidió categorías específicas, mostrarlas
        if categorias_relevantes:
            context += f"CATEGORÍAS SOLICITADAS: {', '.join(categorias_relevantes)}\n"
            for categoria_nombre in categorias_relevantes:
                productos_categoria = self._find_products_by_category(categoria_nombre)
                if productos_categoria:
                    context += f"\nPRODUCTOS EN {categoria_nombre.upper()}:\n"
                    for prod in productos_categoria[:8]:
                        precio = format_currency(float(prod.get('price', 0)), self.tenant_config.currency)
                        context += f"- {prod.get('name', 'N/A')} - {precio} (Stock: {prod.get('stock', 0)})\n"
            context += "\n"
        
        # Si no hay productos específicos, incluir todos para que GPT decida
        if not productos_relevantes and not categorias_relevantes:
            context += f"TODOS LOS PRODUCTOS DISPONIBLES ({len(self.productos)} total):\n"
            for prod in self.productos[:20]:  # Limitar para no saturar
                precio = format_currency(float(prod.get('price', 0)), self.tenant_config.currency)
                context += f"- {prod.get('name', 'N/A')} - {precio} (Stock: {prod.get('stock', 0)}) - {prod.get('description', '')[:50]}...\n"
            
            if len(self.productos) > 20:
                context += f"... y {len(self.productos) - 20} productos más.\n"
        
        return context
    
    def _find_products_by_terms(self, terminos: List[str]) -> List[Dict]:
        """
        Encuentra productos usando los términos que GPT consideró relevantes
        """
        productos_encontrados = []
        
        for producto in self.productos:
            nombre_lower = producto.get('name', '').lower()
            desc_lower = producto.get('description', '').lower()
            
            for termino in terminos:
                termino_lower = str(termino).lower()
                if (termino_lower in nombre_lower or 
                    termino_lower in desc_lower or
                    any(keyword in nombre_lower for keyword in termino_lower.split())):
                    productos_encontrados.append(producto)
                    break
        
        return productos_encontrados
    
    def _find_products_by_category(self, categoria: str) -> List[Dict]:
        """
        Encuentra productos por categoría usando matching flexible
        """
        productos_categoria = []
        categoria_lower = categoria.lower()
        
        for producto in self.productos:
            nombre_lower = producto.get('name', '').lower()
            desc_lower = producto.get('description', '').lower()
            
            if (categoria_lower in nombre_lower or 
                categoria_lower in desc_lower):
                productos_categoria.append(producto)
        
        return productos_categoria
    
    def _ask_gpt_to_format_response(self, response: str) -> str:
        """
        GPT formatea la respuesta final según las preferencias del tenant
        """
        try:
            client = openai.OpenAI()
            
            format_prompt = f"""Formatea esta respuesta para {self.tenant_config.business_name}.

RESPUESTA ACTUAL:
{response}

CONFIGURACIÓN DEL TENANT:
- Negocio: {self.tenant_config.business_name} ({self.tenant_config.business_type})
- Personalidad: {self.tenant_config.bot_personality}
- Usar emojis: {'Sí' if self.tenant_config.use_emojis else 'No'}
- Longitud: {self.tenant_config.response_length}
- Estilo de saludo: {self.tenant_config.greeting_style}

INSTRUCCIONES DE FORMATO:
1. Adapta el tono según la personalidad configurada
2. {'Incluye emojis apropiados' if self.tenant_config.use_emojis else 'Elimina todos los emojis'}
3. Ajusta la longitud según: {self.tenant_config.response_length}
4. Mantén toda la información técnica (precios, stock, nombres)
5. Asegúrate de que suene natural para el tipo de negocio
6. Si es necesario, agrega un cierre apropiado para {self.tenant_config.business_name}

GENERA LA RESPUESTA FORMATEADA:"""

            format_response = client.chat.completions.create(
                model="gpt-4o-mini",  # Usar modelo rápido para formateo
                messages=[{"role": "user", "content": format_prompt}],
                temperature=0.3,
                max_tokens=600
            )
            
            formatted_response = format_response.choices[0].message.content.strip()
            
            # Aplicar límites de longitud finales
            return self._apply_final_length_limits(formatted_response)
            
        except Exception as e:
            print(f"❌ Error formateando respuesta: {e}")
            return self._apply_final_length_limits(response)
    
    def _apply_final_length_limits(self, response: str) -> str:
        """
        Aplica límites finales de longitud según configuración
        """
        max_length = {
            'short': 400,
            'medium': 800,
            'long': 1500
        }.get(self.tenant_config.response_length.lower(), 800)
        
        if len(response) > max_length:
            return response[:max_length-3] + "..."
        
        return response
    
    def _parse_gpt_json_safe(self, json_text: str) -> Dict[str, Any]:
        """
        Parsea JSON de GPT con fallback seguro
        """
        try:
            # Limpiar formato markdown si existe
            if json_text.startswith('```json'):
                json_text = json_text[7:]
            if json_text.endswith('```'):
                json_text = json_text[:-3]
            
            return json.loads(json_text.strip())
        except json.JSONDecodeError as e:
            print(f"⚠️ Error parsing JSON de GPT: {e}")
            # Fallback básico
            return {
                "accion_elegida": "respuesta_directa",
                "razonamiento": "fallback por error de parsing",
                "informacion_necesaria": [],
                "productos_relevantes": [],
                "categorias_relevantes": [],
                "estructura_respuesta": "respuesta libre",
                "tono_requerido": self.tenant_config.bot_personality
            }
    
    def _get_safe_fallback_response(self, mensaje: str) -> str:
        """
        Respuesta de fallback completamente segura
        """
        emoji = " 🤖" if self.tenant_config.use_emojis else ""
        return f"¡Hola! Soy el asistente de {self.tenant_config.business_name}{emoji}. ¿En qué puedo ayudarte hoy?"

# Función pública principal

def process_message_with_pure_gpt_reasoning(
    db: Session,
    telefono: str,
    mensaje: str,
    tenant_id: str,
    productos: List[Dict]
) -> str:
    """
    Procesamiento 100% con razonamiento GPT
    SIN CONDICIONALES - GPT toma todas las decisiones
    """
    try:
        # Crear motor de razonamiento
        reasoning_engine = GPTReasoningEngine(db, tenant_id, productos)
        
        # Procesar con razonamiento puro
        return reasoning_engine.process_message_with_pure_gpt_reasoning(telefono, mensaje)
        
    except Exception as e:
        print(f"❌ Error en razonamiento GPT para {tenant_id}: {e}")
        
        # Fallback final usando configuración mínima
        try:
            tenant_config = get_cached_tenant_config(db, tenant_id)
            emoji = " 🤖" if tenant_config.use_emojis else ""
            return f"¡Hola! Soy el asistente de {tenant_config.business_name}{emoji}. ¿En qué puedo ayudarte?"
        except:
            return "¡Hola! ¿En qué puedo ayudarte hoy?"

# Función adicional para testing y análisis

def analyze_gpt_decision_process(
    db: Session,
    tenant_id: str,
    mensaje: str,
    productos: List[Dict]
) -> Dict[str, Any]:
    """
    Analiza el proceso de decisión de GPT para debugging
    """
    try:
        reasoning_engine = GPTReasoningEngine(db, tenant_id, productos)
        
        # Solo hacer el análisis de decisión
        decision = reasoning_engine._ask_gpt_what_to_do(mensaje)
        
        return {
            "tenant_id": tenant_id,
            "mensaje": mensaje,
            "decision_gpt": decision,
            "business_type": reasoning_engine.tenant_config.business_type,
            "products_count": len(productos),
            "categories_count": len(reasoning_engine.categorias)
        }
        
    except Exception as e:
        return {"error": str(e), "tenant_id": tenant_id}