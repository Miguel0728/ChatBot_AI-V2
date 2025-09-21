from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import os
from dotenv import load_dotenv
from openai import OpenAI
import uuid
from database import DatabaseManager

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Para manejar sesiones
CORS(app)

# Configurar cliente OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Inicializar base de datos
db = DatabaseManager()

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
            db.create_session(session_id)
        
        # Guardar mensaje del usuario en la base de datos
        db.add_message(session_id, 'user', user_message)
        
        # Obtener historial de conversación desde la base de datos
        messages = db.get_openai_messages(session_id)
        
        # Generar respuesta de OpenAI
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=500,
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content
        
        # Guardar respuesta de la IA en la base de datos
        tokens_used = response.usage.total_tokens if hasattr(response, 'usage') else 0
        db.add_message(session_id, 'assistant', ai_response, tokens_used)
        
        return jsonify({
            'response': ai_response,
            'session_id': session_id,
            'tokens_used': tokens_used
        })
    
    except Exception as e:
        print(f"Error en chat: {e}")
        return jsonify({'error': f'Error interno: {str(e)}'}), 500

@app.route('/clear', methods=['POST'])
def clear_conversation():
    """Limpiar la conversación actual"""
    try:
        session_id = session.get('session_id')
        if session_id:
            success = db.clear_session(session_id)
            if success:
                return jsonify({'message': 'Conversación limpiada exitosamente'})
            else:
                return jsonify({'error': 'Error al limpiar conversación'}), 500
        else:
            return jsonify({'message': 'No hay sesión activa'})
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500

@app.route('/history')
def get_history():
    """Obtener historial de la conversación (sin el mensaje del sistema)"""
    try:
        session_id = session.get('session_id')
        if session_id:
            history = db.get_conversation_history(session_id)
            # Filtrar solo mensajes de usuario y asistente
            filtered_history = [
                {'role': msg['role'], 'content': msg['content'], 'timestamp': msg['timestamp']}
                for msg in history if msg['role'] in ['user', 'assistant']
            ]
            return jsonify({'history': filtered_history})
        else:
            return jsonify({'history': []})
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500

@app.route('/stats')
def get_stats():
    """Obtener estadísticas de la sesión actual"""
    try:
        session_id = session.get('session_id')
        if session_id:
            stats = db.get_session_stats(session_id)
            return jsonify(stats)
        else:
            return jsonify({'message': 'No hay sesión activa'})
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500

@app.route('/sessions')
def get_sessions():
    """Obtener todas las sesiones"""
    try:
        sessions = db.get_all_sessions()
        return jsonify({'sessions': sessions})
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500

@app.route('/backup', methods=['POST'])
def create_backup():
    """Crear backup de la base de datos"""
    try:
        success = db.backup_database()
        if success:
            return jsonify({'message': 'Backup creado exitosamente'})
        else:
            return jsonify({'error': 'Error al crear backup'}), 500
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500

if __name__ == '__main__':
    print("🌐 Iniciando servidor web del chatbot...")
    print("📱 Accede a: http://localhost:5000")
    print("💾 Base de datos SQLite inicializada")
    app.run(debug=True, host='0.0.0.0', port=5000)
