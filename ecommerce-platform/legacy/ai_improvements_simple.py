"""
🤖 SISTEMA AVANZADO DE IA - VERSIÓN SIMPLIFICADA
Sistema de entrenamiento, análisis y mejora continua del bot (sin errores SQL)
"""
import json
import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

class ConversationAnalyzer:
    """Analiza conversaciones para detectar patrones y mejorar respuestas"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def log_conversation(
        self, 
        telefono: str, 
        tenant_id: str, 
        mensaje_usuario: str, 
        respuesta_bot: str, 
        intencion_detectada: Optional[str] = None,
        productos_mencionados: Optional[List[str]] = None,
        contexto_sesion: Optional[Dict] = None,
        duracion_ms: Optional[int] = None
    ):
        """Registra una conversación completa para análisis posterior (simplificado)"""
        try:
            # Por ahora solo loggeamos en consola hasta que las tablas estén bien configuradas
            print(f"📊 CONVERSATION LOG:")
            print(f"   👤 Usuario: {telefono} (tenant: {tenant_id})")
            print(f"   💬 Mensaje: '{mensaje_usuario}'")
            print(f"   🎯 Intención: {intencion_detectada}")
            print(f"   ⏱️  Tiempo: {duracion_ms}ms")
            return "logged_to_console"
            
        except Exception as e:
            print(f"Error logging conversation: {e}")
            return None
    
    def get_conversation_context(self, telefono: str, tenant_id: str) -> Dict:
        """Obtiene contexto básico (simplificado sin BD por ahora)"""
        # Contexto básico hasta que se arreglen las tablas
        return {
            "primera_interaccion": True,  # Asumir siempre primera vez por ahora
            "productos_consultados": [],
            "intenciones_frecuentes": [],
            "usuario_tipo": "nuevo_usuario"
        }

class AdvancedIntentDetector:
    """Detector de intenciones mejorado con contexto"""
    
    def __init__(self, db: Session):
        self.db = db
        self.analyzer = ConversationAnalyzer(db)
    
    def detect_intent_with_context(
        self, 
        mensaje: str, 
        telefono: str, 
        tenant_id: str, 
        productos: List[Dict]
    ) -> Dict:
        """Detección de intención mejorada con contexto histórico"""
        
        # Obtener contexto de conversaciones previas
        context = self.analyzer.get_conversation_context(telefono, tenant_id)
        
        # Prompt mejorado con contexto
        prompt = self._build_enhanced_prompt(mensaje, context, productos)
        
        try:
            from openai import OpenAI
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=400
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Agregar información contextual al resultado
            result["contexto_aplicado"] = {
                "es_cliente_recurrente": not context.get("primera_interaccion", True),
                "productos_previos": context.get("productos_consultados", []),
                "patron_comportamiento": context.get("usuario_tipo", "nuevo_usuario")
            }
            
            return result
            
        except Exception as e:
            print(f"Error in enhanced intent detection: {e}")
            # Fallback a detección básica
            return self._basic_intent_detection(mensaje, productos)
    
    def _build_enhanced_prompt(
        self, 
        mensaje: str, 
        context: Dict, 
        productos: List[Dict]
    ) -> str:
        """Construye un prompt enriquecido con contexto e historial"""
        
        context_info = ""
        if not context.get("primera_interaccion", True):
            context_info = f"""
CONTEXTO DE USUARIO:
- Cliente recurrente: Sí
- Productos consultados anteriormente: {', '.join(context.get('productos_consultados', []))}
- Tipo de usuario: {context.get('usuario_tipo', 'desconocido')}
"""
        
        productos_disponibles = "\n".join([
            f"- {prod['name']} (${prod['price']:,.0f}, Stock: {prod['stock']})"
            for prod in productos[:10]  # Primeros 10 productos
        ])
        
        return f"""
Eres un asistente de ventas inteligente. Analiza el mensaje del usuario y detecta su intención específica.

{context_info}

PRODUCTOS DISPONIBLES:
{productos_disponibles}

MENSAJE DEL USUARIO: "{mensaje}"

RESPONDE EN JSON con esta estructura:
{{
    "intencion": "consulta_producto|consulta_categoria|consulta_catalogo|intencion_compra|saludo|consulta_general|queja|despedida",
    "confianza": 0.95,
    "producto_mencionado": "nombre exacto del producto si aplica",
    "categoria_mencionada": "categoria si aplica",
    "contexto_detectado": "resumen de lo que entendiste",
    "sugerencia_respuesta": "tipo de respuesta recomendada",
    "urgencia": "alta|media|baja",
    "sentimiento": "positivo|neutral|negativo"
}}

REGLAS IMPORTANTES:
1. Si es un saludo simple como "hola", NO muestres el catálogo completo
2. Solo responde con información específica que el usuario pidió
3. Si menciona un producto específico, enfócate solo en ese producto
4. Para saludos, responde con saludo amigable y pregunta qué necesita
"""
    
    def _basic_intent_detection(self, mensaje: str, productos: List[Dict]) -> Dict:
        """Detección básica como fallback"""
        mensaje_lower = mensaje.lower()
        
        # Detección simple por palabras clave
        if any(word in mensaje_lower for word in ["hola", "buenos", "buenas", "hi"]):
            return {
                "intencion": "saludo", 
                "confianza": 0.9,
                "sugerencia_respuesta": "saludo_amigable_sin_catalogo"
            }
        elif any(word in mensaje_lower for word in ["quiero", "comprar", "necesito"]):
            return {"intencion": "intencion_compra", "confianza": 0.7}
        elif any(word in mensaje_lower for word in ["que", "tienes", "hay", "disponible"]):
            return {"intencion": "consulta_catalogo", "confianza": 0.6}
        else:
            return {"intencion": "consulta_general", "confianza": 0.5}

class SmartResponseGenerator:
    """Generador de respuestas inteligentes y contextuales"""
    
    def __init__(self, db: Session):
        self.db = db
        self.analyzer = ConversationAnalyzer(db)
    
    def generate_contextual_response(
        self,
        intent_result: Dict,
        productos: List[Dict],
        tenant_info: Dict,
        telefono: str,
        tenant_id: str
    ) -> str:
        """Genera respuesta contextual basada en la intención y el historial"""
        
        context = self.analyzer.get_conversation_context(telefono, tenant_id)
        user_behavior = intent_result.get("contexto_aplicado", {}).get("patron_comportamiento", "nuevo_usuario")
        
        # Personalizar saludo según el tipo de usuario
        if intent_result["intencion"] == "saludo":
            return self._generate_personalized_greeting(context, tenant_info, user_behavior)
        
        # Respuesta contextual para consultas de productos
        elif intent_result["intencion"] == "consulta_producto":
            return self._generate_product_response_with_context(
                intent_result, productos, context, tenant_info
            )
        
        # Respuesta para compradores decididos
        elif intent_result["intencion"] == "intencion_compra":
            return self._generate_purchase_response_with_context(
                intent_result, productos, context, tenant_info
            )
        
        # Respuesta estándar con toque personal
        else:
            return self._generate_standard_response_with_personality(
                intent_result, productos, tenant_info, user_behavior
            )
    
    def _generate_personalized_greeting(
        self, 
        context: Dict, 
        tenant_info: Dict, 
        user_behavior: str
    ) -> str:
        """Saludo personalizado según el historial del usuario"""
        
        store_name = tenant_info.get("name", "nuestra tienda")
        
        if context.get("primera_interaccion", True):
            return f"¡Hola! 👋 Bienvenido a {store_name}. Soy tu asistente de ventas inteligente. ¿En qué puedo ayudarte hoy?"
        
        elif user_behavior == "comprador_decidido":
            productos_interes = context.get("productos_consultados", [])
            if productos_interes:
                return f"¡Hola de nuevo! 😊 Veo que anteriormente consultaste sobre {productos_interes[0]}. ¿Te gustaría continuar donde lo dejamos o necesitas algo más?"
        
        elif user_behavior == "explorador_activo":
            return f"¡Qué bueno verte otra vez! 🌟 Veo que te gusta explorar nuestro catálogo. ¿Hay algo específico que tengas en mente hoy?"
        
        else:
            return f"¡Hola otra vez! 👋 ¿En qué te puedo ayudar en {store_name}?"
    
    def _generate_product_response_with_context(
        self,
        intent_result: Dict,
        productos: List[Dict],
        context: Dict,
        tenant_info: Dict
    ) -> str:
        """Respuesta de producto enriquecida con contexto"""
        
        producto_mencionado = intent_result.get("producto_mencionado", "")
        productos_previos = context.get("productos_consultados", [])
        
        # Buscar el producto específico
        producto_encontrado = None
        for prod in productos:
            if producto_mencionado and producto_mencionado.lower() in prod["name"].lower():
                producto_encontrado = prod
                break
        
        if not producto_encontrado:
            return f"No encontré '{producto_mencionado}' en nuestro catálogo actual. ¿Te gustaría ver productos similares?"
        
        # Generar respuesta contextual
        respuesta = f"📦 **{producto_encontrado['name']}**\n"
        respuesta += f"💰 Precio: ${producto_encontrado['price']:,.0f}\n"
        respuesta += f"📊 Stock: {producto_encontrado['stock']} unidades\n"
        
        if producto_encontrado.get("description"):
            respuesta += f"📝 {producto_encontrado['description']}\n"
        
        # Agregar contexto personalizado
        if producto_mencionado in productos_previos:
            respuesta += f"\n💡 Veo que ya consultaste este producto antes. ¿Te decidiste a comprarlo?"
        
        respuesta += f"\n🛒 Para comprar, escribe: 'Quiero {producto_encontrado['name']}'"
        
        return respuesta
    
    def _generate_purchase_response_with_context(
        self,
        intent_result: Dict,
        productos: List[Dict],
        context: Dict,
        tenant_info: Dict
    ) -> str:
        """Respuesta de compra con sugerencias contextuales"""
        
        return "¡Perfecto! Te ayudo con tu compra. ¿Qué producto específico te interesa?"
    
    def _generate_standard_response_with_personality(
        self,
        intent_result: Dict,
        productos: List[Dict],
        tenant_info: Dict,
        user_behavior: str
    ) -> str:
        """Respuesta estándar con personalidad según el comportamiento del usuario"""
        
        # Personalizar según el tipo de usuario
        if user_behavior == "explorador_activo":
            return "Me encanta que explores nuestro catálogo! 🔍 ¿Hay alguna categoría específica que te interese?"
        elif user_behavior == "comprador_decidido":
            return "Perfecto! Vamos directo al grano. ¿Qué producto específico necesitas?"
        else:
            return "¿En qué puedo ayudarte exactamente? Estoy aquí para hacer tu experiencia de compra lo más fácil posible 😊"

# Función principal de integración
def process_message_with_ai_improvements(
    db: Session,
    telefono: str,
    tenant_id: str,
    mensaje: str,
    productos: List[Dict],
    tenant_info: Dict
) -> Tuple[str, Dict]:
    """
    Procesamiento de mensaje con todas las mejoras de IA integradas
    Retorna: (respuesta_generada, metadata_ia)
    """
    start_time = datetime.now()
    
    # Inicializar servicios de IA
    intent_detector = AdvancedIntentDetector(db)
    response_generator = SmartResponseGenerator(db)
    analyzer = ConversationAnalyzer(db)
    
    try:
        # 1. Detectar intención con contexto
        intent_result = intent_detector.detect_intent_with_context(
            mensaje, telefono, tenant_id, productos
        )
        
        # 2. Generar respuesta contextual
        respuesta = response_generator.generate_contextual_response(
            intent_result, productos, tenant_info, telefono, tenant_id
        )
        
        # 3. Calcular tiempo de respuesta
        end_time = datetime.now()
        duracion_ms = int((end_time - start_time).total_seconds() * 1000)
        
        # 4. Registrar conversación para análisis futuro
        conversation_id = analyzer.log_conversation(
            telefono=telefono,
            tenant_id=tenant_id,
            mensaje_usuario=mensaje,
            respuesta_bot=respuesta,
            intencion_detectada=intent_result.get("intencion"),
            productos_mencionados=[intent_result.get("producto_mencionado")] if intent_result.get("producto_mencionado") else [],
            contexto_sesion=intent_result.get("contexto_aplicado", {}),
            duracion_ms=duracion_ms
        )
        
        # 5. Metadata para debugging y análisis
        metadata = {
            "conversation_id": conversation_id,
            "intent_confidence": intent_result.get("confianza", 0),
            "response_time_ms": duracion_ms,
            "context_applied": intent_result.get("contexto_aplicado", {}),
            "ai_version": "v3.0-simplified"
        }
        
        return respuesta, metadata
        
    except Exception as e:
        print(f"Error in AI processing: {e}")
        # Fallback a respuesta básica
        return "Lo siento, estoy experimentando dificultades técnicas. ¿Puedes repetir tu consulta?", {"error": str(e)}