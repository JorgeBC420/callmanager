#!/usr/bin/env python3
"""
setup_secure.py - Script de configuración segura para CallManager
Genera claves seguras, crea .env, valida permisos de archivo
"""

import os
import sys
import secrets
import json
from pathlib import Path

def generate_secure_key(length=32):
    """Generar una clave criptográfica segura"""
    return secrets.token_urlsafe(length)

def setup_env():
    """Crear archivo .env seguro con claves generadas"""
    env_file = Path('.env')
    example_file = Path('.env.example')
    
    if env_file.exists():
        print(f"⚠️  {env_file} ya existe. Respaldando como {env_file}.backup")
        env_file.rename(f'{env_file}.backup')
    
    # Generar claves seguras
    api_key = generate_secure_key(32)
    secret_key = generate_secure_key(32)
    
    # Leer template de .env.example
    if example_file.exists():
        with open(example_file, 'r', encoding='utf-8') as f:
            env_content = f.read()
    else:
        env_content = ""
    
    # Reemplazar valores por defecto con valores seguros
    env_content = env_content.replace(
        'CALLMANAGER_API_KEY=dev-key-change-in-production',
        f'CALLMANAGER_API_KEY={api_key}'
    )
    env_content = env_content.replace(
        'CALLMANAGER_SECRET_KEY=dev-secret-change-in-production',
        f'CALLMANAGER_SECRET_KEY={secret_key}'
    )
    env_content = env_content.replace(
        'FLASK_ENV=production',
        'FLASK_ENV=production'
    )
    
    # Crear .env con permisos restrictivos
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    # En Windows, no hay chmod. En Unix/Linux:
    if hasattr(os, 'chmod'):
        os.chmod(env_file, 0o600)  # Solo lectura/escritura para el propietario
        print(f"✅ Permisos de archivo .env establecidos (600)")
    
    print(f"✅ Archivo .env creado con claves seguras generadas")
    print(f"   - API Key: {api_key[:16]}...")
    print(f"   - Secret Key: {secret_key[:16]}...")
    print(f"\n⚠️  IMPORTANTE: Guarda estas claves en un lugar seguro")
    print(f"   No compartas el archivo .env ni estas claves")
    
    return api_key, secret_key

def create_build_info():
    """Crear archivo build_info.json para tracking de versión"""
    build_info = {
        'version': '3.3.1',
        'build_type': 'distribution',
        'auto_update': True,
        'update_url': 'https://your-update-server.com/updates'
    }
    
    with open('build_info.json', 'w', encoding='utf-8') as f:
        json.dump(build_info, f, indent=2)
    
    print(f"✅ build_info.json creado")

def validate_security():
    """Validar que no haya credenciales en el código"""
    print("\n🔍 Validando seguridad...")
    
    danger_patterns = [
        'PASSWORD = "',
        'API_KEY = "',
        'SECRET = "',
        'apikey="',
        'password="',
        'token="'
    ]
    
    for file in Path('.').glob('*.py'):
        with open(file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            for pattern in danger_patterns:
                if pattern in content.lower():
                    print(f"⚠️  ADVERTENCIA: Posible credencial hardcodeada en {file}")
                    # Buscar la línea exacta
                    for i, line in enumerate(content.split('\n'), 1):
                        if pattern.lower() in line.lower():
                            print(f"   Línea {i}: {line.strip()}")
    
    print("✅ Validación de seguridad completada")

def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║           CallManager - Configuración Segura                ║
║                   v3.3.1                                     ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Cambiar al directorio del script
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    try:
        # 1. Setup de .env seguro
        print("\n[1/3] Creando archivo .env con claves seguras...")
        api_key, secret_key = setup_env()
        
        # 2. Crear build_info
        print("\n[2/3] Creando información de build...")
        create_build_info()
        
        # 3. Validación de seguridad
        print("\n[3/3] Validando seguridad del código...")
        validate_security()
        
        print("""
╔══════════════════════════════════════════════════════════════╗
║                 ✅ SETUP COMPLETADO                         ║
╚══════════════════════════════════════════════════════════════╝

Próximos pasos:
1. Revisa el archivo .env generado
2. Compartir .env.example (sin claves) con el equipo
3. Guardar el .env real en lugar seguro
4. Ejecutar: python run_demo.py

Documentación:
- SEGURIDAD.md - Mejores prácticas
- DEPLOYMENT.md - Cómo desplegar
        """)
        
    except Exception as e:
        print(f"\n❌ Error durante setup: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
