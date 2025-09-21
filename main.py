import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

mensajes = [
    {"role": "system", "content": "Eres un asistente relajado y divertido."}
]

print("🤖 Hola, como puedo ayudarte hoy? Para terminar escribe salir.\n")

while True:
    entrada = input("Tú: ")
    if entrada.lower() == "salir":
        print("👋 Nos vemos.")
        break

    mensajes.append({"role": "user", "content": entrada})

    try:
        respuesta = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=mensajes
        )
        contenido = respuesta.choices[0].message.content
        mensajes.append({"role": "assistant", "content": contenido})
        print("\nIA:", contenido + "\n")

    except Exception as e:
        print("⚠️  Ocurrió un error:", e)
