#!/usr/bin/env python3
"""
build_executable.py - Construir ejecutable con PyInstaller
Genera un EXE que puede actualizar su código desde un repositorio o servidor
"""

import os
import sys
import json
import subprocess
import shutil
from pathlib import Path
from datetime import datetime

def install_pyinstaller():
    """Instalar PyInstaller si no está disponible"""
    try:
        import PyInstaller
        print("✅ PyInstaller ya está instalado")
    except ImportError:
        print("📦 Instalando PyInstaller...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyinstaller'])
        print("✅ PyInstaller instalado")

def create_updater_script():
    """Crear script de actualización que se incrusta en el EXE"""
    updater_code = '''
import os
import sys
import json
import subprocess
from pathlib import Path

def check_for_updates(build_info_path='build_info.json'):
    """Verificar si hay actualizaciones disponibles"""
    try:
        with open(build_info_path, 'r') as f:
            build_info = json.load(f)
        
        if not build_info.get('auto_update'):
            return False
        
        # Aquí puedes agregar lógica de actualización
        # Ejemplo: descargar de GitHub o servidor privado
        return True
    except:
        return False

def update_from_git():
    """Actualizar código desde repositorio git"""
    try:
        # Stash cambios locales
        subprocess.run(['git', 'stash'], check=False)
        
        # Pull últimos cambios
        subprocess.run(['git', 'pull', 'origin', 'main'], check=True)
        
        # Instalar dependencias actualizadas
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], check=True)
        
        return True
    except Exception as e:
        print(f"Error updating: {e}")
        return False

def restart_application():
    """Reiniciar la aplicación después de actualizar"""
    # Ejecutar el mismo EXE nuevamente
    os.execl(sys.executable, sys.executable, *sys.argv)
'''
    
    with open('updater.py', 'w', encoding='utf-8') as f:
        f.write(updater_code)
    
    print("✅ Script de actualización creado: updater.py")

def create_pyinstaller_spec():
    """Crear archivo spec personalizado para PyInstaller"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

block_cipher = None

a = Analysis(
    ['client/call_manager_app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('phone_generator.py', '.'),
        ('config.py', '.'),
        ('config_loader.py', 'client'),
        ('build_info.json', '.'),
        ('.env.example', '.'),
    ],
    hiddenimports=[
        'customtkinter',
        'socketio',
        'pandas',
        'openpyxl',
        'sqlalchemy',
        'flask',
        'eventlet',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludedimports=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='CallManager',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # True para modo consola, False para GUI
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
'''
    
    with open('CallManager.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("✅ Archivo spec creado: CallManager.spec")

def build_exe():
    """Construir ejecutable con PyInstaller"""
    print("\n🔨 Construyendo ejecutable...")
    
    try:
        # Ejecutar PyInstaller
        subprocess.check_call([
            sys.executable, '-m', 'PyInstaller',
            '--onefile',  # Un archivo único
            '--icon=callmanager.ico',  # Icono (si existe)
            '--name=CallManager',
            '--version-file=version.txt',  # Info de versión (si existe)
            'CallManager.spec'
        ])
        
        print("✅ Ejecutable construido en: dist/CallManager.exe")
        
        # Crear zip con datos necesarios
        create_distribution_package()
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error durante la construcción: {e}")
        sys.exit(1)

def create_distribution_package():
    """Crear paquete de distribución con EXE + archivos necesarios"""
    dist_dir = Path('dist')
    
    # Crear carpeta CallManager en dist
    callmanager_dir = dist_dir / 'CallManager'
    callmanager_dir.mkdir(exist_ok=True)
    
    # Copiar archivos necesarios
    files_to_copy = [
        '.env.example',
        'build_info.json',
        'requirements.txt',
        'README.md',
    ]
    
    for file in files_to_copy:
        src = Path(file)
        if src.exists():
            shutil.copy(src, callmanager_dir / file)
            print(f"  ✓ Copiado: {file}")
    
    # Crear archivo de instalación
    installer_code = '''@echo off
REM CallManager Installer
REM Instala dependencias y crea .env

echo ========== CallManager Installer ==========
echo.

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no encontrado. Instala Python 3.7+
    pause
    exit /b 1
)

echo [1/3] Instalando dependencias...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Fallo al instalar dependencias
    pause
    exit /b 1
)

echo [2/3] Generando configuración segura...
python setup_secure.py
if errorlevel 1 (
    echo ERROR: Fallo al generar .env
    pause
    exit /b 1
)

echo [3/3] Iniciando CallManager...
python CallManager.exe

pause
'''
    
    with open(callmanager_dir / 'install.bat', 'w', encoding='utf-8') as f:
        f.write(installer_code)
    
    print(f"\n✅ Paquete de distribución creado en: {callmanager_dir}")
    print(f"   - CallManager.exe")
    print(f"   - .env.example")
    print(f"   - requirements.txt")
    print(f"   - install.bat")

def create_version_file():
    """Crear archivo de versión para Windows"""
    version_content = '''# UTF-8
#
# For more details about fixed file info 'ffi' see:
# http://msdn.microsoft.com/en-us/library/ms646997.aspx?id=7
VSVersionInfo(
  ffi=FixedFileInfo(
    # Contains all your app constants
    mask=0x3f,
    mask2=0x3f,
    # Contains a bitmask that specifies the valid bits 'flags'r
    strFileInfo=(
      # Contains a list of StringFileInfo blocks, each describing a language/codepage
      # pair that contains version information
      ('StringFileInfo',
        [('040904B0',
        # Contains the following 16 strings, all optional
        OrderedDict([(u'CompanyName', u'CallManager Team'),
        (u'FileDescription', u'CallManager - Sistema de Gestión de Contactos'),
        (u'FileVersion', u'3.3.1.0'),
        (u'InternalName', u'CallManager'),
        (u'LegalCopyright', u'Copyright (C) 2024'),
        (u'OriginalFilename', u'CallManager.exe'),
        (u'ProductName', u'CallManager'),
        (u'ProductVersion', u'3.3.1.0')]))]),
      # Contains the following 4 entries, all optional
      ('VarFileInfo', [('Translation', [1033, 1200])])
  )
)
'''
    
    with open('version.txt', 'w', encoding='utf-8') as f:
        f.write(version_content)
    
    print("✅ Archivo de versión creado: version.txt")

def build_info_for_updates():
    """Crear información de build para actualizaciones"""
    build_info = {
        'app_name': 'CallManager',
        'version': '3.3.1',
        'build_date': datetime.now().isoformat(),
        'auto_update': True,
        'update_check_interval_hours': 24,
        'repository': 'https://github.com/JorgeBC420/callmanager',
        'update_url': 'https://your-update-server.com/api/check-updates',
        'features': [
            'phone_generator',
            'contact_management',
            'excel_import_export',
            'role_based_access',
            'real_time_sync'
        ],
        'minimum_python_version': '3.7.0'
    }
    
    with open('build_info.json', 'w', encoding='utf-8') as f:
        json.dump(build_info, f, indent=2)
    
    print("✅ Información de build actualizada: build_info.json")

def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║        CallManager - Constructor de Ejecutable               ║
║            PyInstaller + Auto-Update                         ║
║                   v3.3.1                                     ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Cambiar al directorio del script
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    try:
        # 1. Instalar PyInstaller
        print("\n[1/5] Verificando PyInstaller...")
        install_pyinstaller()
        
        # 2. Crear archivos necesarios
        print("\n[2/5] Creando archivos de configuración...")
        create_pyinstaller_spec()
        create_version_file()
        create_updater_script()
        
        # 3. Actualizar build_info
        print("\n[3/5] Actualizando información de build...")
        build_info_for_updates()
        
        # 4. Construir EXE
        print("\n[4/5] Construyendo ejecutable...")
        build_exe()
        
        # 5. Instrucciones finales
        print("""
╔══════════════════════════════════════════════════════════════╗
║              ✅ CONSTRUCCIÓN COMPLETADA                      ║
╚══════════════════════════════════════════════════════════════╝

Archivo generado:
  📦 dist/CallManager/CallManager.exe

Cómo usar:
  1. Distribuu el contenido de dist/CallManager/
  2. Los usuarios ejecutan install.bat primero
  3. Luego ejecutan CallManager.exe

Características:
  ✅ Autoactualización desde Git
  ✅ Configuración segura (.env)
  ✅ Todas las dependencias incluidas
  ✅ Icono y versión de Windows
  
Próximos pasos:
  1. Configurar servidor de actualizaciones (opcional)
  2. Crear instalador NSIS (opcional)
  3. Publicar en servidor seguro
        """)
        
    except Exception as e:
        print(f"\n❌ Error durante la construcción: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
