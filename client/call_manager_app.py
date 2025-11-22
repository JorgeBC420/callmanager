#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CallManager v2.0 - Versión Corregida
Material Design Dark Theme con CustomTkinter + API Backend
"""

import customtkinter as ctk
from tkinter import messagebox, filedialog, simpledialog
import os
import sys
import json
import logging
import threading
import requests
import socketio
from datetime import datetime
from pathlib import Path

# Agregar directorios al path
current_dir = os.path.dirname(os.path.abspath(__file__))
ui_dir = os.path.join(current_dir, 'ui')
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
if ui_dir not in sys.path:
    sys.path.insert(0, ui_dir)

# Importar desde config
try:
    from config_loader import load_config
    CONFIG = load_config()
    SERVER_URL = CONFIG.get('SERVER_URL', 'http://localhost:5000')
    API_KEY = CONFIG.get('API_KEY', 'dev-key-change-in-production')
except:
    SERVER_URL = 'http://localhost:5000'
    API_KEY = 'dev-key-change-in-production'

# Importar InterPhone
try:
    from interphone_controller import InterPhoneController, normalize_phone_for_interphone
    interphone_available = True
except:
    interphone_available = False

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
    """Tarjeta de contacto moderna con estado"""
    
    def __init__(self, parent, contact, on_call=None, on_edit=None, on_delete=None, **kwargs):
        super().__init__(parent, fg_color=COLOR_CARD, corner_radius=8, **kwargs)
        
        self.contact = contact
        self.on_call = on_call
        self.on_edit = on_edit
        self.on_delete = on_delete
        
        # Contenedor
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(fill='x', padx=12, pady=12)
        
        # Sección superior: Nombre + Estado
        header = ctk.CTkFrame(main, fg_color="transparent")
        header.pack(fill='x', pady=(0, 8))
        
        # Nombre
        name = ctk.CTkLabel(
            header,
            text=contact.get('name', 'Sin nombre'),
            font=("Segoe UI", 13, "bold"),
            text_color=COLOR_TEXT
        )
        name.pack(anchor='w', side='left')
        
        # Estado de llamada
        status = contact.get('status', 'SIN GESTIONAR')
        status_icon = self._get_status_icon(status)
        status_color = self._get_status_color(status)
        
        status_label = ctk.CTkLabel(
            header,
            text=f"{status_icon} {status}",
            font=("Segoe UI", 10),
            text_color=status_color
        )
        status_label.pack(anchor='e', side='right')
        
        # Teléfono
        phone = ctk.CTkLabel(
            main,
            text=f"📱 {contact.get('phone', 'N/A')}",
            font=("Segoe UI", 11),
            text_color=COLOR_TEXT_SECONDARY
        )
        phone.pack(anchor='w', pady=(0, 4))
        
        # Notas si existen
        if contact.get('notes'):
            notes = ctk.CTkLabel(
                main,
                text=f"📝 {contact.get('notes', '')[:60]}...",
                font=("Segoe UI", 9),
                text_color=COLOR_TEXT_SECONDARY,
                wraplength=300
            )
            notes.pack(anchor='w', pady=(0, 6))
        
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
    
    @staticmethod
    def _get_status_icon(status):
        """Obtener icono según estado"""
        icons = {
            'COMPLETADA': '✅',
            'PENDIENTE': '⏳',
            'EN PROGRESO': '📞',
            'NO CONTACTADO': '❌',
            'NO DISPONIBLE': '⛔',
            'SIN GESTIONAR': '⚪'
        }
        return icons.get(status, '⚪')
    
    @staticmethod
    def _get_status_color(status):
        """Obtener color según estado"""
        colors = {
            'COMPLETADA': COLOR_SUCCESS,
            'PENDIENTE': COLOR_WARNING,
            'EN PROGRESO': COLOR_INFO,
            'NO CONTACTADO': COLOR_DANGER,
            'NO DISPONIBLE': COLOR_DANGER,
            'SIN GESTIONAR': COLOR_TEXT_SECONDARY
        }
        return colors.get(status, COLOR_TEXT_SECONDARY)


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


class LoadingSpinner(ctk.CTkFrame):
    """Spinner de carga animado"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        
        self.spinner_chars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        self.current_frame = 0
        self.is_running = False
        self.after_id = None
        
        self.label = ctk.CTkLabel(
            self,
            text="⠋ Cargando...",
            font=("Segoe UI", 12, "bold"),
            text_color=COLOR_PRIMARY
        )
        self.label.pack(pady=20)
    
    def start(self):
        """Iniciar animación"""
        self.is_running = True
        self._animate()
    
    def stop(self):
        """Detener animación"""
        self.is_running = False
        if self.after_id:
            self.after_cancel(self.after_id)
    
    def _animate(self):
        """Animar spinner"""
        if self.is_running:
            char = self.spinner_chars[self.current_frame]
            self.label.configure(text=f"{char} Cargando...")
            self.current_frame = (self.current_frame + 1) % len(self.spinner_chars)
            self.after_id = self.after(100, self._animate)


class StatusBar(ctk.CTkFrame):
    """Barra de estado mejorada con indicadores de conexión"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color=COLOR_CARD, height=40, **kwargs)
        self.pack_propagate(False)
        
        # Frame para elementos
        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.pack(fill='x', padx=12, pady=10, side='left', expand=True)
        
        # Indicador de conexión
        self.connection_label = ctk.CTkLabel(
            inner,
            text="✅ Conectado",
            font=("Segoe UI", 10),
            text_color=COLOR_SUCCESS
        )
        self.connection_label.pack(side='left', padx=10)
        
        # Separador
        sep1 = ctk.CTkLabel(inner, text="|", font=("Segoe UI", 10), text_color=COLOR_TEXT_SECONDARY)
        sep1.pack(side='left', padx=5)
        
        # Contador de contactos
        self.contact_label = ctk.CTkLabel(
            inner,
            text="📞 0 contactos",
            font=("Segoe UI", 10),
            text_color=COLOR_TEXT_SECONDARY
        )
        self.contact_label.pack(side='left', padx=10)
        
        # Separador
        sep2 = ctk.CTkLabel(inner, text="|", font=("Segoe UI", 10), text_color=COLOR_TEXT_SECONDARY)
        sep2.pack(side='left', padx=5)
        
        # Timestamp
        self.timestamp_label = ctk.CTkLabel(
            inner,
            text="🕐 Ahora",
            font=("Segoe UI", 10),
            text_color=COLOR_TEXT_SECONDARY
        )
        self.timestamp_label.pack(side='left', padx=10)
    
    def set_connected(self, connected):
        """Actualizar estado de conexión"""
        if connected:
            self.connection_label.configure(
                text="✅ Conectado",
                text_color=COLOR_SUCCESS
            )
        else:
            self.connection_label.configure(
                text="❌ Desconectado",
                text_color=COLOR_DANGER
            )
    
    def set_contact_count(self, count):
        """Actualizar contador de contactos"""
        self.contact_label.configure(text=f"📞 {count} contactos")
    
    def update_timestamp(self):
        """Actualizar timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.timestamp_label.configure(text=f"🕐 {timestamp}")
    
    def update_status(self, connected=True, contact_count=0):
        """Método compatible con versión anterior"""
        self.set_connected(connected)
        self.set_contact_count(contact_count)
        self.update_timestamp()


class CallManagerApp(ctk.CTk):
    """CallManager v2.0 - Aplicación Principal con API"""
    
    def __init__(self):
        super().__init__()
        
        self.title('CallManager v2.0 Pro')
        self.geometry('1100x750')
        self.minsize(900, 600)
        
        # Configuración de API
        self.headers = {
            'Content-Type': 'application/json',
            'X-API-Key': API_KEY
        }
        
        # Datos
        self.contacts = {}
        self.filtered_contacts = []
        self.generator_window = None
        
        # InterPhone
        self.interphone_controller = None
        if interphone_available:
            try:
                self.interphone_controller = InterPhoneController()
                logger.info("✅ InterPhone inicializado")
            except Exception as e:
                logger.warning(f"⚠️ InterPhone no disponible: {e}")
        
        # Socket.IO
        self.sio = socketio.Client()
        self.setup_socket()
        
        logger.info("Inicializando CallManager v2.0...")
        
        # Protocolo de cierre
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Build UI
        self._build_ui()
        
        # Load contacts en thread para no bloquear UI
        threading.Thread(target=self.load_contacts, daemon=True).start()
        
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
        btn_theme.pack(side='right', padx=8, pady=10)
        
        # Botón estado
        btn_status = ctk.CTkButton(
            header,
            text="ℹ️ Estado",
            command=self.show_status,
            fg_color=COLOR_WARNING,
            hover_color="#d68910",
            font=("Segoe UI", 11, "bold"),
            height=34,
            width=80
        )
        btn_status.pack(side='right', padx=8, pady=10)
        
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
    
    def setup_socket(self):
        """Configurar eventos Socket.IO para actualizaciones en tiempo real"""
        @self.sio.event
        def connect():
            logger.info('✅ Conectado a Socket.IO')
            self.status_bar.set_connected(True)
            threading.Thread(target=self.load_contacts, daemon=True).start()

        @self.sio.event
        def disconnect():
            logger.warning('❌ Desconectado de Socket.IO')
            self.status_bar.set_connected(False)

        @self.sio.on('contact_updated')
        def on_contact_updated(data):
            logger.debug(f"Contacto actualizado: {data.get('id')}")
            if 'contact' in data:
                contact = data['contact']
                self.contacts[contact['id']] = contact
            self.after(0, self.render_contacts)

        @self.sio.on('contact_deleted')
        def on_contact_deleted(data):
            contact_id = data.get('id')
            logger.debug(f"Contacto borrado: {contact_id}")
            if contact_id in self.contacts:
                del self.contacts[contact_id]
            self.after(0, self.render_contacts)

        # Intentar conectar en thread para no bloquear UI
        threading.Thread(target=self._connect_socket, daemon=True).start()
    
    def _connect_socket(self):
        """Conectar a Socket.IO en background"""
        try:
            logger.info(f"Intentando conectar a {SERVER_URL}")
            self.sio.connect(
                SERVER_URL,
                headers={'X-API-Key': API_KEY},
                wait_timeout=5
            )
        except Exception as e:
            logger.warning(f"Socket.IO no disponible: {e}")
            self.after(0, lambda: self.status_bar.set_connected(False))
    
    def load_contacts(self):
        """Cargar contactos desde API o JSON local"""
        try:
            # Intentar cargar desde API
            try:
                response = requests.get(
                    f'{SERVER_URL}/contacts',
                    headers=self.headers,
                    timeout=5
                )
                if response.status_code == 200:
                    data = response.json()
                    self.contacts = {c['id']: c for c in data}
                    logger.info(f"✅ {len(self.contacts)} contactos cargados desde API")
                else:
                    raise Exception("Error de API")
            except:
                # Fallback a JSON local
                contacts_file = Path(__file__).parent.parent / 'demo_contacts.json'
                
                if contacts_file.exists():
                    with open(contacts_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if isinstance(data, list):
                            self.contacts = {i: c for i, c in enumerate(data, 1)}
                        else:
                            self.contacts = data
                    logger.info(f"✅ {len(self.contacts)} contactos cargados localmente")
                else:
                    # Contactos de demo
                    self.contacts = {
                        1: {'id': 1, 'name': 'Juan García', 'phone': '88883333', 'status': 'SIN GESTIONAR'},
                        2: {'id': 2, 'name': 'María López', 'phone': '87654321', 'status': 'SIN GESTIONAR'},
                        3: {'id': 3, 'name': 'Carlos Rodríguez', 'phone': '88889999', 'status': 'SIN GESTIONAR'},
                        4: {'id': 4, 'name': 'Ana Martínez', 'phone': '87779999', 'status': 'SIN GESTIONAR'},
                        5: {'id': 5, 'name': 'Pedro Sánchez', 'phone': '88881111', 'status': 'SIN GESTIONAR'},
                    }
                    logger.info("📭 Usando contactos de demo")
            
            self.after(0, self.render_contacts)
            self.after(0, lambda: self.status_bar.update_status(True, len(self.contacts)))
        
        except Exception as e:
            logger.error(f"Error cargando contactos: {e}")
            self.after(0, lambda: messagebox.showerror("Error", f"No se pudieron cargar los contactos:\n{e}"))
    
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
        """Hacer llamada a contacto con manejo robusto"""
        try:
            phone = contact.get('phone', '')
            name = contact.get('name', 'N/A')
            contact_id = contact.get('id')
            
            logger.info(f"Intentando llamar a: {phone}")
            
            # Intentar usar InterPhone
            if self.interphone_controller:
                try:
                    normalized = normalize_phone_for_interphone(phone)
                    self.interphone_controller.call(normalized)
                    messagebox.showinfo('Llamada', f'📞 Llamada a {name} iniciada ✅')
                    logger.info(f"📞 Llamada iniciada a {name} ({phone})")
                    
                    # Actualizar estado
                    threading.Thread(
                        target=self._update_contact_status,
                        args=(contact_id, 'EN PROGRESO'),
                        daemon=True
                    ).start()
                except RuntimeError as re:
                    logger.warning(f'InterPhone no disponible: {re}')
                    messagebox.showwarning('InterPhone No Disponible', 
                                         f'InterPhone no está instalado.\n\n'
                                         f'Número: {phone}\n\n'
                                         f'Puedes marcarlo manualmente.')
                except Exception as e:
                    logger.warning(f'Error con InterPhone: {e}')
                    messagebox.showinfo('Llamada', f'📞 Llamada a {name} registrada')
            else:
                messagebox.showinfo('Llamada', f'📞 Llamada a {name} ({phone}) registrada')
                logger.info(f"📞 Mock call a {name}")
        
        except Exception as e:
            logger.error(f'Error en llamada: {e}')
            messagebox.showerror('Error', f'Error en la llamada: {e}')
    
    def edit_contact(self, contact):
        """Editar contacto con diálogo"""
        try:
            # Crear ventana de edición
            edit_window = ctk.CTkToplevel(self)
            edit_window.title(f"Editar: {contact.get('name')}")
            edit_window.geometry('500x500')
            edit_window.resizable(False, False)
            
            # Hacer modal
            edit_window.transient(self)
            edit_window.grab_set()
            
            # Frame contenedor
            main_frame = ctk.CTkFrame(edit_window, fg_color=COLOR_BG)
            main_frame.pack(fill='both', expand=True, padx=20, pady=20)
            
            # Nombre
            ctk.CTkLabel(main_frame, text="Nombre:", font=("Segoe UI", 12, "bold")).pack(anchor='w', pady=(10, 0))
            entry_name = ctk.CTkEntry(main_frame, placeholder_text="Nombre del contacto")
            entry_name.insert(0, contact.get('name', ''))
            entry_name.pack(fill='x', pady=(5, 10))
            
            # Teléfono
            ctk.CTkLabel(main_frame, text="Teléfono:", font=("Segoe UI", 12, "bold")).pack(anchor='w', pady=(10, 0))
            entry_phone = ctk.CTkEntry(main_frame, placeholder_text="Número telefónico")
            entry_phone.insert(0, contact.get('phone', ''))
            entry_phone.pack(fill='x', pady=(5, 10))
            
            # Estado
            ctk.CTkLabel(main_frame, text="Estado:", font=("Segoe UI", 12, "bold")).pack(anchor='w', pady=(10, 0))
            status_var = ctk.StringVar(value=contact.get('status', 'SIN GESTIONAR'))
            status_menu = ctk.CTkOptionMenu(
                main_frame,
                variable=status_var,
                values=['SIN GESTIONAR', 'PENDIENTE', 'EN PROGRESO', 'COMPLETADA', 'NO CONTACTADO', 'NO DISPONIBLE']
            )
            status_menu.pack(fill='x', pady=(5, 10))
            
            # Notas
            ctk.CTkLabel(main_frame, text="Notas:", font=("Segoe UI", 12, "bold")).pack(anchor='w', pady=(10, 0))
            text_notes = ctk.CTkTextbox(main_frame, height=150, font=("Segoe UI", 11))
            text_notes.pack(fill='both', expand=True, pady=(5, 10))
            text_notes.insert('1.0', contact.get('notes', ''))
            
            # Botones
            button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
            button_frame.pack(fill='x', pady=(20, 0))
            
            def save_changes():
                """Guardar cambios en base de datos"""
                try:
                    updated_data = {
                        'name': entry_name.get(),
                        'phone': entry_phone.get(),
                        'status': status_var.get(),
                        'notes': text_notes.get('1.0', 'end-1c')
                    }
                    
                    # Actualizar en API
                    contact_id = contact.get('id')
                    response = requests.put(
                        f'{SERVER_URL}/contacts/{contact_id}',
                        json=updated_data,
                        headers=self.headers,
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        # Actualizar localmente
                        for cid, c in self.contacts.items():
                            if c.get('id') == contact_id:
                                c.update(updated_data)
                                break
                        self.render_contacts()
                        edit_window.destroy()
                        messagebox.showinfo('Éxito', f'✅ {entry_name.get()} actualizado')
                        logger.info(f"✏️ Contacto {contact_id} actualizado")
                    else:
                        messagebox.showerror('Error', f'Error actualizando contacto: {response.text}')
                
                except Exception as e:
                    logger.error(f"Error guardando cambios: {e}")
                    messagebox.showerror('Error', f'Error guardando cambios:\n{e}')
            
            def cancel():
                edit_window.destroy()
            
            btn_save = ctk.CTkButton(
                button_frame,
                text="💾 Guardar",
                command=save_changes,
                fg_color=COLOR_SUCCESS,
                hover_color="#27ae60"
            )
            btn_save.pack(side='left', padx=5, fill='x', expand=True)
            
            btn_cancel = ctk.CTkButton(
                button_frame,
                text="❌ Cancelar",
                command=cancel,
                fg_color=COLOR_DANGER,
                hover_color="#c0392b"
            )
            btn_cancel.pack(side='left', padx=5, fill='x', expand=True)
        
        except Exception as e:
            logger.error(f"Error en editar contacto: {e}")
            messagebox.showerror("Error", f"Error editando contacto:\n{e}")
    
    def delete_contact(self, contact):
        """Borrar contacto con confirmación"""
        try:
            name = contact.get('name', 'Contacto')
            if messagebox.askyesno("Confirmar", f"¿Borrar a {name}?"):
                contact_id = contact.get('id')
                
                # Intentar borrar de API
                try:
                    response = requests.delete(
                        f'{SERVER_URL}/contacts/{contact_id}',
                        headers=self.headers,
                        timeout=10
                    )
                    
                    if response.status_code in [200, 204]:
                        # Borrar localmente
                        for cid in list(self.contacts.keys()):
                            if self.contacts[cid].get('id') == contact_id:
                                del self.contacts[cid]
                                break
                        self.render_contacts()
                        self.status_bar.set_contact_count(len(self.contacts))
                        messagebox.showinfo('Éxito', f'✅ {name} borrado')
                        logger.info(f"🗑️ Contacto {contact_id} borrado desde API")
                    else:
                        raise Exception(f"API error: {response.status_code}")
                except Exception as api_error:
                    logger.warning(f"No se pudo borrar de API: {api_error}")
                    # Fallback a borrado local
                    for cid in list(self.contacts.keys()):
                        if self.contacts[cid].get('id') == contact_id:
                            del self.contacts[cid]
                            break
                    self.render_contacts()
                    self.status_bar.set_contact_count(len(self.contacts))
                    messagebox.showinfo('Éxito', f'✅ {name} borrado (local)')
                    logger.info(f"🗑️ Contacto {contact_id} borrado localmente")
        
        except Exception as e:
            logger.error(f'Error borrando contacto: {e}')
            messagebox.showerror('Error', f'Error borrando contacto: {e}')
    
    def _update_contact_status(self, contact_id, status):
        """Actualizar estado de contacto en background"""
        try:
            response = requests.put(
                f'{SERVER_URL}/contacts/{contact_id}',
                json={'status': status},
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                # Actualizar localmente
                for cid, c in self.contacts.items():
                    if c.get('id') == contact_id:
                        c['status'] = status
                        self.after(0, self.render_contacts)
                        break
                logger.info(f"📝 Estado actualizado: {contact_id} -> {status}")
        except Exception as e:
            logger.warning(f"No se pudo actualizar estado en API: {e}")
    
    def import_contacts(self):
        """Importar contactos desde archivo"""
        try:
            file = filedialog.askopenfilename(
                title="Importar contactos",
                filetypes=[("Excel files", "*.xlsx"), ("CSV files", "*.csv"), ("JSON files", "*.json"), ("All files", "*.*")]
            )
            if not file:
                return
            
            # Leer archivo
            try:
                if file.endswith('.json'):
                    with open(file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    contacts_data = data if isinstance(data, list) else list(data.values())
                elif file.endswith('.csv'):
                    import csv
                    with open(file, 'r', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        contacts_data = list(reader)
                else:  # Excel
                    import pandas as pd
                    df = pd.read_excel(file)
                    contacts_data = df.to_dict('records')
                
                # Enviar a API
                threading.Thread(
                    target=self._import_thread,
                    args=(contacts_data,),
                    daemon=True
                ).start()
                
                messagebox.showinfo('Importación', f'Importando {len(contacts_data)} contactos...')
            
            except Exception as e:
                logger.error(f"Error leyendo archivo: {e}")
                messagebox.showerror('Error', f'Error leyendo archivo:\n{e}')
        
        except Exception as e:
            logger.error(f'Import error: {e}')
            messagebox.showerror('Error', f'Error en importación: {e}')
    
    def _import_thread(self, contacts_data):
        """Thread para importar en background"""
        try:
            for contact in contacts_data:
                try:
                    response = requests.post(
                        f'{SERVER_URL}/contacts',
                        json=contact,
                        headers=self.headers,
                        timeout=10
                    )
                    if response.status_code == 201:
                        new_contact = response.json()
                        self.contacts[new_contact['id']] = new_contact
                except:
                    pass
            
            self.after(0, self.render_contacts)
            self.after(0, lambda: messagebox.showinfo('Éxito', '✅ Importación completada'))
            logger.info(f"📥 Importados {len(contacts_data)} contactos")
        except Exception as e:
            logger.error(f"Import thread error: {e}")
    
    def export_contacts(self):
        """Exportar contactos a archivo"""
        try:
            file = filedialog.asksaveasfilename(
                title="Exportar contactos",
                defaultextension='.xlsx',
                filetypes=[("Excel files", "*.xlsx"), ("CSV files", "*.csv"), ("JSON files", "*.json")],
                initialfile=f"contactos_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )
            if not file:
                return
            
            # Exportar según formato
            try:
                contacts_list = list(self.contacts.values())
                
                if file.endswith('.json'):
                    with open(file, 'w', encoding='utf-8') as f:
                        json.dump(contacts_list, f, ensure_ascii=False, indent=2)
                elif file.endswith('.csv'):
                    import csv
                    if contacts_list:
                        keys = contacts_list[0].keys()
                        with open(file, 'w', newline='', encoding='utf-8') as f:
                            writer = csv.DictWriter(f, fieldnames=keys)
                            writer.writeheader()
                            writer.writerows(contacts_list)
                else:  # Excel
                    import pandas as pd
                    df = pd.DataFrame(contacts_list)
                    df.to_excel(file, index=False)
                
                messagebox.showinfo('Éxito', f'✅ Contactos exportados a:\n{file}')
                logger.info(f"📤 Exportados {len(contacts_list)} contactos a {file}")
            
            except Exception as e:
                logger.error(f"Error exportando: {e}")
                messagebox.showerror('Error', f'Error exportando:\n{e}')
        
        except Exception as e:
            logger.error(f'Export error: {e}')
            messagebox.showerror('Error', f'Error en exportación: {e}')
    
    def open_generator(self):
        """Abrir generador de números telefónicos"""
        try:
            # Intentar importar PhoneGeneratorWindow
            try:
                from phone_generator_window import PhoneGeneratorWindow
                if self.generator_window is None or not self.generator_window.winfo_exists():
                    self.generator_window = PhoneGeneratorWindow(self, SERVER_URL, API_KEY)
                    logger.info("📱 Generador abierto")
                else:
                    self.generator_window.lift()
                    self.generator_window.focus()
            except ImportError:
                messagebox.showinfo("Generador", "Módulo de generador no disponible")
                logger.warning("⚠️ PhoneGeneratorWindow no encontrado")
        
        except Exception as e:
            logger.error(f'Error abriendo generador: {e}')
            messagebox.showerror('Error', f'Error abriendo generador:\n{e}')
    
    def refresh_contacts(self):
        """Refrescar contactos desde servidor"""
        threading.Thread(target=self.load_contacts, daemon=True).start()
        messagebox.showinfo("Refrescar", "Refrescando contactos...")
        logger.info("🔄 Refrescando contactos")
    
    def toggle_theme(self):
        """Cambiar tema"""
        current = ctk.get_appearance_mode()
        new_mode = "light" if current == "dark" else "dark"
        ctk.set_appearance_mode(new_mode)
        logger.info(f"🎨 Tema cambiado a {new_mode}")
    
    def show_status(self):
        """Mostrar estado detallado de la aplicación"""
        try:
            status_msg = f"""
╔══════════════════════════════════════╗
║     ESTADO DE LA APLICACIÓN          ║
╚══════════════════════════════════════╝

📡 Servidor: {SERVER_URL}
🔌 Socket.IO: {'✅ Conectado' if self.sio.connected else '❌ Desconectado'}
📱 Contactos: {len(self.contacts)}
📞 InterPhone: {'✅ Disponible' if self.interphone_controller else '⚠️ No inicializado'}

🔐 Seguridad:
   API Key: {API_KEY[:20]}...
   
📊 Versión: CallManager v2.0
"""
            messagebox.showinfo('Estado de la Aplicación', status_msg)
        except Exception as e:
            logger.error(f'Error mostrando estado: {e}')
    
    def on_closing(self):
        """Manejar cierre de aplicación"""
        logger.info("Cerrando CallManager...")
        try:
            # Desconectar Socket.IO
            if self.sio.connected:
                self.sio.disconnect()
        except:
            pass
        self.destroy()


if __name__ == '__main__':
    logger.info("="*60)
    logger.info("INICIANDO CALLMANAGER v2.0")
    logger.info("="*60)
    
    app = CallManagerApp()
    app.mainloop()
    
    logger.info("✅ Aplicación cerrada")
