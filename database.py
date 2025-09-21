import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Optional

class DatabaseManager:
    """Manejador de base de datos SQLite para el chatbot"""
    
    def __init__(self, db_path: str = "chatbot.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Inicializa la base de datos y crea las tablas necesarias"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabla para sesiones de usuario
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_name TEXT,
                session_data TEXT
            )
        ''')
        
        # Tabla para mensajes de conversación
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                role TEXT CHECK(role IN ('system', 'user', 'assistant')),
                content TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                tokens_used INTEGER DEFAULT 0,
                FOREIGN KEY (session_id) REFERENCES sessions (id)
            )
        ''')
        
        # Tabla para configuraciones
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Índices para mejorar performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_session ON messages(session_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_activity ON sessions(last_activity)')
        
        conn.commit()
        conn.close()
        
        print(f"✅ Base de datos inicializada: {self.db_path}")
    
    def create_session(self, session_id: str, user_name: str = None) -> bool:
        """Crea una nueva sesión de usuario"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO sessions (id, user_name, created_at, last_activity)
                VALUES (?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            ''', (session_id, user_name))
            
            # Agregar mensaje del sistema
            cursor.execute('''
                INSERT INTO messages (session_id, role, content)
                VALUES (?, 'system', 'Eres un asistente relajado y divertido. Responde de manera amigable y útil.')
            ''', (session_id,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error al crear sesión: {e}")
            return False
    
    def add_message(self, session_id: str, role: str, content: str, tokens_used: int = 0) -> bool:
        """Agrega un mensaje a la conversación"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Verificar que la sesión existe
            cursor.execute('SELECT id FROM sessions WHERE id = ?', (session_id,))
            if not cursor.fetchone():
                self.create_session(session_id)
            
            # Agregar mensaje
            cursor.execute('''
                INSERT INTO messages (session_id, role, content, tokens_used)
                VALUES (?, ?, ?, ?)
            ''', (session_id, role, content, tokens_used))
            
            # Actualizar última actividad de la sesión
            cursor.execute('''
                UPDATE sessions SET last_activity = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (session_id,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error al agregar mensaje: {e}")
            return False
    
    def get_conversation_history(self, session_id: str, limit: int = 50) -> List[Dict]:
        """Obtiene el historial de conversación de una sesión"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT role, content, timestamp, tokens_used
                FROM messages
                WHERE session_id = ?
                ORDER BY timestamp ASC
                LIMIT ?
            ''', (session_id, limit))
            
            messages = []
            for row in cursor.fetchall():
                messages.append({
                    'role': row[0],
                    'content': row[1],
                    'timestamp': row[2],
                    'tokens_used': row[3]
                })
            
            conn.close()
            return messages
        except Exception as e:
            print(f"Error al obtener historial: {e}")
            return []
    
    def get_openai_messages(self, session_id: str, limit: int = 20) -> List[Dict]:
        """Obtiene mensajes en formato OpenAI para la API"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT role, content
                FROM messages
                WHERE session_id = ? AND role IN ('system', 'user', 'assistant')
                ORDER BY timestamp ASC
                LIMIT ?
            ''', (session_id, limit))
            
            messages = []
            for row in cursor.fetchall():
                messages.append({
                    'role': row[0],
                    'content': row[1]
                })
            
            conn.close()
            return messages
        except Exception as e:
            print(f"Error al obtener mensajes OpenAI: {e}")
            return [{"role": "system", "content": "Eres un asistente relajado y divertido."}]
    
    def clear_session(self, session_id: str) -> bool:
        """Limpia todas las conversaciones de una sesión (excepto el mensaje del sistema)"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Eliminar todos los mensajes excepto el del sistema
            cursor.execute('''
                DELETE FROM messages
                WHERE session_id = ? AND role != 'system'
            ''', (session_id,))
            
            # Actualizar última actividad
            cursor.execute('''
                UPDATE sessions SET last_activity = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (session_id,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error al limpiar sesión: {e}")
            return False
    
    def get_session_stats(self, session_id: str) -> Dict:
        """Obtiene estadísticas de una sesión"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Contar mensajes
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_messages,
                    COUNT(CASE WHEN role = 'user' THEN 1 END) as user_messages,
                    COUNT(CASE WHEN role = 'assistant' THEN 1 END) as bot_messages,
                    SUM(tokens_used) as total_tokens
                FROM messages
                WHERE session_id = ?
            ''', (session_id,))
            
            stats = cursor.fetchone()
            
            # Obtener info de la sesión
            cursor.execute('''
                SELECT created_at, last_activity
                FROM sessions
                WHERE id = ?
            ''', (session_id,))
            
            session_info = cursor.fetchone()
            
            conn.close()
            
            return {
                'total_messages': stats[0] if stats else 0,
                'user_messages': stats[1] if stats else 0,
                'bot_messages': stats[2] if stats else 0,
                'total_tokens': stats[3] if stats else 0,
                'created_at': session_info[0] if session_info else None,
                'last_activity': session_info[1] if session_info else None
            }
        except Exception as e:
            print(f"Error al obtener estadísticas: {e}")
            return {}
    
    def get_all_sessions(self, limit: int = 10) -> List[Dict]:
        """Obtiene todas las sesiones ordenadas por última actividad"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT s.id, s.user_name, s.created_at, s.last_activity,
                       COUNT(m.id) as message_count
                FROM sessions s
                LEFT JOIN messages m ON s.id = m.session_id
                GROUP BY s.id
                ORDER BY s.last_activity DESC
                LIMIT ?
            ''', (limit,))
            
            sessions = []
            for row in cursor.fetchall():
                sessions.append({
                    'session_id': row[0],
                    'user_name': row[1],
                    'created_at': row[2],
                    'last_activity': row[3],
                    'message_count': row[4]
                })
            
            conn.close()
            return sessions
        except Exception as e:
            print(f"Error al obtener sesiones: {e}")
            return []
    
    def backup_database(self, backup_path: str = None) -> bool:
        """Crea un backup de la base de datos"""
        try:
            if not backup_path:
                backup_path = f"backup_chatbot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            
            import shutil
            shutil.copy2(self.db_path, backup_path)
            print(f"✅ Backup creado: {backup_path}")
            return True
        except Exception as e:
            print(f"Error al crear backup: {e}")
            return False
    
    def close(self):
        """Cierra la conexión a la base de datos"""
        pass  # SQLite se cierra automáticamente
