#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Debug versión - Ver qué causa el cierre inmediato
"""

import sys
import os
import time

# Paths
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'client'))

print("1. Importando customtkinter...")
import customtkinter as ctk
print("   ✅ customtkinter importado")

print("2. Configurando tema...")
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")
print("   ✅ Tema configurado")

print("3. Definiendo clase...")
class DebugApp(ctk.CTk):
    def __init__(self):
        print("   3a. Inicializando CTk...")
        super().__init__()
        print("   3b. CTk inicializado")
        
        self.title('DEBUG - CallManager')
        self.geometry('800x600')
        print("   3c. Geometría establecida")
        
        # Frame principal
        frame = ctk.CTkFrame(self)
        frame.pack(fill='both', expand=True)
        print("   3d. Frame creado")
        
        # Label
        label = ctk.CTkLabel(frame, text="¡HOLA! Si ves esto, la ventana FUNCIONA", font=("Arial", 14))
        label.pack(padx=20, pady=20)
        print("   3e. Label creado")
        
        # Botón
        btn = ctk.CTkButton(frame, text="Click aquí", command=self.on_click)
        btn.pack(padx=20, pady=20)
        print("   3f. Botón creado")
        
    def on_click(self):
        print("   ✅ BOTÓN CLICKEADO!")

print("   ✅ Clase definida")

print("4. Creando instancia de la app...")
try:
    app = DebugApp()
    print("   ✅ App instanciada")
    
    print("5. Iniciando mainloop...")
    print("   ⏳ La ventana debe estar visible ahora...")
    print("   (Presiona Ctrl+C aquí en la terminal para cerrar)\n")
    
    # Esperar 2 segundos antes de mainloop
    time.sleep(2)
    
    app.mainloop()
    print("   ✅ mainloop completó")
    
except Exception as e:
    print(f"   ❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n✅ Script terminó")
