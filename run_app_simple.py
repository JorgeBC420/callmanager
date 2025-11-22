#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CallManager v2.0 - Versión Simplificada para Pruebas
Sin Socket.IO, sin requests complejos - Solo UI
"""

import sys
import os

# Paths
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'client'))

import customtkinter as ctk
from tkinter import messagebox
import threading
import time

# Configurar tema
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Colores
COLOR_PRIMARY = "#0066cc"
COLOR_SUCCESS = "#2ecc71"
COLOR_WARNING = "#f39c12"
COLOR_DANGER = "#e74c3c"
COLOR_INFO = "#3498db"
COLOR_BG = "#1e1e2e"
COLOR_CARD = "#2d2d44"
COLOR_TEXT = "#ffffff"


class SimpleContactCard(ctk.CTkFrame):
    """Tarjeta de contacto simplificada"""
    
    def __init__(self, parent, contact, **kwargs):
        super().__init__(parent, fg_color=COLOR_CARD, corner_radius=8, **kwargs)
        
        self.contact = contact
        
        # Contenedor principal
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(fill='x', padx=12, pady=12)
        
        # Nombre
        name = ctk.CTkLabel(
            main,
            text=contact.get('name', 'Sin nombre'),
            font=("Segoe UI", 13, "bold"),
            text_color=COLOR_TEXT
        )
        name.pack(anchor='w', pady=(0, 4))
        
        # Teléfono
        phone = ctk.CTkLabel(
            main,
            text=f"📱 {contact.get('phone', 'N/A')}",
            font=("Segoe UI", 11),
            text_color="#cccccc"
        )
        phone.pack(anchor='w', pady=(0, 8))
        
        # Botones
        buttons = ctk.CTkFrame(main, fg_color="transparent")
        buttons.pack(fill='x', pady=(6, 0))
        
        btn_call = ctk.CTkButton(
            buttons,
            text="📞 Llamar",
            command=lambda: messagebox.showinfo('Demo', f'Llamando a {contact.get("name")}'),
            fg_color=COLOR_SUCCESS,
            hover_color="#27ae60",
            corner_radius=6,
            font=("Segoe UI", 10, "bold"),
            height=32
        )
        btn_call.pack(side='left', padx=2, fill='x', expand=True)
        
        btn_edit = ctk.CTkButton(
            buttons,
            text="✏️ Editar",
            command=lambda: messagebox.showinfo('Demo', f'Editando {contact.get("name")}'),
            fg_color=COLOR_PRIMARY,
            hover_color="#0052a3",
            corner_radius=6,
            font=("Segoe UI", 10, "bold"),
            height=32
        )
        btn_edit.pack(side='left', padx=2, fill='x', expand=True)
        
        btn_delete = ctk.CTkButton(
            buttons,
            text="🗑️ Borrar",
            command=lambda: messagebox.showinfo('Demo', f'Borrando {contact.get("name")}'),
            fg_color=COLOR_DANGER,
            hover_color="#c0392b",
            corner_radius=6,
            font=("Segoe UI", 10, "bold"),
            height=32
        )
        btn_delete.pack(side='left', padx=2, fill='x', expand=True)


class SimpleApp(ctk.CTk):
    """CallManager v2.0 - Versión Simplificada"""
    
    def __init__(self):
        super().__init__()
        self.title('CallManager v2.0 - Demo')
        self.geometry('1000x700')
        self.minsize(800, 600)
        
        # Datos de demo
        self.contacts = {
            1: {'id': 1, 'name': 'Juan García', 'phone': '88883333'},
            2: {'id': 2, 'name': 'María López', 'phone': '87654321'},
            3: {'id': 3, 'name': 'Carlos Rodríguez', 'phone': '88889999'},
            4: {'id': 4, 'name': 'Ana Martínez', 'phone': '87779999'},
            5: {'id': 5, 'name': 'Pedro Sánchez', 'phone': '88881111'},
        }
        
        # Build UI
        self._build_ui()
    
    def _build_ui(self):
        """Construir interfaz"""
        # Contenedor principal
        main = ctk.CTkFrame(self, fg_color=COLOR_BG)
        main.pack(fill='both', expand=True)
        
        # ===== HEADER =====
        header = ctk.CTkFrame(main, fg_color=COLOR_PRIMARY, height=60)
        header.pack(fill='x', padx=0, pady=0)
        header.pack_propagate(False)
        
        title = ctk.CTkLabel(
            header,
            text="📱 CallManager Pro v2.0",
            font=("Segoe UI", 18, "bold"),
            text_color=COLOR_TEXT
        )
        title.pack(side='left', padx=20, pady=10)
        
        subtitle = ctk.CTkLabel(
            header,
            text="Gestor de Llamadas - Demo UI",
            font=("Segoe UI", 11),
            text_color="#cccccc"
        )
        subtitle.pack(side='left', padx=0, pady=10)
        
        # ===== TOOLBAR =====
        toolbar = ctk.CTkFrame(main, fg_color=COLOR_CARD, height=50)
        toolbar.pack(fill='x', padx=0, pady=0)
        toolbar.pack_propagate(False)
        
        btn_importar = ctk.CTkButton(
            toolbar,
            text="📥 Importar",
            command=lambda: messagebox.showinfo('Demo', 'Importar contactos'),
            fg_color=COLOR_PRIMARY,
            hover_color="#0052a3",
            font=("Segoe UI", 11, "bold"),
            height=34
        )
        btn_importar.pack(side='left', padx=8, pady=8)
        
        btn_exportar = ctk.CTkButton(
            toolbar,
            text="📤 Exportar",
            command=lambda: messagebox.showinfo('Demo', 'Exportar contactos'),
            fg_color=COLOR_INFO,
            hover_color="#2980b9",
            font=("Segoe UI", 11, "bold"),
            height=34
        )
        btn_exportar.pack(side='left', padx=8, pady=8)
        
        btn_generar = ctk.CTkButton(
            toolbar,
            text="📱 Generar",
            command=lambda: messagebox.showinfo('Demo', 'Generador de números'),
            fg_color=COLOR_SUCCESS,
            hover_color="#27ae60",
            font=("Segoe UI", 11, "bold"),
            height=34
        )
        btn_generar.pack(side='left', padx=8, pady=8)
        
        # ===== BÚSQUEDA =====
        search_frame = ctk.CTkFrame(main, fg_color=COLOR_CARD, height=50)
        search_frame.pack(fill='x', padx=12, pady=8)
        search_frame.pack_propagate(False)
        
        search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="🔍 Buscar por nombre o teléfono...",
            font=("Segoe UI", 12),
            border_width=2,
            border_color=COLOR_PRIMARY,
            corner_radius=8,
            height=40
        )
        search_entry.pack(fill='x', padx=8, pady=5)
        
        # ===== CONTACTOS =====
        contacts_frame = ctk.CTkFrame(main, fg_color=COLOR_CARD, corner_radius=8)
        contacts_frame.pack(fill='both', expand=True, padx=12, pady=8)
        
        # ScrollableFrame
        self.contacts_list = ctk.CTkScrollableFrame(
            contacts_frame,
            fg_color=COLOR_CARD,
            corner_radius=8
        )
        self.contacts_list.pack(fill='both', expand=True, padx=1, pady=1)
        
        # Renderizar contactos
        for cid, contact in self.contacts.items():
            card = SimpleContactCard(self.contacts_list, contact)
            card.pack(fill='x', pady=6, padx=4)
        
        # ===== STATUS BAR =====
        status = ctk.CTkFrame(main, fg_color=COLOR_CARD, height=40)
        status.pack(fill='x', padx=0, pady=0)
        status.pack_propagate(False)
        
        status_text = ctk.CTkLabel(
            status,
            text=f"✅ Conectado  |  📞 {len(self.contacts)} contactos  |  🕐 Ahora",
            font=("Segoe UI", 10),
            text_color="#cccccc"
        )
        status_text.pack(side='left', padx=12, pady=10)


if __name__ == "__main__":
    print("\n" + "="*60)
    print("INICIANDO CALLMANAGER v2.0 - DEMO SIMPLIFICADA")
    print("="*60)
    print("\n✨ La ventana debería aparecer ahora...")
    print("📌 Puedes probar los botones y la UI")
    print("❌ Cierra la ventana para salir\n")
    
    try:
        app = SimpleApp()
        app.mainloop()
        print("\n✅ Aplicación cerrada correctamente")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
