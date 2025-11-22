#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CallManager v2.0 - Versión Corregida
Material Design Dark Theme con CustomTkinter
"""

import customtkinter as ctk
from tkinter import messagebox, filedialog
import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Colores Material Design
COLOR_PRIMARY = "#0066cc"
COLOR_SUCCESS = "#2ecc71"
COLOR_WARNING = "#f39c12"
COLOR_DANGER = "#e74c3c"
COLOR_INFO = "#3498db"
COLOR_BG = "#1e1e2e"
COLOR_CARD = "#2d2d44"
COLOR_TEXT = "#ffffff"
COLOR_TEXT_SECONDARY = "#cccccc"

# Configuración
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class ModernContactCard(ctk.CTkFrame):
    """Tarjeta de contacto moderna"""
    
    def __init__(self, parent, contact, on_call=None, on_edit=None, on_delete=None, **kwargs):
        super().__init__(parent, fg_color=COLOR_CARD, corner_radius=8, **kwargs)
        
        self.contact = contact
        self.on_call = on_call
        self.on_edit = on_edit
        self.on_delete = on_delete
        
        # Contenedor
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
            text_color=COLOR_TEXT_SECONDARY
        )
        phone.pack(anchor='w', pady=(0, 8))
        
        # Botones
        buttons = ctk.CTkFrame(main, fg_color="transparent")
        buttons.pack(fill='x', pady=(6, 0))
        
        if self.on_call:
            btn_call = ctk.CTkButton(
                buttons,
                text="📞 Llamar",
                command=self.on_call,
                fg_color=COLOR_SUCCESS,
                hover_color="#27ae60",
                corner_radius=6,
                font=("Segoe UI", 10, "bold"),
                height=32
            )
            btn_call.pack(side='left', padx=2, fill='x', expand=True)
        
        if self.on_edit:
            btn_edit = ctk.CTkButton(
                buttons,
                text="✏️ Editar",
                command=self.on_edit,
                fg_color=COLOR_PRIMARY,
                hover_color="#0052a3",
                corner_radius=6,
                font=("Segoe UI", 10, "bold"),
                height=32
            )
            btn_edit.pack(side='left', padx=2, fill='x', expand=True)
        
        if self.on_delete:
            btn_delete = ctk.CTkButton(
                buttons,
                text="🗑️ Borrar",
                command=self.on_delete,
                fg_color=COLOR_DANGER,
                hover_color="#c0392b",
                corner_radius=6,
                font=("Segoe UI", 10, "bold"),
                height=32
            )
            btn_delete.pack(side='left', padx=2, fill='x', expand=True)


class ModernSearchBar(ctk.CTkFrame):
    """Barra de búsqueda moderna"""
    
    def __init__(self, parent, on_search=None, **kwargs):
        super().__init__(parent, fg_color=COLOR_CARD, corner_radius=8, **kwargs)
        
        self.on_search = on_search
        
        # Frame interno
        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.pack(fill='x', padx=8, pady=8)
        
        # Entry
        self.entry = ctk.CTkEntry(
            inner,
            placeholder_text="🔍 Buscar contacto...",
            font=("Segoe UI", 12),
            border_width=2,
            border_color=COLOR_PRIMARY,
            corner_radius=8,
            height=40
        )
        self.entry.pack(side='left', fill='both', expand=True, padx=(0, 8))
        self.entry.bind('<KeyRelease>', self._on_key_release)
        
        # Botón limpiar
        btn_clear = ctk.CTkButton(
            inner,
            text="✕",
            command=self._clear,
            fg_color=COLOR_DANGER,
            hover_color="#c0392b",
            corner_radius=6,
            width=40,
            height=40,
            font=("Segoe UI", 14)
        )
        btn_clear.pack(side='left', padx=0)
    
    def _on_key_release(self, event):
        if self.on_search:
            self.on_search(self.entry.get())
    
    def _clear(self):
        self.entry.delete(0, 'end')
        if self.on_search:
            self.on_search("")
    
    def get(self):
        return self.entry.get()


class StatusBar(ctk.CTkFrame):
    """Barra de estado"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color=COLOR_CARD, height=40, **kwargs)
        self.pack_propagate(False)
        
        self.status_label = ctk.CTkLabel(
            self,
            text="✅ Conectado | 📞 0 contactos",
            font=("Segoe UI", 10),
            text_color=COLOR_TEXT_SECONDARY
        )
        self.status_label.pack(side='left', padx=12, pady=10)
    
    def update_status(self, connected=True, contact_count=0):
        status = "✅ Conectado" if connected else "❌ Desconectado"
        timestamp = datetime.now().strftime("%H:%M:%S")
        text = f"{status} | 📞 {contact_count} contactos | 🕐 {timestamp}"
        self.status_label.configure(text=text)


class CallManagerApp(ctk.CTk):
    """CallManager v2.0 - Aplicación Principal"""
    
    def __init__(self):
        super().__init__()
        
        self.title('CallManager v2.0 Pro')
        self.geometry('1100x750')
        self.minsize(900, 600)
        
        # Datos
        self.contacts = {}
        self.filtered_contacts = []
        
        logger.info("Inicializando CallManager v2.0...")
        
        # Protocolo de cierre
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Build UI
        self._build_ui()
        
        # Load contacts
        self.load_contacts()
        
        logger.info("CallManager v2.0 listo")
    
    def _build_ui(self):
        """Construir interfaz de usuario"""
        
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
            text="Sistema de Gestión de Llamadas",
            font=("Segoe UI", 11),
            text_color=COLOR_TEXT_SECONDARY
        )
        subtitle.pack(side='left', padx=0, pady=10)
        
        # Botón tema
        btn_theme = ctk.CTkButton(
            header,
            text="🌙 Tema",
            command=self.toggle_theme,
            fg_color=COLOR_INFO,
            hover_color="#2980b9",
            font=("Segoe UI", 11, "bold"),
            height=34,
            width=80
        )
        btn_theme.pack(side='right', padx=20, pady=10)
        
        # ===== TOOLBAR =====
        toolbar = ctk.CTkFrame(main, fg_color=COLOR_CARD, height=50)
        toolbar.pack(fill='x', padx=12, pady=6)
        toolbar.pack_propagate(False)
        
        btn_importar = ctk.CTkButton(
            toolbar,
            text="📥 Importar",
            command=self.import_contacts,
            fg_color=COLOR_PRIMARY,
            hover_color="#0052a3",
            font=("Segoe UI", 11, "bold"),
            height=34
        )
        btn_importar.pack(side='left', padx=6, pady=8)
        
        btn_exportar = ctk.CTkButton(
            toolbar,
            text="📤 Exportar",
            command=self.export_contacts,
            fg_color=COLOR_INFO,
            hover_color="#2980b9",
            font=("Segoe UI", 11, "bold"),
            height=34
        )
        btn_exportar.pack(side='left', padx=6, pady=8)
        
        btn_generar = ctk.CTkButton(
            toolbar,
            text="📱 Generar",
            command=self.open_generator,
            fg_color=COLOR_SUCCESS,
            hover_color="#27ae60",
            font=("Segoe UI", 11, "bold"),
            height=34
        )
        btn_generar.pack(side='left', padx=6, pady=8)
        
        btn_refrescar = ctk.CTkButton(
            toolbar,
            text="🔄 Refrescar",
            command=self.refresh_contacts,
            fg_color=COLOR_WARNING,
            hover_color="#d68910",
            font=("Segoe UI", 11, "bold"),
            height=34
        )
        btn_refrescar.pack(side='left', padx=6, pady=8)
        
        # ===== BÚSQUEDA =====
        self.search_bar = ModernSearchBar(main, on_search=self.filter_contacts)
        self.search_bar.pack(fill='x', padx=12, pady=6)
        
        # ===== CONTACTOS =====
        contacts_frame = ctk.CTkFrame(main, fg_color=COLOR_CARD, corner_radius=8)
        contacts_frame.pack(fill='both', expand=True, padx=12, pady=6)
        
        self.list_frame = ctk.CTkScrollableFrame(
            contacts_frame,
            fg_color=COLOR_CARD,
            corner_radius=8
        )
        self.list_frame.pack(fill='both', expand=True, padx=1, pady=1)
        
        # ===== STATUS BAR =====
        self.status_bar = StatusBar(main)
        self.status_bar.pack(fill='x', padx=0, pady=0)
    
    def load_contacts(self):
        """Cargar contactos desde JSON"""
        try:
            contacts_file = Path(__file__).parent.parent / 'demo_contacts.json'
            
            if contacts_file.exists():
                with open(contacts_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        self.contacts = {i: c for i, c in enumerate(data, 1)}
                    else:
                        self.contacts = data
                logger.info(f"✅ {len(self.contacts)} contactos cargados")
            else:
                # Contactos de demo
                self.contacts = {
                    1: {'id': 1, 'name': 'Juan García', 'phone': '88883333'},
                    2: {'id': 2, 'name': 'María López', 'phone': '87654321'},
                    3: {'id': 3, 'name': 'Carlos Rodríguez', 'phone': '88889999'},
                    4: {'id': 4, 'name': 'Ana Martínez', 'phone': '87779999'},
                    5: {'id': 5, 'name': 'Pedro Sánchez', 'phone': '88881111'},
                }
                logger.info("📭 Usando contactos de demo")
            
            self.render_contacts()
            self.status_bar.update_status(True, len(self.contacts))
        
        except Exception as e:
            logger.error(f"Error cargando contactos: {e}")
            messagebox.showerror("Error", f"No se pudieron cargar los contactos:\n{e}")
    
    def render_contacts(self):
        """Renderizar lista de contactos"""
        try:
            # Limpiar
            for w in self.list_frame.winfo_children():
                w.destroy()
            
            contacts_to_show = self.filtered_contacts if self.filtered_contacts else self.contacts
            
            if not contacts_to_show:
                msg = "No hay contactos" if not self.contacts else "Sin resultados"
                lbl = ctk.CTkLabel(
                    self.list_frame,
                    text=f"📭 {msg}",
                    font=("Segoe UI", 14),
                    text_color=COLOR_TEXT_SECONDARY
                )
                lbl.pack(pady=40)
            else:
                for cid, contact in contacts_to_show.items():
                    card = ModernContactCard(
                        self.list_frame,
                        contact,
                        on_call=lambda c=contact: self.call_contact(c),
                        on_edit=lambda c=contact: self.edit_contact(c),
                        on_delete=lambda c=contact: self.delete_contact(c)
                    )
                    card.pack(fill='x', pady=4, padx=4)
        
        except Exception as e:
            logger.error(f"Error renderizando: {e}")
    
    def filter_contacts(self, query):
        """Filtrar contactos por búsqueda"""
        query = query.lower()
        self.filtered_contacts = {
            cid: c for cid, c in self.contacts.items()
            if query in c.get('name', '').lower() or query in c.get('phone', '').lower()
        }
        self.render_contacts()
        self.status_bar.update_status(True, len(self.filtered_contacts if query else self.contacts))
    
    def call_contact(self, contact):
        """Hacer llamada a contacto"""
        messagebox.showinfo("Llamada", f"Llamando a {contact.get('name', 'N/A')}\n{contact.get('phone', 'N/A')}")
        logger.info(f"📞 Llamada a {contact.get('name')}")
    
    def edit_contact(self, contact):
        """Editar contacto"""
        messagebox.showinfo("Editar", f"Editando a {contact.get('name', 'N/A')}")
        logger.info(f"✏️ Editando {contact.get('name')}")
    
    def delete_contact(self, contact):
        """Borrar contacto"""
        if messagebox.askyesno("Borrar", f"¿Borrar a {contact.get('name')}?"):
            # Encontrar y borrar
            for cid, c in list(self.contacts.items()):
                if c.get('id') == contact.get('id'):
                    del self.contacts[cid]
                    break
            self.render_contacts()
            logger.info(f"🗑️ Borrado {contact.get('name')}")
    
    def import_contacts(self):
        """Importar contactos"""
        file = filedialog.askopenfilename(
            title="Importar contactos",
            filetypes=[("JSON files", "*.json"), ("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if file:
            messagebox.showinfo("Importar", f"Importando desde:\n{file}")
            logger.info(f"📥 Importando desde {file}")
    
    def export_contacts(self):
        """Exportar contactos"""
        file = filedialog.asksaveasfilename(
            title="Exportar contactos",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("CSV files", "*.csv")]
        )
        if file:
            messagebox.showinfo("Exportar", f"Exportando a:\n{file}")
            logger.info(f"📤 Exportando a {file}")
    
    def open_generator(self):
        """Abrir generador de números"""
        messagebox.showinfo("Generador", "Abriendo generador de números telefónicos")
        logger.info("📱 Generador abierto")
    
    def refresh_contacts(self):
        """Refrescar contactos"""
        self.load_contacts()
        messagebox.showinfo("Refrescar", "Contactos refrescados")
        logger.info("🔄 Contactos refrescados")
    
    def toggle_theme(self):
        """Cambiar tema"""
        current = ctk.get_appearance_mode()
        new_mode = "light" if current == "dark" else "dark"
        ctk.set_appearance_mode(new_mode)
        logger.info(f"🎨 Tema cambiado a {new_mode}")
    
    def on_closing(self):
        """Manejar cierre de aplicación"""
        logger.info("Cerrando CallManager...")
        self.destroy()


if __name__ == '__main__':
    logger.info("="*60)
    logger.info("INICIANDO CALLMANAGER v2.0")
    logger.info("="*60)
    
    app = CallManagerApp()
    app.mainloop()
    
    logger.info("✅ Aplicación cerrada")
