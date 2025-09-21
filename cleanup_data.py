#!/usr/bin/env python3
"""
Script para limpiar datos del ChatBot AI
Permite eliminar información guardada de forma selectiva
"""

import os
import sys
from database import DatabaseManager
from datetime import datetime

def show_menu():
    """Muestra el menú de opciones"""
    print("\n🗑️  LIMPIEZA DE DATOS - CHATBOT AI")
    print("=" * 40)
    print("1. 🧹 Limpiar TODA la base de datos")
    print("2. 📋 Limpiar sesiones específicas")
    print("3. 📊 Ver estadísticas actuales")
    print("4. 💾 Crear backup antes de limpiar")
    print("5. 🔄 Resetear solo mi sesión actual")
    print("6. ❌ Salir")
    print("-" * 40)

def clear_all_database():
    """Elimina completamente la base de datos"""
    confirm = input("⚠️  ¿Estás SEGURO de que quieres eliminar TODA la información? (escribe 'SÍ ELIMINAR'): ")
    if confirm == "SÍ ELIMINAR":
        try:
            if os.path.exists("chatbot.db"):
                os.remove("chatbot.db")
                print("✅ Base de datos eliminada completamente")
                
                # Crear nueva base de datos limpia
                db = DatabaseManager()
                print("✅ Nueva base de datos inicializada")
            else:
                print("ℹ️  No hay base de datos para eliminar")
        except Exception as e:
            print(f"❌ Error al eliminar base de datos: {e}")
    else:
        print("❌ Operación cancelada")

def show_current_stats():
    """Muestra estadísticas actuales de la base de datos"""
    try:
        if not os.path.exists("chatbot.db"):
            print("ℹ️  No hay base de datos existente")
            return
            
        db = DatabaseManager()
        sessions = db.get_all_sessions()
        
        print("\n📊 ESTADÍSTICAS ACTUALES:")
        print(f"Total de sesiones: {len(sessions)}")
        
        total_messages = 0
        total_tokens = 0
        
        for session in sessions:
            stats = db.get_session_stats(session['session_id'])
            total_messages += stats.get('total_messages', 0)
            total_tokens += stats.get('total_tokens', 0)
            
            print(f"\n🔹 Sesión: {session['session_id'][:8]}...")
            print(f"   Mensajes: {stats.get('total_messages', 0)}")
            print(f"   Tokens: {stats.get('total_tokens', 0)}")
            print(f"   Última actividad: {session['last_activity']}")
        
        print(f"\n📈 TOTALES:")
        print(f"Mensajes totales: {total_messages}")
        print(f"Tokens totales: {total_tokens}")
        
    except Exception as e:
        print(f"❌ Error al obtener estadísticas: {e}")

def create_backup():
    """Crea un backup antes de limpiar"""
    try:
        if not os.path.exists("chatbot.db"):
            print("ℹ️  No hay base de datos para respaldar")
            return False
            
        db = DatabaseManager()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"backup_before_cleanup_{timestamp}.db"
        
        success = db.backup_database(backup_name)
        if success:
            print(f"✅ Backup creado: {backup_name}")
            return True
        else:
            print("❌ Error al crear backup")
            return False
    except Exception as e:
        print(f"❌ Error al crear backup: {e}")
        return False

def clear_specific_sessions():
    """Permite limpiar sesiones específicas"""
    try:
        if not os.path.exists("chatbot.db"):
            print("ℹ️  No hay base de datos existente")
            return
            
        db = DatabaseManager()
        sessions = db.get_all_sessions()
        
        if not sessions:
            print("ℹ️  No hay sesiones para limpiar")
            return
        
        print("\n📋 SESIONES DISPONIBLES:")
        for i, session in enumerate(sessions, 1):
            stats = db.get_session_stats(session['session_id'])
            print(f"{i}. {session['session_id'][:8]}... "
                  f"({stats.get('total_messages', 0)} mensajes, "
                  f"{session['last_activity']})")
        
        print(f"{len(sessions) + 1}. 🗑️  Eliminar TODAS las sesiones")
        
        try:
            choice = int(input("\nSelecciona el número de sesión a limpiar: "))
            
            if choice == len(sessions) + 1:
                # Eliminar todas las sesiones
                confirm = input("⚠️  ¿Eliminar TODAS las sesiones? (s/N): ")
                if confirm.lower() in ['s', 'si', 'sí']:
                    for session in sessions:
                        db.clear_session(session['session_id'])
                    print("✅ Todas las sesiones limpiadas")
                else:
                    print("❌ Operación cancelada")
            elif 1 <= choice <= len(sessions):
                # Eliminar sesión específica
                session_to_clear = sessions[choice - 1]
                success = db.clear_session(session_to_clear['session_id'])
                if success:
                    print(f"✅ Sesión {session_to_clear['session_id'][:8]}... limpiada")
                else:
                    print("❌ Error al limpiar sesión")
            else:
                print("❌ Opción no válida")
                
        except ValueError:
            print("❌ Por favor ingresa un número válido")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def reset_current_session():
    """Resetea solo la sesión actual (simulada)"""
    print("\n🔄 Para resetear tu sesión actual:")
    print("1. Ve al navegador web")
    print("2. Haz clic en el botón 'Limpiar' en la interfaz")
    print("3. O cierra y abre una nueva pestaña/ventana")
    print("\nEsto creará una nueva sesión limpia manteniendo el historial anterior.")

def main():
    """Función principal"""
    while True:
        show_menu()
        
        try:
            choice = input("Selecciona una opción (1-6): ").strip()
            
            if choice == "1":
                clear_all_database()
            elif choice == "2":
                clear_specific_sessions()
            elif choice == "3":
                show_current_stats()
            elif choice == "4":
                create_backup()
            elif choice == "5":
                reset_current_session()
            elif choice == "6":
                print("👋 ¡Hasta luego!")
                break
            else:
                print("❌ Opción no válida. Por favor selecciona 1-6.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Operación cancelada por el usuario")
            break
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
        
        input("\nPresiona Enter para continuar...")

if __name__ == "__main__":
    main()
