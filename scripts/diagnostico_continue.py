#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Diagnostic script para Continue + Ollama
"""

import json
import sys
from pathlib import Path

def check_config():
    """Revisar la configuración de Continue"""
    print("=" * 60)
    print("VERIFICACIÓN DE CONFIGURACIÓN")
    print("=" * 60)
    
    config_path = Path.home() / ".continue" / "config.yaml"
    
    if not config_path.exists():
        print(f"❌ No encontrado: {config_path}")
        return False
    
    print(f"✅ Encontrado: {config_path}")
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Contar modelos
        models_count = content.count('provider: "ollama"')
        print(f"📦 Modelos configurados: {models_count}")
        
        # Verificar apiBase
        if 'http://localhost:11434' in content:
            print(f"✅ apiBase configurado correctamente")
        else:
            print(f"❌ apiBase no encontrado o incorrecto")
            
        return True
        
    except Exception as e:
        print(f"❌ Error al leer config: {e}")
        return False

def check_continue_extension():
    """Revisar si Continue está instalada"""
    print("\n" + "=" * 60)
    print("VERIFICACIÓN DE EXTENSIÓN CONTINUE")
    print("=" * 60)
    
    # VS Code extensions están en el USERPROFILE
    extensions_path = Path.home() / ".vscode" / "extensions"
    
    if not extensions_path.exists():
        print("❌ Directorio .vscode/extensions no encontrado")
        return False
    
    # Buscar extensión de Continue
    continue_extensions = []
    for ext_dir in extensions_path.iterdir():
        if 'continue' in ext_dir.name.lower():
            continue_extensions.append(ext_dir.name)
    
    if continue_extensions:
        print(f"✅ Continue instalado:")
        for ext in continue_extensions:
            print(f"   • {ext}")
        return True
    else:
        print("❌ Continue no encontrado en extensiones")
        print("\n💡 Para instalar Continue:")
        print("   1. Abre VS Code")
        print("   2. Ctrl+Shift+X (Extensions)")
        print("   3. Busca: 'Continue'")
        print("   4. Instala 'Continue - Coding with AI'")
        return False

def check_ollama_models():
    """Verificar qué modelos Ollama tiene"""
    print("\n" + "=" * 60)
    print("VERIFICACIÓN DE MODELOS OLLAMA")
    print("=" * 60)
    
    try:
        import requests
    except ImportError:
        print("⚠️  requests no instalado, saltando verificación de Ollama")
        return None
    
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        
        if response.status_code == 200:
            models = response.json().get("models", [])
            print(f"✅ Ollama conectado (localhost:11434)")
            print(f"� Modelos disponibles ({len(models)}):")
            
            required_models = [
                'deepseek-v3',
                'deepseek-r1',
                'llama3.2-11b',
                'gpt-oss-120b'
            ]
            
            found_models = [m.get('name', '') for m in models]
            
            for model in required_models:
                if any(model in fm for fm in found_models):
                    print(f"   ✅ {model}")
                else:
                    print(f"   ❌ {model} (no instalado)")
            
            return True
            
    except requests.exceptions.ConnectionError:
        print("❌ Ollama no está ejecutándose")
        print("\n💡 Para iniciar Ollama:")
        print("   ollama serve")
        return False
    except Exception as e:
        print(f"⚠️  Error: {e}")
        return None

def check_firewall():
    """Verificar configuración de firewall"""
    print("\n" + "=" * 60)
    print("VERIFICACIÓN DE FIREWALL")
    print("=" * 60)
    
    print("⚠️  Verificar manualmente:")
    print("   1. Control Panel → Windows Defender Firewall")
    print("   2. Allow an app through firewall")
    print("   3. Busca 'python.exe'")
    print("   4. Asegúrate que 'Private' está checkeado")

if __name__ == "__main__":
    results = {
        'config': check_config(),
        'extension': check_continue_extension(),
        'ollama': check_ollama_models(),
    }
    
    print("\n" + "=" * 60)
    print("RESUMEN")
    print("=" * 60)
    
    if all(v is True for v in results.values()):
        print("✅ TODO BIEN - Continue está listo para usar")
        print("\n🚀 Pasos siguientes:")
        print("   1. Abre VS Code")
        print("   2. Presiona Ctrl+Shift+C (Continue Chat)")
        print("   3. ¡Empieza a chatear con IA offline!")
    else:
        print("❌ Hay algunos problemas a resolver")
        print("\nProblemas encontrados:")
        for key, value in results.items():
            if value is False:
                print(f"   • {key}")
