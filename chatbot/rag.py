import re
import httpx
from django.conf import settings
LLAMA_CPP = "llamacpp"
GROQ = "groq"

def generar_respuesta(prompt: str, pregunta: str, n_predict: int = 384, temperatura: float = 0.7, engine: str = "llamacpp"):
    headers = {
        "Content-Type": "application/json"
    }
    if engine == GROQ:
        url = f"{settings.GROQ_API}v1/chat/completions"
        headers["Authorization"] = f"Bearer {settings.GROQ_API_KEY}"
    else:
        url = f"{settings.LLAMACPP_API}veyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzc0NzI1NDAxLCJpYXQiOjE3NzQ3MjE4MDEsImp0aSI6IjQwNTExOGJlOGE4MjQxMzg4N2YyMDFmODdhMDU3MjYyIiwidXNlcl9pZCI6IjEifQ.4mIDJFdt1qJ2mAbZ8Exwuk4psaRjwiEgpXpHwLFCTEQ1/chat/completions"
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": pregunta}
        ],
        "max_tokens": n_predict,
        "temperature": temperatura,
        "stream": False,
        "stop": ["Usuario:", "Pregunta:"],
    }
    print(headers)
    with httpx.Client(timeout=900, headers=headers) as client:
        print("haciendo peticion a: ", url)
        resp = client.post(url, json=payload)
        resp.raise_for_status()
        data = resp.json()
        return data['choices'][0]['message']['content']


def limpiar_respuesta(respuesta: str):
    texto = re.sub(r"```+", "", respuesta)
    
    texto = texto.strip()

    if texto.startswith("=== RESPUESTA ===\n"):
        texto = texto.replace("=== RESPUESTA ===\n", "")
    if texto.startswith("===\nRespuesta ===\n"):
        texto = texto.replace("===\nRespuesta ===\n", "")
    if texto.startswith("=== RESPUESTA\n"):
        texto = texto.replace("=== RESPUESTA\n", "")
    if texto.startswith("===\nRespuesta\nHistorial relevante:\n"):
        texto = texto.replace("===\nRespuesta\nHistorial relevante:\n", "")
    if texto.startswith("Asistente: "):
        texto = texto.replace("Asistente: ", "").strip()
    if texto.startswith("Asistente:\n"):
        texto = texto.replace("Asistente:\n", "").strip()

    return texto.replace("===\nRespuesta\nHistorial relevante:\n", "")
