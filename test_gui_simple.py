#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test simple de CustomTkinter - Diagnosticar problemas de GUI
"""

import sys
import os

# Agregar paths
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'client'))

print("=" * 60)
print("DIAGNÓSTICO DE GUI - CustomTkinter")
print("=" * 60)

# Test 1: Importar customtkinter
print("\n1. Importando customtkinter...")
try:
    import customtkinter as ctk
    print("   ✅ customtkinter importado correctamente")
except ImportError as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# Test 2: Configurar tema
print("\n2. Configurando tema...")
try:
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    print("   ✅ Tema configurado")
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# Test 3: Crear ventana simple
print("\n3. Creando ventana simple...")
try:
    class SimpleApp(ctk.CTk):
        def __init__(self):
            super().__init__()
            self.title('CallManager - Test Simple')
            self.geometry('800x600')
            
            # Label simple
            label = ctk.CTkLabel(
                self,
                text="✅ INTERFAZ CARGADA CORRECTAMENTE",
                font=("Segoe UI", 20, "bold"),
                text_color="#2ecc71"
            )
            label.pack(pady=20)
            
            # Info
            info = ctk.CTkLabel(
                self,
                text="CallManager v2.0 UI Test\nSi ves este texto, la GUI funciona!",
                font=("Segoe UI", 14),
                text_color="#ffffff"
            )
            info.pack(pady=10)
            
            # Botón
            btn = ctk.CTkButton(
                self,
                text="Cerrar Ventana (o Ctrl+C)",
                command=self.quit,
                fg_color="#0066cc",
                hover_color="#0052a3",
                font=("Segoe UI", 12, "bold"),
                height=40
            )
            btn.pack(pady=20, padx=20, fill='x')
    
    print("   ✅ Clase creada")
    
    # Crear y mostrar app
    print("\n4. Iniciando aplicación...")
    app = SimpleApp()
    print("   ✅ Ventana creada - Mostrando...")
    print("\n   🎉 Si ves una ventana azul oscura, ¡la GUI FUNCIONA!")
    print("   📌 Cierra la ventana (botón X) o presiona Ctrl+C\n")
    app.mainloop()
    print("   ✅ Ventana cerrada correctamente")
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ TEST COMPLETADO - GUI FUNCIONAL")
print("=" * 60)
