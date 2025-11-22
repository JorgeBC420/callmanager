#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Inicia el servidor CallManager sin debugger/reloader para producción
"""

import os
import sys

# Asegurar que estamos en modo desarrollo para permitir socketio
os.environ['FLASK_ENV'] = 'development'

# Importar y correr
from server import socketio, app, SERVER_HOST, SERVER_PORT

if __name__ == '__main__':
    print("🚀 Iniciando CallManager Server (sin debugger)...")
    print(f"   URL: http://{SERVER_HOST}:{SERVER_PORT}")
    socketio.run(app, host=SERVER_HOST, port=SERVER_PORT, debug=False, use_reloader=False, allow_unsafe_werkzeug=True)
