"""
🤖 INTEGRACIÓN DE QUERIES SQL CON PROMPTS DEL BOT
Genera instrucciones automáticas para que el bot use las queries configuradas
"""
import logging
from typing import Dict, List, Any, Optional
from prompt_schemas import DatabaseQueries, DatabaseQuery

logger = logging.getLogger(__name__)

class BotPromptIntegration:
    """
    🔗 Servicio para integrar queries SQL dinámicas con prompts del bot
    
    Características:
    - Genera instrucciones automáticas para el bot
    - Explica qué información puede consultar
    - Proporciona ejemplos de uso
    - Documenta parámetros disponibles
    """
    
    @staticmethod
    def generate_database_instructions(db_queries: DatabaseQueries) -> str:
        """
        Genera instrucciones para el bot sobre qué puede consultar en la BD
        
        Args:
            db_queries: Configuración de queries disponibles
            
        Returns:
            str: Instrucciones formateadas para incluir en el prompt del sistema
        """
        if not db_queries:
            return ""
        
        instructions = []
        instructions.append("\n🗃️ INFORMACIÓN DE BASE DE DATOS DISPONIBLE:")
        instructions.append("Tienes acceso a consultar información actualizada en tiempo real de la base de datos.")
        instructions.append("Usa esta información para responder preguntas específicas de los clientes.\n")
        
        # Agregar instrucciones para cada query activa
        if db_queries.products_query and db_queries.products_query.is_active:
            instructions.append(BotPromptIntegration._format_query_instructions(
                "📦 PRODUCTOS", 
                db_queries.products_query,
                [
                    "¿Qué productos tienes disponibles?",
                    "¿Tienes productos de la categoría X?",
                    "¿Cuánto cuesta el producto Y?",
                    "¿Hay stock del producto Z?"
                ]
            ))
        
        if db_queries.campaigns_query and db_queries.campaigns_query.is_active:
            instructions.append(BotPromptIntegration._format_query_instructions(
                "📢 CAMPAÑAS",
                db_queries.campaigns_query, 
                [
                    "¿Qué promociones tienen activas?",
                    "¿Hay alguna campaña especial?",
                    "¿Cuándo termina la promoción actual?"
                ]
            ))
        
        if db_queries.discounts_query and db_queries.discounts_query.is_active:
            instructions.append(BotPromptIntegration._format_query_instructions(
                "💰 DESCUENTOS",
                db_queries.discounts_query,
                [
                    "¿Qué descuentos están disponibles?",
                    "¿Hay alguna oferta especial?",
                    "¿Cuánto descuento puedo obtener?"
                ]
            ))
        
        # Agregar queries personalizadas
        if db_queries.custom_queries:
            for custom_query in db_queries.custom_queries:
                if custom_query.is_active:
                    instructions.append(BotPromptIntegration._format_query_instructions(
                        f"🔧 {custom_query.name.upper()}",
                        custom_query,
                        ["Pregunta personalizada sobre " + custom_query.description]
                    ))
        
        instructions.append("\n🎯 INSTRUCCIONES DE USO:")
        instructions.append("- Cuando el cliente pregunte sobre productos, consulta la base de datos")
        instructions.append("- Siempre proporciona información actualizada y precisa") 
        instructions.append("- Si no encuentras información específica, sugiérele alternativas")
        instructions.append("- Menciona precios, stock y características relevantes")
        instructions.append("- Sugiere productos relacionados cuando sea apropiado")
        
        return "\n".join(instructions)
    
    @staticmethod
    def _format_query_instructions(title: str, query: DatabaseQuery, examples: List[str]) -> str:
        """Formatea las instrucciones para una query específica"""
        lines = []
        lines.append(f"\n{title}:")
        lines.append(f"- Descripción: {query.description}")
        lines.append(f"- Puedes consultar hasta {query.max_results} resultados")
        
        if query.parameters:
            params_text = ", ".join([p for p in query.parameters if p != "client_id"])
            if params_text:
                lines.append(f"- Parámetros disponibles: {params_text}")
        
        lines.append("- Ejemplos de preguntas que puedes responder:")
        for example in examples[:3]:  # Máximo 3 ejemplos
            lines.append(f"  • {example}")
        
        return "\n".join(lines)
    
    @staticmethod
    def generate_enhanced_system_prompt(
        base_prompt: str, 
        db_queries: DatabaseQueries,
        business_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Genera un prompt del sistema mejorado con capacidades de BD
        
        Args:
            base_prompt: Prompt base configurado por el usuario
            db_queries: Queries de BD configuradas
            business_context: Contexto adicional del negocio
            
        Returns:
            str: Prompt del sistema completo y mejorado
        """
        enhanced_prompt = base_prompt
        
        # Agregar instrucciones de base de datos
        db_instructions = BotPromptIntegration.generate_database_instructions(db_queries)
        if db_instructions:
            enhanced_prompt += "\n\n" + db_instructions
        
        # Agregar contexto de negocio si está disponible
        if business_context:
            business_info = BotPromptIntegration._format_business_context(business_context)
            if business_info:
                enhanced_prompt += "\n\n" + business_info
        
        # Agregar instrucciones finales
        enhanced_prompt += "\n\n🚀 CAPACIDADES ESPECIALES:"
        enhanced_prompt += "\n- Consultas en tiempo real a la base de datos"
        enhanced_prompt += "\n- Información siempre actualizada de productos y promociones"
        enhanced_prompt += "\n- Respuestas precisas basadas en datos reales"
        enhanced_prompt += "\n- Sugerencias personalizadas según disponibilidad"
        
        return enhanced_prompt
    
    @staticmethod
    def _format_business_context(business_context: Dict[str, Any]) -> str:
        """Formatea el contexto del negocio para incluir en el prompt"""
        lines = []
        lines.append("📊 CONTEXTO DEL NEGOCIO:")
        
        if business_context.get("business_type"):
            lines.append(f"- Tipo de negocio: {business_context['business_type']}")
        
        if business_context.get("total_products"):
            lines.append(f"- Total de productos: {business_context['total_products']}")
        
        if business_context.get("categories"):
            categories = ", ".join(business_context["categories"][:5])  # Máximo 5 categorías
            lines.append(f"- Categorías principales: {categories}")
        
        if business_context.get("active_campaigns"):
            lines.append(f"- Campañas activas: {business_context['active_campaigns']}")
        
        if business_context.get("active_discounts"):
            lines.append(f"- Descuentos vigentes: {business_context['active_discounts']}")
        
        return "\n".join(lines) if len(lines) > 1 else ""
    
    @staticmethod
    def generate_query_examples(db_queries: DatabaseQueries) -> List[Dict[str, Any]]:
        """
        Genera ejemplos de preguntas y respuestas para mostrar las capacidades del bot
        
        Returns:
            Lista de ejemplos con pregunta, query usada y tipo de respuesta esperada
        """
        examples = []
        
        if db_queries.products_query and db_queries.products_query.is_active:
            examples.extend([
                {
                    "question": "¿Qué productos tienen disponibles?",
                    "query_type": "productos",
                    "parameters": {"category": "%", "limit": 10},
                    "expected_response": "Lista de productos con nombres, precios y stock"
                },
                {
                    "question": "¿Tienes productos de cannabis?",
                    "query_type": "productos", 
                    "parameters": {"category": "cannabis", "limit": 5},
                    "expected_response": "Productos específicos de la categoría cannabis"
                }
            ])
        
        if db_queries.discounts_query and db_queries.discounts_query.is_active:
            examples.extend([
                {
                    "question": "¿Qué descuentos tienen disponibles?",
                    "query_type": "descuentos",
                    "parameters": {"limit": 5},
                    "expected_response": "Lista de descuentos activos con porcentajes o montos"
                }
            ])
        
        if db_queries.campaigns_query and db_queries.campaigns_query.is_active:
            examples.extend([
                {
                    "question": "¿Hay alguna promoción especial?", 
                    "query_type": "campanas",
                    "parameters": {"limit": 3},
                    "expected_response": "Campañas promocionales activas con fechas"
                }
            ])
        
        return examples
    
    @staticmethod
    def validate_query_integration(base_prompt: str, db_queries: DatabaseQueries) -> Dict[str, Any]:
        """
        Valida que la integración de queries con prompts sea coherente
        
        Returns:
            Diccionario con el resultado de la validación
        """
        validation = {
            "is_valid": True,
            "warnings": [],
            "suggestions": []
        }
        
        # Verificar que hay al menos una query activa
        active_queries = []
        if db_queries.products_query and db_queries.products_query.is_active:
            active_queries.append("productos")
        if db_queries.campaigns_query and db_queries.campaigns_query.is_active:
            active_queries.append("campañas")
        if db_queries.discounts_query and db_queries.discounts_query.is_active:
            active_queries.append("descuentos")
        
        if not active_queries:
            validation["warnings"].append("No hay queries activas configuradas")
            validation["suggestions"].append("Activa al menos una query para aprovechar la funcionalidad de BD")
        
        # Verificar que el prompt menciona productos o información de BD
        prompt_lower = base_prompt.lower()
        database_keywords = ["productos", "catalogo", "inventario", "stock", "precio", "descuento", "promocion", "campaña"]
        has_db_references = any(keyword in prompt_lower for keyword in database_keywords)
        
        if not has_db_references and active_queries:
            validation["suggestions"].append("Considera mencionar productos o información de BD en tu prompt base")
        
        validation["active_queries_count"] = len(active_queries)
        validation["active_queries"] = active_queries
        
        return validation