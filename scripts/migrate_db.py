#!/usr/bin/env python3
"""
migrate_db.py - Migrar base de datos para agregar columna password_hash
"""

import sqlite3
import os
from pathlib import Path

DB_PATH = Path(__file__).parent / "callmanager.db"

def migrate_database():
    """Agregar columna password_hash a tabla users"""
    
    if not DB_PATH.exists():
        print(f"❌ Base de datos no encontrada: {DB_PATH}")
        print("   Se creará una nueva BD en el próximo inicio del servidor")
        return False
    
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    try:
        # Verificar si la columna ya existe
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'password_hash' in columns:
            print("✅ Columna password_hash ya existe")
            return True
        
        print("🔄 Migrando base de datos...")
        
        # Agregar columna con valor por defecto vacío
        # (los usuarios existentes no tendrán contraseña, pero podrán usar API Key)
        cursor.execute("""
            ALTER TABLE users 
            ADD COLUMN password_hash TEXT DEFAULT ''
        """)
        
        conn.commit()
        print("✅ Columna password_hash agregada exitosamente")
        
        # Mostrar estructura actualizada
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        print("\n📋 Estructura actualizada de tabla users:")
        for col in columns:
            col_id, col_name, col_type, not_null, default, pk = col
            nullable = "✓ NULL" if not not_null else "NOT NULL"
            print(f"   {col_name:20} {col_type:15} {nullable}")
        
        return True
        
    except sqlite3.OperationalError as e:
        if "already exists" in str(e):
            print("✅ Columna password_hash ya existe")
            return True
        else:
            print(f"❌ Error en migración: {e}")
            return False
    finally:
        conn.close()

def reset_database():
    """Borrar BD completamente para reiniciar desde cero"""
    
    if DB_PATH.exists():
        try:
            os.remove(DB_PATH)
            print(f"✅ Base de datos eliminada: {DB_PATH}")
            
            # También eliminar archivo de WAL si existe
            wal_file = Path(str(DB_PATH) + "-wal")
            shm_file = Path(str(DB_PATH) + "-shm")
            
            if wal_file.exists():
                os.remove(wal_file)
                print(f"✅ Archivo WAL eliminado")
            
            if shm_file.exists():
                os.remove(shm_file)
                print(f"✅ Archivo SHM eliminado")
                
            print("\n✅ Se creará una nueva BD con estructura completa en el próximo inicio")
            return True
        except Exception as e:
            print(f"❌ Error al eliminar BD: {e}")
            return False
    else:
        print("ℹ️  Base de datos no existe, se creará en el próximo inicio")
        return True

if __name__ == "__main__":
    import sys
    
    print("""
╔════════════════════════════════════════════════════════════╗
║              HERRAMIENTA DE MIGRACIÓN DE BD               ║
║                  CallManager v3.3.1                        ║
╚════════════════════════════════════════════════════════════╝
""")
    
    print(f"Base de datos: {DB_PATH}")
    print(f"Existe: {'✅ Sí' if DB_PATH.exists() else '❌ No'}\n")
    
    if len(sys.argv) > 1 and sys.argv[1] == "--reset":
        print("⚠️  ADVERTENCIA: Esto borrará TODA la base de datos")
        confirm = input("¿Deseas continuar? (escribe 'SI' para confirmar): ")
        if confirm.upper() == "SI":
            reset_database()
        else:
            print("Operación cancelada")
    else:
        # Intentar migración normal
        if migrate_database():
            print("\n✅ Migración completada exitosamente")
        else:
            print("\n⚠️  Migración falló. Considera usar: python migrate_db.py --reset")
    
    print("""
Próximos pasos:
1. Ejecutar: python server.py
2. El servidor creará el usuario admin/1234 si no existe
3. Probar login con las nuevas credenciales
    """)
