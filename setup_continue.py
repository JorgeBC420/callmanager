#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Setup script para configurar Continue con Ollama
"""

import os
import shutil
import sys
from pathlib import Path

def setup_continue_config():
    """Copiar configuración de Continue a la carpeta correcta"""
    
    # Directorio de Continue
    continue_dir = Path.home() / ".continue"
    config_file = continue_dir / "config.yaml"
    
    # Archivo local de configuración
    local_config = Path(__file__).parent / ".continue_config.yaml"
    
    print(f"📁 Directorio Continue: {continue_dir}")
    print(f"📄 Configuración local: {local_config}")
    
    # Crear directorio si no existe
    continue_dir.mkdir(exist_ok=True)
    print(f"✓ Directorio creado/verificado")
    
    # Copiar archivo
    try:
        if local_config.exists():
            shutil.copy2(local_config, config_file)
            print(f"✅ Configuración copiada a: {config_file}")
        else:
            print(f"❌ Archivo local no encontrado: {local_config}")
            return False
            
    except Exception as e:
        print(f"❌ Error al copiar: {e}")
        return False
    
    # Verificar que se copió correctamente
    if config_file.exists():
        print(f"✅ Verificación OK - Archivo existe")
        with open(config_file, 'r', encoding='utf-8') as f:
            print(f"\n📋 Contenido de configuración:")
            print(f.read())
        return True
    else:
        print(f"❌ Verificación FALLIDA - Archivo no existe")
        return False

def check_ollama():
    """Verificar si Ollama está disponible"""
    print("\n" + "="*60)
    print("VERIFICAR OLLAMA")
    print("="*60)
    
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            print("✅ Ollama está ejecutándose en localhost:11434")
            models = response.json().get("models", [])
            print(f"\n📦 Modelos disponibles ({len(models)}):")
            for model in models:
                print(f"   • {model.get('name')}")
            return True
        else:
            print(f"❌ Error HTTP {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Ollama no está ejecutándose en localhost:11434")
        print("\n💡 Para iniciar Ollama, ejecuta:")
        print("   ollama serve")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("SETUP CONTINUE + OLLAMA")
    print("="*60)
    
    # Setup de configuración
    if setup_continue_config():
        print("\n✅ Configuración de Continue lista")
    else:
        print("\n❌ Error en configuración de Continue")
        sys.exit(1)
    
    # Verificar Ollama
    if not check_ollama():
        print("\n⚠️  IMPORTANTE: Ollama no está ejecutándose")
        print("   Inicia Ollama con: ollama serve")
    
    print("\n" + "="*60)
    print("✅ SETUP COMPLETADO")
    print("="*60)
    print("\n📝 Próximos pasos:")
    print("   1. Asegúrate de que Ollama esté ejecutándose: ollama serve")
    print("   2. Abre VS Code")
    print("   3. Presiona Ctrl+Shift+C para abrir Continue")
    print("   4. Selecciona uno de los modelos Ollama disponibles")
