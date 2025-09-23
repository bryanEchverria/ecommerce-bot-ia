"""
🤖 SISTEMA DE BOT MULTI-TENANT DINÁMICO - REFACTORIZADO
Integra configuración personalizada 100% desde BD por tenant
🔒 SIN HARDCODING de ningún tenant específico  
🚀 Escalable automáticamente a cualquier nuevo tipo de negocio
"""
import json
import os
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
import openai
from services.tenant_config_manager import (
    get_cached_tenant_config,
    extract_dynamic_categories_from_products,
    get_dynamic_business_insights,
    format_currency,
    TenantConfig,
    ProductCategory
)

# Configuración OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

class DynamicTenantBot:
    """
    Bot completamente dinámico que se adapta automáticamente a cualquier tenant
    """
    
    def __init__(self, db: Session, tenant_id: str, productos: List[Dict]):
        self.db = db
        self.tenant_id = tenant_id
        self.productos = productos
        
        # Cargar configuración dinámica desde BD
        self.tenant_config = get_cached_tenant_config(db, tenant_id)
        self.categorias = extract_dynamic_categories_from_products(productos)
        self.business_insights = get_dynamic_business_insights(self.tenant_config, productos)
        
        print(f"🤖 Bot inicializado para {self.tenant_config.business_name} ({self.tenant_config.business_type})")
    
    def process_message_with_dynamic_ai(self, telefono: str, mensaje: str) -> str:
        """
        Procesa mensaje usando IA GPT con configuración 100% dinámica del tenant
        """
        # Validar contexto del mensaje
        if not self._validate_message_context(mensaje):
            return self._get_security_warning()
        
        # Construir contexto dinámico de productos
        productos_contexto = self._build_products_context()
        
        # Construir prompt personalizado completamente dinámico
        system_prompt = self._build_dynamic_system_prompt(productos_contexto)
        
        # Procesar con GPT usando configuración del tenant
        try:
            return self._call_gpt_with_tenant_config(system_prompt, mensaje)
        except Exception as e:
            print(f"❌ Error en GPT para {self.tenant_id}: {e}")
            return self._get_intelligent_fallback_response(mensaje)
    
    def _build_products_context(self) -> str:
        """
        Construye contexto de productos dinámico y optimizado
        """
        if not self.productos:
            return "\n\nACTUALMENTE NO HAY PRODUCTOS DISPONIBLES."
        
        productos_contexto = f"\n\nPRODUCTOS DISPONIBLES EN {self.tenant_config.business_name} ({len(self.productos)} productos):\n"
        
        # Mostrar productos más relevantes primero (con stock y ofertas)
        productos_ordenados = sorted(
            self.productos,
            key=lambda p: (
                p.get('stock', 0) > 0,  # Disponibles primero
                p.get('sale_price', 0) > 0,  # Ofertas después
                -float(p.get('price', 0))  # Precios más altos después
            ),
            reverse=True
        )
        
        # Limitar productos para no saturar el prompt (ajustable por configuración)
        max_productos = self._get_max_products_in_context()
        productos_mostrar = productos_ordenados[:max_productos]
        
        for i, producto in enumerate(productos_mostrar, 1):
            precio = float(producto.get('price', 0))
            sale_price = float(producto.get('sale_price', 0)) if producto.get('sale_price') else None
            precio_mostrar = sale_price if sale_price else precio
            stock = int(producto.get('stock', 0))
            
            # Formatear precio dinámicamente
            precio_formateado = format_currency(precio_mostrar, self.tenant_config.currency)
            
            productos_contexto += f"{i}. {producto.get('name', 'N/A')}"
            
            if precio_mostrar > 0:
                productos_contexto += f" - {precio_formateado}"
                
                # Indicar oferta si aplica
                if sale_price and sale_price < precio:
                    descuento = ((precio - sale_price) / precio) * 100
                    productos_contexto += f" (¡{descuento:.0f}% OFF!)"
            
            if stock > 0:
                if stock > 10:
                    productos_contexto += f" ✅ Disponible"
                else:
                    productos_contexto += f" ⚠️ Quedan {stock}"
            else:
                productos_contexto += f" ❌ Agotado"
                
            productos_contexto += f"\n"
        
        # Agregar resumen de categorías
        if self.categorias:
            categorias_texto = ", ".join([cat.name for cat in self.categorias])
            productos_contexto += f"\nCATEGORÍAS: {categorias_texto}\n"
        
        return productos_contexto
    
    def _build_dynamic_system_prompt(self, productos_contexto: str) -> str:
        """
        Construye prompt del sistema completamente dinámico basado en configuración del tenant
        """
        # Obtener prompt personalizado desde BD o usar default dinámico
        custom_prompt = self._get_tenant_system_prompt()
        
        # Información del negocio completamente dinámica
        business_info = f"""
INFORMACIÓN DEL NEGOCIO:
- Empresa: {self.tenant_config.business_name}
- Tipo de negocio: {self.tenant_config.business_type}
- Moneda: {self.tenant_config.currency}
- Idioma: {self.tenant_config.language}
- Total productos: {self.business_insights['total_products']}
- Productos disponibles: {self.business_insights['available_products']}
- Rango de precios: {self.business_insights['price_range']}
- Palabras clave principales: {', '.join(self.business_insights['top_keywords'])}"""
        
        # Configuración de estilo dinámica
        style_config = f"""
CONFIGURACIÓN DE ESTILO:
- Personalidad: {self.tenant_config.bot_personality}
- Usar emojis: {'Sí' if self.tenant_config.use_emojis else 'No'}
- Longitud de respuesta: {self.tenant_config.response_length}
- Estilo de saludo: {self.tenant_config.greeting_style}"""
        
        # Instrucciones dinámicas basadas en el tipo de negocio
        business_instructions = self._get_business_specific_instructions()
        
        return f"""{custom_prompt}

{business_info}

{productos_contexto}

{style_config}

{business_instructions}

INSTRUCCIONES CRÍTICAS:
1. SIEMPRE usa información REAL de productos de la lista de arriba
2. Menciona precios exactos en {self.tenant_config.currency} cuando sea relevante
3. Verifica stock disponible antes de recomendar productos
4. Respeta la personalidad y estilo configurado para {self.tenant_config.business_name}
5. Si preguntan por productos específicos, busca coincidencias en la lista
6. Adapta tu lenguaje al idioma: {self.tenant_config.language}
7. Usa el contexto del tipo de negocio: {self.tenant_config.business_type}

RESPONDE como el asistente especializado de {self.tenant_config.business_name}:"""
    
    def _get_tenant_system_prompt(self) -> str:
        """
        Obtiene prompt personalizado del tenant desde BD o genera uno dinámico
        """
        try:
            from models import TenantPrompts
            
            config = self.db.query(TenantPrompts).filter(
                TenantPrompts.tenant_id == self.tenant_id,
                TenantPrompts.is_active == True
            ).first()
            
            if config and config.system_prompt:
                return config.system_prompt
                
        except Exception as e:
            print(f"⚠️ No se pudo cargar prompt personalizado: {e}")
        
        # Generar prompt dinámico basado en tipo de negocio
        return self._generate_dynamic_default_prompt()
    
    def _generate_dynamic_default_prompt(self) -> str:
        """
        Genera prompt por defecto adaptado al tipo de negocio
        """
        business_type = self.tenant_config.business_type.lower()
        business_name = self.tenant_config.business_name
        
        # Templates por tipo de negocio
        if 'cannabis' in business_type or 'cbd' in business_type:
            return f"Eres un asistente especializado en productos de cannabis medicinal y recreativo para {business_name}. Proporciona información educativa, responsable y profesional sobre productos, efectos, dosificaciones y uso seguro."
        
        elif 'technology' in business_type or 'gaming' in business_type or 'tech' in business_type:
            return f"Eres un experto en tecnología para {business_name}. Ayuda a los clientes con especificaciones técnicas, compatibilidad, rendimiento y recomendaciones de productos tecnológicos."
        
        elif 'clothing' in business_type or 'fashion' in business_type or 'apparel' in business_type:
            return f"Eres un consultor de moda para {business_name}. Asiste con tallas, estilos, tendencias, combinaciones y cuidado de prendas."
        
        elif 'food' in business_type or 'restaurant' in business_type or 'delivery' in business_type:
            return f"Eres un asistente gastronómico para {business_name}. Ayuda con recomendaciones de comida, ingredientes, menús y pedidos."
        
        elif 'health' in business_type or 'pharmacy' in business_type or 'medical' in business_type:
            return f"Eres un asistente de salud para {business_name}. Proporciona información sobre productos de salud, bienestar y cuidado personal de manera responsable."
        
        else:  # General/desconocido
            return f"Eres un asistente de ventas profesional para {business_name}. Ayuda a los clientes con información de productos, precios, disponibilidad y recomendaciones personalizadas de manera amigable y eficiente."
    
    def _get_business_specific_instructions(self) -> str:
        """
        Genera instrucciones específicas basadas en el tipo de negocio
        """
        business_type = self.tenant_config.business_type.lower()
        
        if 'cannabis' in business_type:
            return """
INSTRUCCIONES ESPECÍFICAS PARA CANNABIS:
- Enfatiza el uso responsable y legal
- Menciona efectos y potencia cuando sea relevante
- Sugiere dosificaciones conservadoras para principiantes
- Incluye información sobre CBD vs THC si aplica"""
        
        elif 'technology' in business_type:
            return """
INSTRUCCIONES ESPECÍFICAS PARA TECNOLOGÍA:
- Menciona especificaciones técnicas relevantes
- Compara características entre productos similares
- Considera compatibilidad y requisitos del sistema
- Sugiere accesorios complementarios"""
        
        elif 'food' in business_type:
            return """
INSTRUCCIONES ESPECÍFICAS PARA COMIDA:
- Menciona ingredientes principales
- Considera alergias y restricciones dietéticas
- Sugiere combinaciones y acompañamientos
- Incluye información nutricional si está disponible"""
        
        else:
            return """
INSTRUCCIONES GENERALES:
- Adapta tu comunicación al tipo de producto
- Enfócate en beneficios y características únicas
- Sugiere productos complementarios cuando sea apropiado
- Personaliza según las necesidades expresadas por el cliente"""
    
    def _get_max_products_in_context(self) -> int:
        """
        Determina cuántos productos incluir en el contexto basado en configuración
        """
        response_length = self.tenant_config.response_length.lower()
        
        if response_length == 'short':
            return 8
        elif response_length == 'long':
            return 20
        else:  # medium
            return 12
    
    def _call_gpt_with_tenant_config(self, system_prompt: str, mensaje: str) -> str:
        """
        Llama a GPT usando la configuración específica del tenant
        """
        client = openai.OpenAI()
        
        print(f"🤖 Procesando con {self.tenant_config.ai_model} (temp: {self.tenant_config.ai_temperature}) para {self.tenant_id}")
        
        response = client.chat.completions.create(
            model=self.tenant_config.ai_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": mensaje}
            ],
            temperature=self.tenant_config.ai_temperature,
            max_tokens=self.tenant_config.max_tokens
        )
        
        respuesta = response.choices[0].message.content.strip()
        
        # Aplicar límites de longitud según configuración
        respuesta = self._apply_response_length_limits(respuesta)
        
        # Aplicar formateo según estilo del tenant
        respuesta = self._apply_tenant_formatting(respuesta)
        
        print(f"✅ Respuesta generada para {self.tenant_config.business_name}")
        return respuesta
    
    def _apply_response_length_limits(self, respuesta: str) -> str:
        """
        Aplica límites de longitud según configuración del tenant
        """
        response_length = self.tenant_config.response_length.lower()
        
        if response_length == 'short' and len(respuesta) > 300:
            return respuesta[:297] + "..."
        elif response_length == 'medium' and len(respuesta) > 600:
            return respuesta[:597] + "..."
        elif response_length == 'long' and len(respuesta) > 1200:
            return respuesta[:1197] + "..."
        
        return respuesta
    
    def _apply_tenant_formatting(self, respuesta: str) -> str:
        """
        Aplica formateo específico según configuración del tenant
        """
        # Remover emojis si están deshabilitados
        if not self.tenant_config.use_emojis:
            import re
            respuesta = re.sub(r'[^\w\s\.,\!\?\-\(\)\n]', '', respuesta)
        
        # Agregar firma del negocio si está configurado
        if len(respuesta) > 100:  # Solo para respuestas sustanciales
            respuesta += f"\n\n---\n{self.tenant_config.business_name}"
        
        return respuesta
    
    def _validate_message_context(self, mensaje: str) -> bool:
        """
        Valida que el mensaje sea apropiado para el contexto del tenant
        """
        forbidden_patterns = [
            "change tenant", "switch client", "admin", "config", "delete", 
            "sql", "database", "hack", f"tenant:{self.tenant_id}",
            "switch to", "cambiar a", "administrador"
        ]
        
        mensaje_lower = mensaje.lower()
        for pattern in forbidden_patterns:
            if pattern in mensaje_lower:
                print(f"⚠️ Mensaje bloqueado para {self.tenant_id}: contiene '{pattern}'")
                return False
        
        return True
    
    def _get_security_warning(self) -> str:
        """
        Mensaje de seguridad cuando se detecta actividad sospechosa
        """
        return f"⚠️ Lo siento, no puedo procesar ese tipo de solicitud. ¿En qué puedo ayudarte con nuestros productos en {self.tenant_config.business_name}?"
    
    def _get_intelligent_fallback_response(self, mensaje: str) -> str:
        """
        Respuesta de fallback inteligente usando información del tenant
        """
        if self.productos and any(keyword in mensaje.lower() for keyword in ['producto', 'price', 'precio', 'cost', 'costo']):
            productos_destacados = [p.get('name', 'N/A') for p in self.productos[:3] if p.get('stock', 0) > 0]
            productos_texto = ", ".join(productos_destacados)
            
            emoji = " 🌟" if self.tenant_config.use_emojis else ""
            return f"¡Hola! Soy el asistente de {self.tenant_config.business_name}{emoji}. Algunos productos destacados: {productos_texto}. ¿Te interesa alguno en particular?"
        
        emoji = " 🤖" if self.tenant_config.use_emojis else ""
        return f"¡Hola! Soy el asistente de {self.tenant_config.business_name}{emoji}. ¿En qué puedo ayudarte hoy?"
    
    def get_dynamic_greeting(self) -> str:
        """
        Genera saludo dinámico personalizado
        """
        from services.tenant_config_manager import get_dynamic_greeting_template
        return get_dynamic_greeting_template(self.tenant_config, self.categorias)

# Funciones públicas refactorizadas

def process_message_with_dynamic_ai_refactored(
    db: Session, 
    telefono: str, 
    mensaje: str, 
    tenant_id: str,
    productos: List[Dict]
) -> str:
    """
    Función principal para procesar mensajes de manera 100% dinámica
    """
    try:
        # Crear bot dinámico para el tenant
        bot = DynamicTenantBot(db, tenant_id, productos)
        
        # Procesar mensaje
        return bot.process_message_with_dynamic_ai(telefono, mensaje)
        
    except Exception as e:
        print(f"❌ Error en procesamiento dinámico para {tenant_id}: {e}")
        
        # Fallback seguro
        try:
            tenant_config = get_cached_tenant_config(db, tenant_id)
            return f"¡Hola! Soy el asistente de {tenant_config.business_name}. ¿En qué puedo ayudarte hoy?"
        except:
            return "¡Hola! ¿En qué puedo ayudarte hoy?"

def get_dynamic_greeting_with_products_refactored(
    tenant_id: str,
    productos: List[Dict],
    db: Session
) -> str:
    """
    Genera saludo dinámico con información de productos
    """
    try:
        bot = DynamicTenantBot(db, tenant_id, productos)
        return bot.get_dynamic_greeting()
    except Exception as e:
        print(f"❌ Error generando saludo dinámico: {e}")
        tenant_config = get_cached_tenant_config(db, tenant_id)
        return f"¡Hola! Bienvenido a {tenant_config.business_name}. ¿En qué puedo ayudarte?"

# Mantener compatibilidad con nombres antiguos (deprecated)
def get_tenant_bot_config(db: Session, tenant_id: str) -> Optional[Dict[str, Any]]:
    """
    DEPRECATED: Usar get_cached_tenant_config del tenant_config_manager
    """
    print("⚠️ DEPRECATED: Usar get_cached_tenant_config del tenant_config_manager")
    config = get_cached_tenant_config(db, tenant_id)
    if config:
        return {
            "system_prompt": config.bot_personality,
            "style_overrides": {
                "tono": config.bot_personality,
                "usar_emojis": config.use_emojis,
                "limite_respuesta_caracteres": 300 if config.response_length == 'short' else 600
            },
            "nlg_params": {
                "modelo": config.ai_model,
                "temperature_nlg": config.ai_temperature,
                "max_tokens_nlg": config.max_tokens
            }
        }
    return None