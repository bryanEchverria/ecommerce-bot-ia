"""
🤖 SISTEMA AVANZADO DE IA - MEJORAS INTELIGENTES
Sistema de entrenamiento, análisis y mejora continua del bot
"""
import json
import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import text
import openai

# Configuración OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

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
        """Registra una conversación completa para análisis posterior"""
        try:
            query = text("""
                INSERT INTO conversation_history 
                (telefono, tenant_id, mensaje_usuario, respuesta_bot, intencion_detectada, 
                 productos_mencionados, contexto_sesion, duracion_respuesta_ms)
                VALUES (:telefono, :tenant_id, :mensaje_usuario, :respuesta_bot, 
                        :intencion_detectada, :productos_mencionados, :contexto_sesion, :duracion_ms)
                RETURNING id
            """)
            
            result = self.db.execute(query, {
                "telefono": telefono,
                "tenant_id": tenant_id,
                "mensaje_usuario": mensaje_usuario,
                "respuesta_bot": respuesta_bot,
                "intencion_detectada": intencion_detectada,
                "productos_mencionados": productos_mencionados or [],
                "contexto_sesion": json.dumps(contexto_sesion or {}),
                "duracion_ms": duracion_ms
            })
            
            self.db.commit()
            return result.scalar()
            
        except Exception as e:
            print(f"Error logging conversation: {e}")
            self.db.rollback()
            return None
    
    def analyze_intent_patterns(self, tenant_id: str, days_back: int = 30) -> Dict:
        """Analiza patrones de intenciones para mejorar detección"""
        try:
            query = text("""
                SELECT 
                    intencion_detectada,
                    COUNT(*) as frecuencia,
                    AVG(CASE WHEN respuesta_bot LIKE '%✅%' OR respuesta_bot LIKE '%🎉%' 
                             THEN 1.0 ELSE 0.5 END) as efectividad_estimada,
                    array_agg(DISTINCT productos_mencionados[1]) FILTER (WHERE productos_mencionados[1] IS NOT NULL) as productos_relacionados
                FROM conversation_history
                WHERE tenant_id = :tenant_id 
                AND timestamp_mensaje >= NOW() - INTERVAL :days_back DAY
                AND intencion_detectada IS NOT NULL
                GROUP BY intencion_detectada
                ORDER BY frecuencia DESC
            """)
            
            result = self.db.execute(query, {
                "tenant_id": tenant_id,
                "days_back": str(days_back)
            })
            
            patterns = []
            for row in result:
                patterns.append({
                    "intencion": row.intencion_detectada,
                    "frecuencia": row.frecuencia,
                    "efectividad": float(row.efectividad_estimada),
                    "productos_relacionados": row.productos_relacionados or []
                })
            
            return {"patterns": patterns, "total_analyzed": len(patterns)}
            
        except Exception as e:
            print(f"Error analyzing intent patterns: {e}")
            return {"patterns": [], "total_analyzed": 0}
    
    def get_conversation_context(self, telefono: str, tenant_id: str) -> Dict:
        """Obtiene contexto inteligente de conversaciones previas"""
        try:
            # Obtener contexto guardado
            query = text("""
                SELECT contexto_json, productos_interes, ultima_actualizacion
                FROM conversation_context
                WHERE telefono = :telefono AND tenant_id = :tenant_id
                AND (expira_en IS NULL OR expira_en > NOW())
            """)
            
            result = self.db.execute(query, {
                "telefono": telefono,
                "tenant_id": tenant_id
            }).first()
            
            if result:
                context = json.loads(result.contexto_json)
                context["productos_interes"] = result.productos_interes
                context["ultima_actualizacion"] = result.ultima_actualizacion.isoformat()
                return context
            
            # Si no hay contexto, crear uno basado en historial reciente
            query = text("""
                SELECT mensaje_usuario, respuesta_bot, intencion_detectada, productos_mencionados
                FROM conversation_history
                WHERE telefono = :telefono AND tenant_id = :tenant_id
                ORDER BY timestamp_mensaje DESC
                LIMIT 10
            """)
            
            result = self.db.execute(query, {
                "telefono": telefono,
                "tenant_id": tenant_id
            })
            
            recent_messages = []
            all_products = []
            intenciones = []
            
            for row in result:
                recent_messages.append({
                    "usuario": row.mensaje_usuario,
                    "bot": row.respuesta_bot,
                    "intencion": row.intencion_detectada
                })
                if row.productos_mencionados:
                    all_products.extend(row.productos_mencionados)
                if row.intencion_detectada:
                    intenciones.append(row.intencion_detectada)
            
            # Crear nuevo contexto
            context = {
                "conversaciones_recientes": recent_messages[-5:],  # Últimas 5
                "productos_consultados": list(set(all_products)),
                "intenciones_frecuentes": list(set(intenciones)),
                "primera_interaccion": len(recent_messages) == 0
            }
            
            # Guardar contexto
            self.save_conversation_context(telefono, tenant_id, context)
            
            return context
            
        except Exception as e:
            print(f"Error getting conversation context: {e}")
            return {"primera_interaccion": True, "productos_consultados": []}
    
    def save_conversation_context(self, telefono: str, tenant_id: str, context: Dict):
        """Guarda el contexto actualizado de la conversación"""
        try:
            productos_interes = context.get("productos_consultados", [])
            expira_en = datetime.now() + timedelta(days=7)  # Contexto válido por 7 días
            
            query = text("""
                INSERT INTO conversation_context 
                (telefono, tenant_id, contexto_json, productos_interes, expira_en)
                VALUES (:telefono, :tenant_id, :contexto_json, :productos_interes, :expira_en)
                ON CONFLICT (telefono, tenant_id)
                DO UPDATE SET 
                    contexto_json = EXCLUDED.contexto_json,
                    productos_interes = EXCLUDED.productos_interes,
                    ultima_actualizacion = NOW(),
                    expira_en = EXCLUDED.expira_en
            """)
            
            self.db.execute(query, {
                "telefono": telefono,
                "tenant_id": tenant_id,
                "contexto_json": json.dumps(context),
                "productos_interes": productos_interes,
                "expira_en": expira_en
            })
            
            self.db.commit()
            
        except Exception as e:
            print(f"Error saving conversation context: {e}")
            self.db.rollback()

class AdvancedIntentDetector:
    """Detector de intenciones mejorado con análisis contextual"""
    
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
        
        # Obtener patrones exitosos para este tenant
        patterns = self.analyzer.analyze_intent_patterns(tenant_id)
        
        # Prompt mejorado con contexto
        prompt = self._build_enhanced_prompt(mensaje, context, patterns, productos)
        
        try:
            import openai
            openai.api_key = os.getenv("OPENAI_API_KEY")
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=400
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Agregar información contextual al resultado
            result["contexto_aplicado"] = {
                "es_cliente_recurrente": not context.get("primera_interaccion", True),
                "productos_previos": context.get("productos_consultados", []),
                "patron_comportamiento": self._analyze_user_behavior(context)
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
        patterns: Dict, 
        productos: List[Dict]
    ) -> str:
        """Construye un prompt enriquecido con contexto e historial"""
        
        context_info = ""
        if not context.get("primera_interaccion", True):
            context_info = f"""
CONTEXTO DE USUARIO:
- Cliente recurrente: Sí
- Productos consultados anteriormente: {', '.join(context.get('productos_consultados', []))}
- Intenciones frecuentes: {', '.join(context.get('intenciones_frecuentes', []))}
- Última interacción: {context.get('ultima_actualizacion', 'Sin datos')}
"""
        
        patterns_info = ""
        if patterns.get("patterns"):
            top_patterns = patterns["patterns"][:3]  # Top 3 patrones
            patterns_info = f"""
PATRONES EXITOSOS DETECTADOS:
{chr(10).join([f"- {p['intencion']}: {p['frecuencia']} usos, {p['efectividad']:.1%} efectividad" for p in top_patterns])}
"""
        
        productos_disponibles = "\n".join([
            f"- {prod['name']} (${prod['price']:,.0f}, Stock: {prod['stock']})"
            for prod in productos[:10]  # Primeros 10 productos
        ])
        
        return f"""
Eres un asistente de ventas inteligente. Analiza el mensaje del usuario y detecta su intención específica.

{context_info}

{patterns_info}

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
    "sentimiento": "positivo|neutral|negativo",
    "productos_rechazados": ["productos que explícitamente NO quiere"],
    "categoria_rechazada": "categoria que explícitamente NO quiere"
}}

REGLAS CRÍTICAS:
1. **NEGACIONES**: Si dice "No quiero X" o "No busco X", registra X en productos_rechazados
2. **CORRECCIONES**: Si dice "No quiero X, busco Y", enfócate SOLO en Y
3. **CATEGORÍAS**: Identifica correctamente: semillas, aceites, flores, comestibles, accesorios
4. **FRUSTRACIÓN**: Si repite una solicitud o corrige, aumenta urgencia a "alta"
5. **PRECISIÓN**: Si menciona una categoría específica, responde SOLO con esa categoría

EJEMPLOS CRÍTICOS:
- "No quiero aceite busco semillas" → categoria_mencionada: "semillas", categoria_rechazada: "aceites"
- "Que semillas tienes" → categoria_mencionada: "semillas"
- "No me sirve eso" → sentimiento: "negativo", urgencia: "alta"
"""
    
    def _analyze_user_behavior(self, context: Dict) -> str:
        """Analiza el patrón de comportamiento del usuario"""
        if context.get("primera_interaccion", True):
            return "nuevo_usuario"
        
        intenciones = context.get("intenciones_frecuentes", [])
        productos = context.get("productos_consultados", [])
        
        if len(productos) > 3:
            return "explorador_activo"
        elif "intencion_compra" in intenciones:
            return "comprador_decidido"
        elif len(intenciones) > 2:
            return "usuario_frecuente"
        else:
            return "usuario_casual"
    
    def _basic_intent_detection(self, mensaje: str, productos: List[Dict]) -> Dict:
        """Detección básica como fallback"""
        mensaje_lower = mensaje.lower()
        
        # Detección simple por palabras clave
        if any(word in mensaje_lower for word in ["hola", "buenos", "buenas"]):
            return {"intencion": "saludo", "confianza": 0.8}
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
        
        # Respuesta para consultas de categoría
        elif intent_result["intencion"] == "consulta_categoria":
            return self._generate_category_response_with_context(
                intent_result, productos, context, tenant_info
            )
        
        # Respuesta para consultas de catálogo completo
        elif intent_result["intencion"] == "consulta_catalogo":
            return self._generate_catalog_response(productos, tenant_info)
        
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
            if producto_mencionado.lower() in prod["name"].lower():
                producto_encontrado = prod
                break
        
        if not producto_encontrado:
            return f"No encontré '{producto_mencionado}' en nuestro catálogo actual. ¿Te gustaría ver productos similares?"
        
        # Generar respuesta contextual
        respuesta = f"📦 **{producto_encontrado['name']}**\n"
        respuesta += f"💰 Precio: ${producto_encontrado['price']:,.0f}\n"
        respuesta += f"📊 Stock: {producto_encontrado['stock']} unidades\n"
        
        if producto_encontrado["description"]:
            respuesta += f"📝 {producto_encontrado['description']}\n"
        
        # Agregar contexto personalizado
        if producto_mencionado in productos_previos:
            respuesta += f"\n💡 Veo que ya consultaste este producto antes. ¿Te decidiste a comprarlo?"
        
        respuesta += f"\n🛒 Para comprar, escribe: 'Quiero {producto_encontrado['name']}'"
        
        return respuesta
    
    def _generate_category_response_with_context(
        self,
        intent_result: Dict,
        productos: List[Dict],
        context: Dict,
        tenant_info: Dict
    ) -> str:
        """Respuesta de categoría que respeta negaciones y correcciones"""
        
        categoria_solicitada = intent_result.get("categoria_mencionada", "").lower()
        categoria_rechazada = intent_result.get("categoria_rechazada", "").lower()
        productos_rechazados = intent_result.get("productos_rechazados", [])
        
        # Filtrar productos por categoría solicitada
        productos_categoria = []
        for prod in productos:
            categoria_prod = prod.get('category', '').lower()
            nombre_prod = prod.get('name', '').lower()
            
            # Verificar si coincide con la categoría solicitada
            categoria_match = False
            if categoria_solicitada in ["semillas", "semilla"] and ("semilla" in nombre_prod or categoria_prod == "semillas"):
                categoria_match = True
            elif categoria_solicitada in ["aceites", "aceite"] and ("aceite" in nombre_prod or "cbd" in nombre_prod or categoria_prod == "aceites"):
                categoria_match = True
            elif categoria_solicitada in ["flores", "flor"] and (any(word in nombre_prod for word in ["northern", "kush", "widow", "flores"]) or categoria_prod == "flores"):
                categoria_match = True
            elif categoria_solicitada in ["comestibles", "comestible"] and ("brownie" in nombre_prod or "comestible" in nombre_prod or categoria_prod == "comestibles"):
                categoria_match = True
            elif categoria_solicitada in ["accesorios", "accesorio"] and (any(word in nombre_prod for word in ["grinder", "bong", "papel", "vaporizador"]) or categoria_prod == "accesorios"):
                categoria_match = True
            
            # Verificar que NO esté en productos rechazados
            es_rechazado = False
            if categoria_rechazada and (categoria_rechazada in nombre_prod or categoria_rechazada in categoria_prod):
                es_rechazado = True
            
            for prod_rechazado in productos_rechazados:
                if prod_rechazado.lower() in nombre_prod:
                    es_rechazado = True
                    break
            
            if categoria_match and not es_rechazado:
                productos_categoria.append(prod)
        
        if not productos_categoria:
            if categoria_rechazada:
                return f"Entiendo que no quieres {categoria_rechazada}. Lamentablemente no tenemos {categoria_solicitada} disponibles en este momento."
            return f"No tenemos {categoria_solicitada} disponibles en este momento."
        
        # Generar respuesta
        store_name = tenant_info.get("name", "nuestra tienda")
        respuesta = f"🏪 **{categoria_solicitada.title()} en {store_name}:**\n\n"
        
        for i, prod in enumerate(productos_categoria, 1):
            precio_formato = f"${prod['price']:,.0f}"
            stock_emoji = "✅" if prod['stock'] > 5 else "⚠️"
            respuesta += f"{i}. **{prod['name']}**\n"
            respuesta += f"   💰 **{precio_formato}**\n"
            if prod['stock'] > 5:
                stock_text = 'Disponible'
            elif prod['stock'] > 0:
                stock_text = f'Quedan {prod["stock"]}'
            else:
                stock_text = 'Agotado'
            respuesta += f"   {stock_emoji} {stock_text}\n"
            if prod.get('description'):
                desc_corta = prod['description'][:60] + "..." if len(prod['description']) > 60 else prod['description']
                respuesta += f"   📝 {desc_corta}\n"
            respuesta += "\n"
        
        respuesta += f"📊 **Resumen:** {len(productos_categoria)} disponibles, 0 agotados\n\n"
        respuesta += "🛒 **Para comprar:** Escribe 'Quiero [nombre del producto]'"
        
        return respuesta
    
    def _generate_purchase_response_with_context(
        self,
        intent_result: Dict,
        productos: List[Dict],
        context: Dict,
        tenant_info: Dict
    ) -> str:
        """Respuesta de compra con sugerencias contextuales"""
        
        # Lógica de generación de respuesta de compra...
        # (Similar a la implementación actual pero con contexto)
        
        return "Respuesta de compra contextual (pendiente de implementar detalles específicos)"
    
    def _generate_standard_response_with_personality(
        self,
        intent_result: Dict,
        productos: List[Dict],
        tenant_info: Dict,
        user_behavior: str
    ) -> str:
        """Respuesta estándar con personalidad según el comportamiento del usuario"""
        
        # Detectar si está preguntando por catálogo/productos - usar la intención
        intencion = intent_result.get("intencion", "")
        contexto = intent_result.get("contexto_detectado", "").lower()
        
        # Si la IA detectó consulta de catálogo O si el contexto contiene palabras clave
        if intencion == "consulta_catalogo" or any(keyword in contexto for keyword in [
            "productos", "catalogo", "catálogo", "que tienes", "que vendes", 
            "que hay", "stock", "disponible", "otros productos", "menu"
        ]):
            return self._generate_catalog_response(productos, tenant_info)
        
        # Personalizar según el tipo de usuario
        if user_behavior == "explorador_activo":
            return "Me encanta que explores nuestro catálogo! 🔍 ¿Hay alguna categoría específica que te interese?"
        elif user_behavior == "comprador_decidido":
            return "Perfecto! Vamos directo al grano. ¿Qué producto específico necesitas?"
        else:
            return "¿En qué puedo ayudarte exactamente? Estoy aquí para hacer tu experiencia de compra lo más fácil posible 😊"
    
    def _generate_catalog_response(self, productos: List[Dict], tenant_info: Dict) -> str:
        """Genera respuesta de catálogo organizada por categorías"""
        if not productos:
            return "Lo siento, no tenemos productos disponibles en este momento."
        
        # Obtener categorías únicas
        categorias = {}
        for prod in productos:
            categoria = prod.get('category', 'General')
            if categoria not in categorias:
                categorias[categoria] = []
            categorias[categoria].append(prod)
        
        # Generar respuesta organizada
        store_name = tenant_info.get("name", "nuestra tienda")
        respuesta = f"🏪 **Catálogo {store_name}:**\n\n"
        
        for categoria, prods in categorias.items():
            respuesta += f"**📂 {categoria}** ({len(prods)} productos)\n"
            for prod in prods[:3]:  # Máximo 3 por categoría
                precio_formato = f"${prod['price']:,.0f}"
                stock_emoji = "✅" if prod['stock'] > 5 else "⚠️"
                respuesta += f"  • {prod['name']} - {precio_formato} {stock_emoji}\n"
            if len(prods) > 3:
                respuesta += f"  • ...y {len(prods)-3} más\n"
            respuesta += "\n"
        
        respuesta += "💬 **Para ver detalles:** Escribe el nombre del producto\n"
        respuesta += "🛒 **Para comprar:** Escribe 'Quiero [producto]'"
        
        return respuesta

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
            "ai_version": "v2.1-enhanced"
        }
        
        return respuesta, metadata
        
    except Exception as e:
        print(f"Error in AI processing: {e}")
        # Fallback a respuesta básica
        return "Lo siento, estoy experimentando dificultades técnicas. ¿Puedes repetir tu consulta?", {"error": str(e)}