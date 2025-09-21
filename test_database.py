import os
import sys
from database import DatabaseManager
import uuid

def test_database():
    """Prueba completa del sistema de base de datos"""
    print("🧪 PRUEBAS DEL SISTEMA DE BASE DE DATOS")
    print("=" * 50)
    
    # Usar base de datos de prueba
    db = DatabaseManager("test_chatbot.db")
    
    try:
        # Test 1: Crear sesión
        print("\n📝 Test 1: Crear sesión")
        session_id = str(uuid.uuid4())
        success = db.create_session(session_id, "TestUser")
        print(f"✅ Sesión creada: {success}")
        
        # Test 2: Agregar mensajes
        print("\n💬 Test 2: Agregar mensajes")
        db.add_message(session_id, "user", "Hola, ¿cómo estás?")
        db.add_message(session_id, "assistant", "¡Hola! Estoy muy bien, gracias por preguntar. ¿En qué puedo ayudarte?", 25)
        db.add_message(session_id, "user", "¿Puedes contarme un chiste?")
        db.add_message(session_id, "assistant", "¡Por supuesto! ¿Por qué los programadores prefieren la oscuridad? Porque la luz atrae bugs. 😄", 30)
        print("✅ Mensajes agregados correctamente")
        
        # Test 3: Obtener historial
        print("\n📚 Test 3: Obtener historial")
        history = db.get_conversation_history(session_id)
        print(f"✅ Historial obtenido: {len(history)} mensajes")
        for msg in history[:3]:  # Mostrar primeros 3
            print(f"   {msg['role']}: {msg['content'][:50]}...")
        
        # Test 4: Obtener mensajes para OpenAI
        print("\n🤖 Test 4: Formato OpenAI")
        openai_messages = db.get_openai_messages(session_id)
        print(f"✅ Mensajes OpenAI: {len(openai_messages)}")
        
        # Test 5: Estadísticas
        print("\n📊 Test 5: Estadísticas")
        stats = db.get_session_stats(session_id)
        print(f"✅ Estadísticas obtenidas:")
        print(f"   Total mensajes: {stats.get('total_messages', 0)}")
        print(f"   Mensajes usuario: {stats.get('user_messages', 0)}")
        print(f"   Mensajes bot: {stats.get('bot_messages', 0)}")
        print(f"   Tokens usados: {stats.get('total_tokens', 0)}")
        
        # Test 6: Crear segunda sesión
        print("\n👥 Test 6: Múltiples sesiones")
        session_id2 = str(uuid.uuid4())
        db.create_session(session_id2, "TestUser2")
        db.add_message(session_id2, "user", "¿Cuál es la capital de Francia?")
        db.add_message(session_id2, "assistant", "La capital de Francia es París.", 15)
        
        sessions = db.get_all_sessions()
        print(f"✅ Total de sesiones: {len(sessions)}")
        
        # Test 7: Limpiar sesión
        print("\n🧹 Test 7: Limpiar sesión")
        success = db.clear_session(session_id)
        print(f"✅ Sesión limpiada: {success}")
        
        history_after_clear = db.get_conversation_history(session_id)
        print(f"✅ Mensajes después de limpiar: {len(history_after_clear)}")
        
        # Test 8: Backup
        print("\n💾 Test 8: Crear backup")
        backup_success = db.backup_database("test_backup.db")
        print(f"✅ Backup creado: {backup_success}")
        
        print("\n🎉 TODAS LAS PRUEBAS PASARON EXITOSAMENTE")
        
    except Exception as e:
        print(f"❌ Error en las pruebas: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Limpiar archivos de prueba
        try:
            if os.path.exists("test_chatbot.db"):
                os.remove("test_chatbot.db")
                print("🗑️ Archivo de prueba eliminado")
            if os.path.exists("test_backup.db"):
                os.remove("test_backup.db")
                print("🗑️ Backup de prueba eliminado")
        except:
            pass

def test_performance():
    """Prueba de rendimiento con múltiples mensajes"""
    print("\n⚡ PRUEBA DE RENDIMIENTO")
    print("=" * 30)
    
    db = DatabaseManager("perf_test.db")
    session_id = str(uuid.uuid4())
    db.create_session(session_id)
    
    import time
    
    # Insertar muchos mensajes
    start_time = time.time()
    for i in range(100):
        db.add_message(session_id, "user", f"Mensaje de prueba {i}")
        db.add_message(session_id, "assistant", f"Respuesta de prueba {i}", 20)
    
    insert_time = time.time() - start_time
    print(f"✅ Inserción de 200 mensajes: {insert_time:.2f} segundos")
    
    # Leer historial
    start_time = time.time()
    history = db.get_conversation_history(session_id)
    read_time = time.time() - start_time
    print(f"✅ Lectura de {len(history)} mensajes: {read_time:.3f} segundos")
    
    # Limpiar
    try:
        os.remove("perf_test.db")
    except:
        pass

if __name__ == "__main__":
    test_database()
    test_performance()
    
    print("\n🚀 ¿Quieres probar la aplicación web con persistencia?")
    print("Ejecuta: python app.py")
