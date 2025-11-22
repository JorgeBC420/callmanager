"""
Configuración Inicial del Sistema - CallManager
Inicialización de todos los componentes: Chat IA, Grabación, UI Responsiva

Autor: CallManager System
Versión: 2.0
Fecha: 2025-11-22
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def check_ollama_installed() -> bool:
    """Verificar si Ollama está instalado"""
    try:
        result = subprocess.run(
            ['ollama', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except:
        return False


def check_ollama_running() -> bool:
    """Verificar si Ollama está ejecutándose"""
    try:
        import requests
        response = requests.get(
            'http://localhost:11434/api/tags',
            timeout=2
        )
        return response.status_code == 200
    except:
        return False


def install_ollama():
    """Instrucciones para instalar Ollama"""
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║          INSTALAR OLLAMA PARA CHAT IA                      ║
    ╚════════════════════════════════════════════════════════════╝
    
    1. Descargar Ollama:
       👉 https://ollama.ai/
    
    2. Después de instalar, ejecutar modelo:
       $ ollama pull mistral
    
    3. Mantener Ollama ejecutándose en otra terminal:
       $ ollama serve
    
    4. Verificar que esté disponible en:
       http://localhost:11434/api/tags
    
    El Chat IA funcionará automáticamente una vez Ollama esté activo.
    """)


def verify_dependencies():
    """Verificar todas las dependencias"""
    print("\n╔════════════════════════════════════════════════════════════╗")
    print("║         VERIFICACIÓN DE DEPENDENCIAS                      ║")
    print("╚════════════════════════════════════════════════════════════╝\n")
    
    # Verificar Python packages
    required_packages = [
        'customtkinter',
        'requests',
        'pyaudio',
        'openpyxl',
        'socketio',
        'flask',
        'sqlalchemy'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Instalar packages faltantes:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False
    
    print("\n✅ Todos los packages están instalados\n")
    
    # Verificar Ollama
    print("Verificando Ollama para Chat IA...")
    
    if check_ollama_installed():
        print("✅ Ollama instalado")
        
        if check_ollama_running():
            print("✅ Ollama ejecutándose")
        else:
            print("⚠️  Ollama instalado pero NO está ejecutándose")
            print("   Ejecutar en otra terminal: ollama serve")
    else:
        print("⚠️  Ollama NO está instalado")
        install_ollama()
    
    # Verificar directorios
    print("\nVerificando directorios...")
    
    directories = [
        'recordings',
        'client/ui',
        'backups'
    ]
    
    for directory in directories:
        path = Path(directory)
        path.mkdir(parents=True, exist_ok=True)
        print(f"✅ {directory}")
    
    return True


def create_initialization_file():
    """Crear archivo de inicialización para la app"""
    
    init_code = '''"""
Inicializador de CallManager con Nuevos Componentes
Ejecutar una sola vez al inicio
"""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def initialize_all_systems():
    """Inicializar todos los sistemas"""
    
    # Crear directorios necesarios
    Path("recordings").mkdir(exist_ok=True)
    Path("backups").mkdir(exist_ok=True)
    
    # Inicializar Chat IA
    try:
        from chat_assistant import initialize_chat_assistant
        chat = initialize_chat_assistant()
        logger.info("✅ Chat Assistant inicializado")
    except Exception as e:
        logger.warning(f"⚠️ Chat Assistant error: {e}")
    
    # Inicializar Grabador
    try:
        from call_recorder import initialize_call_recorder
        recorder = initialize_call_recorder("recordings")
        logger.info("✅ Call Recorder inicializado")
    except Exception as e:
        logger.warning(f"⚠️ Call Recorder error: {e}")
    
    # Inicializar Tracking
    try:
        from call_tracking import initialize_tracker
        tracker = initialize_tracker()
        logger.info("✅ Call Tracker inicializado")
    except Exception as e:
        logger.warning(f"⚠️ Call Tracker error: {e}")
    
    logger.info("✨ Sistema inicializado correctamente")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    initialize_all_systems()
'''
    
    with open('client/system_init.py', 'w', encoding='utf-8') as f:
        f.write(init_code)
    
    print("✅ Archivo de inicialización creado: client/system_init.py")


def setup_ui_files():
    """Verificar que los archivos de UI existan"""
    
    ui_files = [
        'client/ui/chat_widget.py',
        'client/ui/responsive_ui.py',
        'client/ui/metrics_dashboard.py'
    ]
    
    for file in ui_files:
        if Path(file).exists():
            print(f"✅ {file}")
        else:
            print(f"⚠️  Falta {file}")


def print_welcome_banner():
    """Banner de bienvenida"""
    banner = """
    
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║        🎉 CALLMANAGER v2.5 - CONFIGURACIÓN COMPLETA 🎉       ║
║                                                               ║
║  Nueva Funcionalidad Agregada:                               ║
║  ✅ Chat IA con Ollama - Manejo de Objeciones                ║
║  ✅ Grabación Automática de Llamadas                         ║
║  ✅ UI Responsiva (Móviles, Tablets, Desktop)                ║
║  ✅ Exportación a Excel                                      ║
║  ✅ Atajos de Teclado                                        ║
║  ✅ Editor Inline de Contactos                               ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
    
    """
    print(banner)


def print_next_steps():
    """Pasos siguientes"""
    steps = """
╔═══════════════════════════════════════════════════════════════╗
║                    PASOS SIGUIENTES                          ║
╚═══════════════════════════════════════════════════════════════╝

1️⃣  INSTALAR DEPENDENCIAS:
    cd callmanager
    pip install -r requirements.txt

2️⃣  INSTALAR OLLAMA (para Chat IA):
    - Ir a: https://ollama.ai/
    - Descargar e instalar
    - Ejecutar: ollama pull mistral

3️⃣  EJECUTAR OLLAMA EN OTRA TERMINAL:
    ollama serve

4️⃣  INICIALIZAR SISTEMA:
    cd client
    python system_init.py

5️⃣  EJECUTAR APLICACIÓN:
    python call_manager_app.py

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 NUEVOS ATAJOS DE TECLADO:
    
    Ctrl+N   → Nuevo contacto
    Ctrl+E   → Exportar a Excel
    Ctrl+F   → Buscar
    Ctrl+C   → Llamar
    Ctrl+A   → Abrir Chat IA
    F2       → Editar contacto
    Delete   → Eliminar contacto
    Escape   → Cancelar

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 CARACTERÍSTICAS:

1. CHAT IA PARA OBJECIONES:
   - Haz Ctrl+A durante una llamada
   - Pregunta al IA cómo responder objeciones
   - Sugerencias de argumentos de venta

2. GRABACIÓN DE LLAMADAS:
   - Grabación automática al hacer llamadas
   - Metadatos guardados automáticamente
   - Exportar grabaciones a Excel

3. UI RESPONSIVA:
   - Funciona en tablets y celulares
   - Editor inline de contactos
   - Notas limitadas a 244 caracteres
   - Exportación a Excel desde cualquier lugar

4. MÉTRICAS MEJORADAS:
   - Duración de llamadas en tiempo real
   - Dashboard con KPIs
   - Historial de llamadas

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📚 DOCUMENTACIÓN:
    
    Ver: INTEGRACION_NUEVOS_COMPONENTES.md
         SISTEMA_RASTREO_TIEMPO_COMPLETO.md
         DEMO.md

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

¿Preguntas o problemas? Revisa los archivos de documentación.

    """
    print(steps)


def main():
    """Función principal"""
    print_welcome_banner()
    
    # Verificar dependencias
    if not verify_dependencies():
        print("\n❌ Por favor instala las dependencias faltantes")
        return False
    
    # Crear archivo de inicialización
    create_initialization_file()
    
    # Verificar UI files
    print("\nVerificando archivos de UI...")
    setup_ui_files()
    
    # Imprimir pasos siguientes
    print_next_steps()
    
    return True


if __name__ == "__main__":
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    success = main()
    sys.exit(0 if success else 1)
