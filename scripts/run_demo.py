"""
run_demo.py - Ejecutar servidor en modo demo local
Útil para probar UI, botones y funcionalidad sin configuración externa
"""
import os
import sys
import time
import threading
import subprocess
from pathlib import Path

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    print("""
╔════════════════════════════════════════════════════════════════╗
║              CALLMANAGER - MODO DEMO LOCAL                    ║
║                      Test UI & Features                       ║
╚════════════════════════════════════════════════════════════════╝
    """)

def generate_demo_data():
    """Generar datos de prueba"""
    print("📊 Generando contactos de prueba...")
    try:
        exec(open('demo_contacts.py').read())
        print("   ✅ Contactos generados\n")
    except Exception as e:
        print(f"   ⚠️ No se generaron contactos: {e}\n")

def start_server():
    """Iniciar servidor en background"""
    print("🚀 Iniciando servidor Flask...")
    try:
        import server
        from flask_socketio import SocketIO
        print("   ✅ Servidor iniciando en http://127.0.0.1:5000\n")
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}\n")
        return False

def print_usage():
    """Imprimir instrucciones"""
    print("""
📋 INSTRUCCIONES PARA DEMO
──────────────────────────────────────────────────────────────

1. SERVIDOR (ya está corriendo)
   ✅ Escucha en: http://127.0.0.1:5000
   ✅ Base de datos: contacts.db
   ✅ API Key: dev-key-change-in-production

2. CLIENTE (ejecuta en otra terminal)
   Windows:
     cd c:/Users/bjorg/OneDrive/Desktop/callmanager/client
     python call_manager_app.py
   
   El cliente se conectará automáticamente a localhost:5000

3. PRUEBAS QUE PUEDES HACER
   
   ✅ TEST 1: Conexión
      - Inicia el cliente
      - Debería mostrar "Socket.IO: Conectado" en Estado
      - Verifica que se carga la lista de contactos

   ✅ TEST 2: Importar contactos
      - Haz clic en 📥 Importar Excel
      - Selecciona demo_contacts.csv o cualquier Excel
      - Verifica que aparecen en la lista
      - Intenta importar 2 veces el mismo archivo (prueba duplicados)

   ✅ TEST 3: UI y botones
      - Haz clic en 🔄 Refrescar
      - Verifica que los contactos se recargan
      - Haz clic en ℹ️ Estado (debe mostrar información)
      - Verifica que NO hay botones superpuestos

   ✅ TEST 4: Llamar (InterPhone)
      - Haz clic en 📞 Llamar en algún contacto
      - Si InterPhone no está instalado, debe mostrar error claro
      - Si está instalado, debe intentar marcar

   ✅ TEST 5: Bloquear contactos
      - Haz clic en 🔒 Bloquear
      - Debe cambiar a 🔓 Desbloquear
      - En otra pestaña del cliente, debe verse bloqueado

4. ARCHIVOS DE PRUEBA
   
   ✅ demo_contacts.csv - 15 contactos de prueba
   ✅ demo_contacts.json - Same data in JSON
   ✅ contacts.db - Base de datos local (se crea automáticamente)

5. LOGS Y DEBUGGING
   
   ✅ Servidor: Ver consola del servidor
   ✅ Cliente: Ver consola del cliente
   ✅ Base: callmanager.log - logs detallados

6. LIMPIAR Y REINICIAR
   
   Para eliminar datos de demo:
     - Cierra el servidor (Ctrl+C)
     - Elimina: contacts.db
     - Reinicia: python server.py

═══════════════════════════════════════════════════════════════
    """)

def main():
    clear_screen()
    print_header()
    
    # Paso 1: Generar datos
    generate_demo_data()
    
    # Paso 2: Imprimir instrucciones
    print_usage()
    
    # Paso 3: Mensaje final
    print("""
🎯 PRÓXIMOS PASOS
──────────────────────────────────────────────────────────────

1. Abre OTRA terminal (no cierres esta)
   Windows:
     cd c:/Users/bjorg/OneDrive/Desktop/callmanager/client
     python call_manager_app.py

2. La app debería conectar automáticamente a localhost:5000

3. Prueba todas las funciones:
   ✓ Importar contactos
   ✓ Refrescar
   ✓ Ver estado
   ✓ Intentar marcar
   ✓ Bloquear contactos

4. Verifica en esta consola que NO hay errores

═══════════════════════════════════════════════════════════════

⏸️  Presiona Ctrl+C para detener el servidor

    """)
    
    # Paso 4: Iniciar servidor
    print("Iniciando servidor...")
    print("─" * 60)
    try:
        # Import y run server
        sys.path.insert(0, str(Path(__file__).parent))
        import server
        
        # El servidor se inicia aquí
        # (No retorna hasta que se cierre)
        
    except KeyboardInterrupt:
        print("\n\n✅ Servidor detenido")
        print("Para reiniciar: python run_demo.py")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Verifica que todos los archivos estén presentes")

if __name__ == '__main__':
    main()
