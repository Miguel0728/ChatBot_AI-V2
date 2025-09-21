import os
import sys
from dotenv import load_dotenv
from openai import OpenAI

def test_openai_connection():
    """Prueba la conexión con OpenAI"""
    print("🔍 Probando conexión con OpenAI...")
    
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("❌ No se encontró la API key de OpenAI en el archivo .env")
        print("📋 Por favor, agrega tu API key en el archivo .env:")
        print("   OPENAI_API_KEY=tu_api_key_aqui")
        return False
    
    try:
        client = OpenAI(api_key=api_key)
        
        # Prueba simple
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Di 'Conexión exitosa'"}],
            max_tokens=10
        )
        
        print("✅ Conexión exitosa con OpenAI")
        print(f"📝 Respuesta de prueba: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        print(f"❌ Error al conectar con OpenAI: {e}")
        return False

def test_chatbot_functionality():
    """Prueba funcionalidades específicas del chatbot"""
    print("\n🤖 Probando funcionalidades del chatbot...")
    
    load_dotenv()
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    # Mensajes de prueba
    test_messages = [
        "Hola, ¿cómo estás?",
        "¿Cuál es la capital de Francia?",
        "Cuéntame un chiste",
        "¿Puedes ayudarme con programación en Python?"
    ]
    
    mensajes = [
        {"role": "system", "content": "Eres un asistente relajado y divertido."}
    ]
    
    for i, test_msg in enumerate(test_messages, 1):
        try:
            print(f"\n📤 Prueba {i}: {test_msg}")
            
            mensajes.append({"role": "user", "content": test_msg})
            
            respuesta = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=mensajes,
                max_tokens=150
            )
            
            contenido = respuesta.choices[0].message.content
            mensajes.append({"role": "assistant", "content": contenido})
            
            print(f"📥 Respuesta: {contenido[:100]}...")
            print("✅ Prueba exitosa")
            
        except Exception as e:
            print(f"❌ Error en prueba {i}: {e}")

def test_error_handling():
    """Prueba el manejo de errores"""
    print("\n⚠️ Probando manejo de errores...")
    
    # Prueba con API key inválida
    try:
        client = OpenAI(api_key="invalid_key")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "test"}]
        )
        print("❌ Error: debería haber fallado con API key inválida")
    except Exception as e:
        print("✅ Manejo de errores correcto para API key inválida")

def run_interactive_test():
    """Ejecuta una prueba interactiva limitada"""
    print("\n🎮 Prueba interactiva (máximo 3 mensajes)...")
    
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("❌ No se puede hacer prueba interactiva sin API key")
        return
    
    client = OpenAI(api_key=api_key)
    mensajes = [
        {"role": "system", "content": "Eres un asistente relajado y divertido."}
    ]
    
    print("💬 Escribe hasta 3 mensajes para probar el chatbot (escribe 'salir' para terminar antes)")
    
    for i in range(3):
        entrada = input(f"\nTú ({i+1}/3): ")
        
        if entrada.lower() == "salir":
            break
            
        mensajes.append({"role": "user", "content": entrada})
        
        try:
            respuesta = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=mensajes
            )
            contenido = respuesta.choices[0].message.content
            mensajes.append({"role": "assistant", "content": contenido})
            print(f"🤖 IA: {contenido}")
            
        except Exception as e:
            print(f"❌ Error: {e}")

def main():
    print("🚀 PRUEBAS DEL CHATBOT AI")
    print("=" * 40)
    
    # Ejecutar todas las pruebas
    if test_openai_connection():
        test_chatbot_functionality()
        test_error_handling()
        
        # Preguntar si quiere hacer prueba interactiva
        respuesta = input("\n❓ ¿Quieres hacer una prueba interactiva? (s/n): ")
        if respuesta.lower() in ['s', 'si', 'sí', 'y', 'yes']:
            run_interactive_test()
    
    print("\n🏁 Pruebas completadas!")

if __name__ == "__main__":
    main()
