#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Ejecutor de CallManager con logging
"""

import sys
import os
import logging

# Configurar logging ANTES de importar la app
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('callmanager_gui.log')
    ]
)

logger = logging.getLogger(__name__)

print("\n" + "="*60)
print("INICIANDO CALLMANAGER v2.0")
print("="*60 + "\n")

logger.info("Starting CallManager...")

try:
    # Agregar paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    client_dir = os.path.join(current_dir, 'client')
    ui_dir = os.path.join(client_dir, 'ui')
    
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    if client_dir not in sys.path:
        sys.path.insert(0, client_dir)
    if ui_dir not in sys.path:
        sys.path.insert(0, ui_dir)
    
    logger.info(f"Python paths configured")
    
    # Importar app
    logger.info("Importing CallManager application...")
    from client.call_manager_app import CallManagerApp
    logger.info("✅ CallManager imported successfully")
    
    # Crear y ejecutar
    logger.info("Creating CallManager instance...")
    app = CallManagerApp()
    logger.info("✅ CallManager instance created")
    
    logger.info("Starting main loop (GUI should appear now)...")
    print("\n🎨 LA INTERFAZ DEBERÍA APARECER AHORA...")
    print("📌 Cierra la ventana para salir\n")
    
    app.mainloop()
    
    logger.info("✅ CallManager closed normally")
    print("\n✅ CallManager cerrado correctamente")
    
except KeyboardInterrupt:
    logger.info("Interrupted by user")
    print("\n⚠️  Interrumpido por usuario")
    sys.exit(0)
    
except Exception as e:
    logger.error(f"❌ FATAL ERROR: {e}", exc_info=True)
    print(f"\n❌ ERROR FATAL: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("="*60)
print("FIN")
print("="*60)
