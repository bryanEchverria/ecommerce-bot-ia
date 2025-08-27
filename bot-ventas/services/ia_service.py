import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# --- Forzar path absoluto al .env ---
dotenv_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(dotenv_path)

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError(f"❌ No se encontró la variable OPENAI_API_KEY en {dotenv_path}")

client = OpenAI(api_key=api_key)

def interpretar_mensaje(mensaje_usuario: str) -> dict:
    """
    Usa OpenAI para interpretar el mensaje y devolver intención, productos y cantidades.
    Puede interpretar varios productos a la vez.
    """
    prompt = f"""
    Eres un bot de ventas de WhatsApp. Analiza el siguiente mensaje y devuelve en formato JSON:
    - intencion: 'comprar', 'consulta', 'problema' u 'otro'
    - productos: lista de objetos con {{"nombre": <nombre_producto>, "cantidad": <entero>}}
    
    Ejemplo:
    Usuario: "quiero 2 panes y una bebida"
    Respuesta:
    {{
        "intencion": "comprar",
        "productos": [
            {{"nombre": "pan", "cantidad": 2}},
            {{"nombre": "bebida", "cantidad": 1}}
        ]
    }}

    Mensaje: "{mensaje_usuario}"
    Responde SOLO con el JSON válido, sin texto adicional.
    """

    try:
        respuesta = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )

        contenido = respuesta.choices[0].message.content.strip()

        # Intentar parsear a JSON de forma segura
        return json.loads(contenido)

    except json.JSONDecodeError:
        print(f"⚠️ Error: La respuesta no era JSON válido -> {contenido}")
        return {"intencion": "otro", "productos": []}
    except Exception as e:
        print(f"⚠️ Error interpretando mensaje: {e}")
        return {"intencion": "otro", "productos": []}


def interpretar_confirmacion(mensaje_usuario: str) -> str:
    """
    Usa OpenAI para interpretar si el mensaje es confirmación (sí), rechazo (no) u otra cosa.
    """
    prompt = f"""
    Eres un bot de ventas. Analiza el siguiente mensaje y responde SOLO con:
    - "si" si el usuario está confirmando positivamente (acepta el pedido)
    - "no" si el usuario lo está rechazando o cancelando
    - "otro" si no está claro

    Mensaje: "{mensaje_usuario}"
    """

    try:
        respuesta = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        contenido = respuesta.choices[0].message.content.strip().lower()

        if contenido == "si" or "sí" in contenido:
            return "si"
        elif contenido == "no":
            return "no"
        return "otro"

    except Exception as e:
        print(f"⚠️ Error interpretando confirmación: {e}")
        return "otro"
