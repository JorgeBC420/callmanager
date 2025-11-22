#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Iniciar CallManager Completo:
1. Servidor Flask en background
2. Cliente CustomTkinter en foreground
"""

import subprocess
import time
import os
import sys

print("\n" + "="*70)
print("🚀 INICIANDO CALLMANAGER v2.0 COMPLETO")
print("="*70 + "\n")

# Cambiar a directorio del proyecto
os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("1️⃣  Iniciando servidor Flask en background...")
print("   (puerto 5000)")

# Iniciar servidor
server_process = subprocess.Popen(
    [sys.executable, "server.py"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

time.sleep(3)

if server_process.poll() is None:
    print("   ✅ Servidor iniciado correctamente\n")
else:
    print("   ❌ Error iniciando servidor\n")
    sys.exit(1)

print("2️⃣  Iniciando cliente CallManager...")
print("   (presiona Alt+F4 o cierra la ventana para salir)\n")

# Iniciar cliente
try:
    client_process = subprocess.Popen(
        [sys.executable, "client/call_manager_app.py"]
    )
    client_process.wait()
except KeyboardInterrupt:
    print("\n\n📛 Cerrando CallManager...")
finally:
    # Cerrar servidor
    server_process.terminate()
    try:
        server_process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        server_process.kill()

print("✅ CallManager cerrado\n")
