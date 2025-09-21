from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import os
from dotenv import load_dotenv
from openai import OpenAI
import uuid

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Para manejar sesiones
CORS(app)

# Configurar cliente OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Almacenar conversaciones por sesión
conversations = {}

@app.route('/')
def home():
    """Página principal del chatbot"""
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    """Endpoint para procesar mensajes del chat"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'Mensaje vacío'}), 400
        
        # Obtener o crear ID de sesión
        session_id = session.get('session_id')
        if not session_id:
            session_id = str(uuid.uuid4())
            session['session_id'] = session_id
        
        # Obtener o crear historial de conversación
        if session_id not in conversations:
            conversations[session_id] = [
                {"role": "system", "content": "Eres un asistente relajado y divertido. Responde de manera amigable y útil."}
            ]
        
        # Agregar mensaje del usuario
        conversations[session_id].append({"role": "user", "content": user_message})
        
        # Generar respuesta de OpenAI
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=conversations[session_id],
            max_tokens=500,
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content
        
        # Agregar respuesta de la IA al historial
        conversations[session_id].append({"role": "assistant", "content": ai_response})
        
        return jsonify({
            'response': ai_response,
            'session_id': session_id
        })
    
    except Exception as e:
        print(f"Error en chat: {e}")
        return jsonify({'error': f'Error interno: {str(e)}'}), 500

@app.route('/clear', methods=['POST'])
def clear_conversation():
    """Limpiar la conversación actual"""
    session_id = session.get('session_id')
    if session_id and session_id in conversations:
        # Reiniciar conversación manteniendo solo el mensaje del sistema
        conversations[session_id] = [
            {"role": "system", "content": "Eres un asistente relajado y divertido. Responde de manera amigable y útil."}
        ]
    
    return jsonify({'message': 'Conversación limpiada'})

@app.route('/history')
def get_history():
    """Obtener historial de la conversación (sin el mensaje del sistema)"""
    session_id = session.get('session_id')
    if session_id and session_id in conversations:
        # Filtrar solo mensajes de usuario y asistente
        history = [msg for msg in conversations[session_id] if msg['role'] != 'system']
        return jsonify({'history': history})
    
    return jsonify({'history': []})

if __name__ == '__main__':
    print("🌐 Iniciando servidor web del chatbot...")
    print("📱 Accede a: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
