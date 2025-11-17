"""
config_loader.py - Cargar configuración desde múltiples fuentes
Prioridad: Env variables → config_local.json → config.py defaults
"""
import os
import json

def get_server_url():
    """Obtener URL del servidor desde env o archivo"""
    # 1. Variable de entorno
    url = os.environ.get('CALLMANAGER_SERVER_URL')
    if url:
        return url
    
    # 2. Archivo config_local.json
    config_path = os.path.join(os.path.dirname(__file__), 'config_local.json')
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                if 'SERVER_URL' in config:
                    return config['SERVER_URL']
        except Exception as e:
            print(f"Error loading config_local.json: {e}")
    
    # 3. Valor por defecto
    return 'http://127.0.0.1:5000'

def get_api_key():
    """Obtener API key desde env o archivo"""
    # 1. Variable de entorno
    key = os.environ.get('CALLMANAGER_API_KEY')
    if key:
        return key
    
    # 2. Archivo config_local.json
    config_path = os.path.join(os.path.dirname(__file__), 'config_local.json')
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                if 'API_KEY' in config:
                    return config['API_KEY']
        except Exception as e:
            print(f"Error loading config_local.json: {e}")
    
    # 3. Valor por defecto
    return 'dev-key-change-in-production'

def load_config():
    """Cargar toda la configuración disponible"""
    return {
        'SERVER_URL': get_server_url(),
        'API_KEY': get_api_key(),
    }
