import json
import openai

def generar_respuesta_con_ia(mensaje: str, productos: list, tenant_info: dict, contexto: str = "general") -> str:
    """Genera respuestas más naturales usando GPT"""
    try:
        client = openai.OpenAI()
        productos_lista = ", ".join([f"{prod['name']} (${prod['price']})" for prod in productos[:5]])
        
        if contexto == "saludo":
            prompt = f"""
            Eres un asistente de ventas de {tenant_info['name']}, especializada en {tenant_info.get('type', 'productos')}.
            
            El cliente escribió: "{mensaje}"
            
            Responde de manera cálida y profesional:
            - Saluda cordialmente mencionando el nombre de la tienda
            - Pregunta en qué puedes ayudar hoy
            - Máximo 2 frases, tono amigable
            
            NO menciones productos aún.
            """
        
        elif contexto == "producto_no_encontrado":
            prompt = f"""
            Eres un asistente de ventas de {tenant_info['name']}.
            
            El cliente busca: "{mensaje}"
            Productos disponibles: {productos_lista}
            
            Responde de manera útil:
            - Informa que no tienes exactamente lo que busca
            - Sugiere un producto similar si hay alguno relacionado
            - O invita a ver el catálogo
            - Máximo 2 frases, tono comprensivo
            """
        
        else:  # respuesta_general
            prompt = f"""
            Eres un asistente de ventas de {tenant_info['name']}, especializada en {tenant_info.get('type', 'productos')}.
            
            Cliente escribió: "{mensaje}"
            Productos disponibles: {productos_lista}
            
            Responde de manera natural y útil:
            - Si pregunta por algo específico, ayúdale a encontrarlo
            - Si es confuso, pide clarificación
            - Siempre mantén el foco en ayudar con la compra
            - Máximo 3 frases, tono profesional y amigable
            """
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            max_tokens=100
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        print(f"Error IA: {e}")
        return None

def detectar_intencion_compra(mensaje: str, productos: list) -> dict:
    """Detecta si el cliente quiere comprar algo específico"""
    try:
        client = openai.OpenAI()
        productos_lista = "\n".join([f"- {prod['name']}" for prod in productos])
        
        prompt = f"""
        PRODUCTOS DISPONIBLES:
        {productos_lista}
        
        MENSAJE: "{mensaje}"
        
        ¿El cliente quiere comprar un producto específico?
        
        Responde SOLO en este formato JSON:
        {{"quiere_comprar": true/false, "producto": "nombre exacto del producto o null", "cantidad": numero o null}}
        """
        
        response = client.chat.completions.create(
            model="gpt-4o-mini", 
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=80
        )
        
        respuesta = response.choices[0].message.content.strip()
        if respuesta.startswith("```json"):
            respuesta = respuesta.replace("```json", "").replace("```", "").strip()
        
        return json.loads(respuesta)
        
    except Exception as e:
        print(f"Error detectando intención: {e}")
        return {"quiere_comprar": False, "producto": None, "cantidad": None}