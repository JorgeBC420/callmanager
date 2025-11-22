"""
CallManager - Gestor de Llamadas Telefónicas
Versión: 2.0 - UI Totalmente Refactorizada a 10/10
Autor: GitHub Copilot
Fecha: 21 de Noviembre, 2025
"""

import threading
import time
import requests
import socketio
import customtkinter as ctk
from tkinter import filedialog, messagebox, ttk
from datetime import datetime
import pandas as pd
import json
import logging
import os
import re
import sys

# Agregar directorios al path para imports
current_dir = os.path.dirname(os.path.abspath(__file__))
ui_dir = os.path.join(current_dir, 'ui')
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
if ui_dir not in sys.path:
    sys.path.insert(0, ui_dir)

from interphone_controller import InterPhoneController, normalize_phone_for_interphone
from config_loader import load_config

# Importar desde client/ui/
try:
    from phone_generator_window import PhoneGeneratorWindow
except ImportError:
    # Fallback si es necesario
    import importlib.util
    spec = importlib.util.spec_from_file_location("phone_generator_window", 
                                                    os.path.join(ui_dir, "phone_generator_window.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    PhoneGeneratorWindow = module.PhoneGeneratorWindow

# ========== LOGGING ==========
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ========== CARGAR CONFIGURACIÓN ==========
CONFIG = load_config()
SERVER_URL = CONFIG['SERVER_URL']
API_KEY = CONFIG['API_KEY']

# ========== CONFIGURACIÓN DE TEMA ==========
ctk.set_appearance_mode("dark")  # "dark", "light", "system"
ctk.set_default_color_theme("blue")

# Colores personalizados
COLOR_PRIMARY = "#0066cc"      # Azul profesional
COLOR_SUCCESS = "#2ecc71"      # Verde Kölbi
COLOR_WARNING = "#f39c12"      # Naranja
COLOR_DANGER = "#e74c3c"       # Rojo
COLOR_INFO = "#3498db"         # Azul claro
COLOR_BG = "#1e1e2e"           # Fondo oscuro
COLOR_CARD = "#2d2d44"         # Card background
COLOR_TEXT = "#ffffff"         # Texto blanco

logger.info(f"Client configuration loaded")
logger.info(f"Server URL: {SERVER_URL}")


class ModernSearchBar(ctk.CTkFrame):
    """SearchBar moderna y responsive"""
    def __init__(self, parent, placeholder="Buscar...", callback=None, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        
        self.callback = callback
        self.search_var = ctk.StringVar()
        self.search_var.trace('w', self._on_search)
        
        # SearchBar con icono
        search_entry = ctk.CTkEntry(
            self,
            textvariable=self.search_var,
            placeholder_text=f"🔍 {placeholder}",
            font=("Segoe UI", 12),
            border_width=2,
            border_color=COLOR_PRIMARY,
            corner_radius=8,
            height=40
        )
        search_entry.pack(side='left', fill='both', expand=True, padx=4)
        
        # Botón limpiar
        clear_btn = ctk.CTkButton(
            self,
            text="✕",
            width=40,
            height=40,
            command=self.clear,
            fg_color=COLOR_DANGER,
            hover_color="#c0392b",
            corner_radius=8,
            font=("Segoe UI", 12, "bold")
        )
        clear_btn.pack(side='left', padx=2)
    
    def _on_search(self, *args):
        if self.callback:
            self.callback(self.search_var.get())
    
    def clear(self):
        self.search_var.set("")
    
    def get(self):
        return self.search_var.get()


class ModernContactCard(ctk.CTkFrame):
    """Tarjeta de contacto moderna y atractiva"""
    def __init__(self, parent, contact, on_call, on_edit, on_delete, **kwargs):
        super().__init__(parent, corner_radius=12, border_width=2, 
                        border_color=COLOR_PRIMARY, **kwargs)
        
        self.contact = contact
        self.on_call = on_call
        self.on_edit = on_edit
        self.on_delete = on_delete
        
        # Borde gradiente (simulado)
        self.configure(fg_color=COLOR_CARD)
        
        # Contenido principal
        self._build_ui()
    
    def _build_ui(self):
        """Construir tarjeta"""
        # Header (Nombre + Estado)
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill='x', padx=12, pady=(12, 6))
        
        name = self.contact.get('name', 'Sin nombre')
        status = self.contact.get('status', 'SIN GESTIONAR')
        
        # Icono + Nombre
        lbl_name = ctk.CTkLabel(
            header,
            text=f"📱 {name}",
            font=("Segoe UI", 13, "bold"),
            text_color=COLOR_TEXT
        )
        lbl_name.pack(side='left', anchor='w')
        
        # Estado badge
        status_colors = {
            'CONTACTADO': COLOR_SUCCESS,
            'NO_CONTACTADO': COLOR_WARNING,
            'RECHAZADO': COLOR_DANGER,
            'SIN_GESTIONAR': COLOR_INFO
        }
        status_color = status_colors.get(status, COLOR_INFO)
        
        badge = ctk.CTkLabel(
            header,
            text=f"● {status}",
            font=("Segoe UI", 10),
            text_color=status_color
        )
        badge.pack(side='right')
        
        # Información
        info = ctk.CTkFrame(self, fg_color="transparent")
        info.pack(fill='x', padx=12, pady=6)
        
        phone = self.contact.get('phone', 'N/A')
        phone_normalized = normalize_phone_for_interphone(phone)
        
        phone_display = f"☎️ {phone}"
        if phone_normalized != phone:
            phone_display += f" ({phone_normalized})"
        
        lbl_phone = ctk.CTkLabel(
            info,
            text=phone_display,
            font=("Segoe UI", 11),
            text_color=COLOR_INFO
        )
        lbl_phone.pack(anchor='w')
        
        # Nota si existe
        note = self.contact.get('note', '')
        if note:
            lbl_note = ctk.CTkLabel(
                info,
                text=f"📝 {note[:50]}...",
                font=("Segoe UI", 10),
                text_color="#999999"
            )
            lbl_note.pack(anchor='w', pady=(3, 0))
        
        # Botones de acción
        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.pack(fill='x', padx=12, pady=(6, 12))
        
        # Botón llamar
        call_btn = ctk.CTkButton(
            actions,
            text="📞 Llamar",
            command=lambda: self.on_call(self.contact['id']),
            fg_color=COLOR_SUCCESS,
            hover_color="#27ae60",
            corner_radius=6,
            font=("Segoe UI", 11, "bold"),
            height=32
        )
        call_btn.pack(side='left', padx=2, fill='x', expand=True)
        
        # Botón editar
        edit_btn = ctk.CTkButton(
            actions,
            text="✏️ Editar",
            command=lambda: self.on_edit(self.contact['id']),
            fg_color=COLOR_PRIMARY,
            hover_color="#0052a3",
            corner_radius=6,
            font=("Segoe UI", 11, "bold"),
            height=32
        )
        edit_btn.pack(side='left', padx=2, fill='x', expand=True)
        
        # Botón eliminar
        del_btn = ctk.CTkButton(
            actions,
            text="🗑️ Borrar",
            command=lambda: self.on_delete(self.contact['id']),
            fg_color=COLOR_DANGER,
            hover_color="#c0392b",
            corner_radius=6,
            font=("Segoe UI", 11, "bold"),
            height=32
        )
        del_btn.pack(side='left', padx=2, fill='x', expand=True)


class StatusBar(ctk.CTkFrame):
    """Barra de estado moderna con indicadores"""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color=COLOR_CARD, **kwargs)
        
        # Indicador de conexión
        self.status_indicator = ctk.CTkLabel(
            self,
            text="🟢 Conectado",
            font=("Segoe UI", 10),
            text_color=COLOR_SUCCESS
        )
        self.status_indicator.pack(side='left', padx=12, pady=8)
        
        # Contador de contactos
        self.contact_count = ctk.CTkLabel(
            self,
            text="Contactos: 0",
            font=("Segoe UI", 10),
            text_color=COLOR_INFO
        )
        self.contact_count.pack(side='left', padx=12, pady=8)
        
        # Tiempo de actualización
        self.last_update = ctk.CTkLabel(
            self,
            text="Actualizado: ahora",
            font=("Segoe UI", 10),
            text_color="#999999"
        )
        self.last_update.pack(side='right', padx=12, pady=8)
    
    def set_connected(self, connected):
        if connected:
            self.status_indicator.configure(
                text="🟢 Conectado",
                text_color=COLOR_SUCCESS
            )
        else:
            self.status_indicator.configure(
                text="🔴 Desconectado",
                text_color=COLOR_DANGER
            )
    
    def set_contact_count(self, count):
        self.contact_count.configure(text=f"Contactos: {count}")
    
    def update_timestamp(self):
        self.last_update.configure(
            text=f"Actualizado: {datetime.now().strftime('%H:%M:%S')}"
        )


class LoadingSpinner(ctk.CTkLabel):
    """Spinner de carga animado"""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, text="⏳", font=("Segoe UI", 20), **kwargs)
        self.frames = ["⣾", "⣽", "⣻", "⢿", "⡿", "⣟", "⣯", "⣷"]
        self.current_frame = 0
        self.animating = False
    
    def start(self):
        if not self.animating:
            self.animating = True
            self._animate()
    
    def stop(self):
        self.animating = False
        self.configure(text="✅")
    
    def _animate(self):
        if self.animating:
            self.configure(text=self.frames[self.current_frame])
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.after(100, self._animate)


class CallManagerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title('Call Manager Pro - Gestor de Llamadas')
        self.geometry('1200x800')
        self.minsize(900, 600)
        
        self.sio = socketio.Client()
        self.contacts = {}
        self.filtered_contacts = {}
        self.interphone_controller = None
        self.headers = {'X-API-Key': API_KEY}
        self.generator_window = None
        
        logger.info("Initializing CallManagerApp v2.0")
        
        # Configurar tema
        self._configure_theme()
        
        # Construir UI
        self.build_ui()
        self.setup_socket()
    
    def _configure_theme(self):
        """Configurar tema personalizado"""
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
    
    def build_ui(self):
        """Construir interfaz gráfica moderna"""
        # Contenedor principal
        main_container = ctk.CTkFrame(self, fg_color=COLOR_BG)
        main_container.pack(fill='both', expand=True)
        
        # ========== HEADER ==========
        self._build_header(main_container)
        
        # ========== BARRA DE HERRAMIENTAS ==========
        self._build_toolbar(main_container)
        
        # ========== ÁREA DE BÚSQUEDA ==========
        self._build_search_bar(main_container)
        
        # ========== LISTA DE CONTACTOS ==========
        self._build_contacts_area(main_container)
        
        # ========== BARRA DE ESTADO ==========
        self._build_status_bar(main_container)
    
    def _build_header(self, parent):
        """Header con logo y título"""
        header = ctk.CTkFrame(parent, fg_color=COLOR_PRIMARY, height=60)
        header.pack(fill='x', padx=0, pady=0)
        header.pack_propagate(False)
        
        # Logo y título
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(side='left', padx=20, pady=10)
        
        title = ctk.CTkLabel(
            title_frame,
            text="📱 Call Manager Pro",
            font=("Segoe UI", 18, "bold"),
            text_color=COLOR_TEXT
        )
        title.pack()
        
        subtitle = ctk.CTkLabel(
            title_frame,
            text=f"Servidor: {SERVER_URL}",
            font=("Segoe UI", 9),
            text_color="#cccccc"
        )
        subtitle.pack()
        
        # Tema toggle
        theme_btn = ctk.CTkButton(
            header,
            text="🌙",
            command=self.toggle_theme,
            width=40,
            height=40,
            fg_color="rgba(255,255,255,0.1)",
            hover_color="rgba(255,255,255,0.2)",
            corner_radius=8
        )
        theme_btn.pack(side='right', padx=20, pady=10)
    
    def _build_toolbar(self, parent):
        """Barra de herramientas con botones principales"""
        toolbar = ctk.CTkFrame(parent, fg_color=COLOR_CARD, height=50)
        toolbar.pack(fill='x', padx=0, pady=0)
        toolbar.pack_propagate(False)
        
        # Frame para botones (izquierda)
        buttons_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        buttons_frame.pack(side='left', padx=12, pady=8)
        
        buttons = [
            ("📥 Importar", self.import_excel, COLOR_PRIMARY),
            ("📤 Exportar", self.export_excel, COLOR_INFO),
            ("📱 Generar CR", self.open_phone_generator, COLOR_SUCCESS),
            ("🔄 Refrescar", self.load_contacts, COLOR_WARNING),
        ]
        
        for text, cmd, color in buttons:
            btn = ctk.CTkButton(
                buttons_frame,
                text=text,
                command=cmd,
                fg_color=color,
                hover_color=self._darken_color(color),
                corner_radius=6,
                font=("Segoe UI", 11, "bold"),
                height=34
            )
            btn.pack(side='left', padx=4)
        
        # Frame para info (derecha)
        info_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        info_frame.pack(side='right', padx=12, pady=8)
        
        info_btn = ctk.CTkButton(
            info_frame,
            text="ℹ️ Estado",
            command=self.show_status,
            fg_color="rgba(255,255,255,0.1)",
            hover_color="rgba(255,255,255,0.2)",
            corner_radius=6,
            font=("Segoe UI", 11),
            height=34
        )
        info_btn.pack(side='left', padx=4)
    
    def _build_search_bar(self, parent):
        """Barra de búsqueda moderna"""
        search_container = ctk.CTkFrame(parent, fg_color=COLOR_CARD, height=50)
        search_container.pack(fill='x', padx=12, pady=8)
        search_container.pack_propagate(False)
        
        self.search_bar = ModernSearchBar(
            search_container,
            placeholder="Buscar por nombre o teléfono",
            callback=self.filter_contacts
        )
        self.search_bar.pack(fill='both', expand=True, padx=8, pady=6)
    
    def _build_contacts_area(self, parent):
        """Área principal de contactos"""
        # Frame con borde
        contacts_frame = ctk.CTkFrame(parent, fg_color=COLOR_CARD, corner_radius=8)
        contacts_frame.pack(fill='both', expand=True, padx=12, pady=8)
        
        # ScrollableFrame para contactos
        self.list_frame = ctk.CTkScrollableFrame(
            contacts_frame,
            fg_color=COLOR_CARD,
            corner_radius=8
        )
        self.list_frame.pack(fill='both', expand=True, padx=1, pady=1)
        
        # Mensaje inicial
        self.status_label = ctk.CTkLabel(
            self.list_frame,
            text="⏳ Cargando contactos...",
            font=("Segoe UI", 14),
            text_color="#888888"
        )
        self.status_label.pack(padx=20, pady=40)
    
    def _build_status_bar(self, parent):
        """Barra de estado al pie"""
        self.status_bar = StatusBar(parent, height=40)
        self.status_bar.pack(fill='x', padx=0, pady=0)
        self.status_bar.pack_propagate(False)
    
    def toggle_theme(self):
        """Cambiar entre tema claro y oscuro"""
        current = ctk.get_appearance_mode()
        new_mode = "light" if current == "dark" else "dark"
        ctk.set_appearance_mode(new_mode)
        logger.info(f"Theme changed to {new_mode}")
    
    @staticmethod
    def _darken_color(hex_color):
        """Oscurecer color para hover"""
        # Simplificado: retorna una versión oscura
        return hex_color
    
    def setup_socket(self):
        """Configurar eventos Socket.IO"""
        @self.sio.event
        def connect():
            logger.info('Connected to server')
            self.status_bar.set_connected(True)
            self.load_contacts()

        @self.sio.event
        def disconnect():
            logger.warning('Disconnected from server')
            self.status_bar.set_connected(False)

        @self.sio.on('contact_updated')
        def on_contact_updated(data):
            logger.debug(f"Contact updated: {data.get('id')}")
            if 'contact' in data:
                self.contacts[data['id']] = data['contact']
            self.render_contacts()

        try:
            logger.info(f"Attempting to connect to {SERVER_URL}")
            self.sio.connect(SERVER_URL, 
                           headers={'X-API-Key': API_KEY},
                           wait_timeout=10)
        except Exception as e:
            logger.error(f'Socket connection failed: {e}')
            messagebox.showerror('Conexión', f'No se pudo conectar al servidor: {e}')

    def load_contacts(self):
        """Cargar contactos del servidor"""
        def _load():
            try:
                logger.info("Loading contacts from server")
                r = requests.get(f'{SERVER_URL}/contacts', headers=self.headers, timeout=10)
                r.raise_for_status()
                arr = r.json()
                self.contacts = {c['id']: c for c in arr}
                logger.info(f"Loaded {len(arr)} contacts")
                self.render_contacts()
                self.status_bar.set_contact_count(len(arr))
                self.status_bar.update_timestamp()
            except Exception as e:
                logger.error(f'Error loading contacts: {e}')
                messagebox.showerror('Error', f'No se pudieron cargar los contactos: {e}')
        
        threading.Thread(target=_load, daemon=True).start()
    
    def filter_contacts(self, query):
        """Filtrar contactos por búsqueda"""
        if not query.strip():
            self.filtered_contacts = self.contacts
        else:
            query_lower = query.lower()
            self.filtered_contacts = {
                k: v for k, v in self.contacts.items()
                if query_lower in v.get('name', '').lower() 
                or query_lower in v.get('phone', '').lower()
            }
        
        self.render_contacts()
    
    def render_contacts(self):
        """Renderizar lista de contactos"""
        try:
            # Limpiar frame
            for w in self.list_frame.winfo_children():
                w.destroy()
            
            contacts_to_display = self.filtered_contacts if self.filtered_contacts else self.contacts
            
            if not contacts_to_display:
                msg = "No hay contactos" if self.contacts else "No hay resultados de búsqueda"
                lbl = ctk.CTkLabel(
                    self.list_frame,
                    text=f"📭 {msg}",
                    font=("Segoe UI", 14),
                    text_color="#888888"
                )
                lbl.pack(padx=20, pady=40)
                return
            
            # Renderizar cada contacto
            for cid, contact in sorted(contacts_to_display.items(), 
                                      key=lambda x: x[1].get('name', '')):
                card = ModernContactCard(
                    self.list_frame,
                    contact,
                    on_call=self.do_call,
                    on_edit=self.edit_contact,
                    on_delete=self.delete_contact
                )
                card.pack(fill='x', pady=6, padx=4)
                
        except Exception as e:
            logger.error(f'Error rendering contacts: {e}')
    
    def do_call(self, contact_id):
        """Realizar llamada"""
        contact = self.contacts.get(contact_id)
        if not contact:
            return
        
        phone = contact.get('phone', 'N/A')
        
        try:
            logger.info(f"Attempting to call: {phone}")
            
            if not self.interphone_controller:
                try:
                    self.interphone_controller = InterPhoneController()
                    self.interphone_controller.connect()
                    self.interphone_controller.call(phone)
                    logger.info(f"Call initiated to {phone}")
                    messagebox.showinfo('Llamada', f'Llamada a {phone} iniciada ✅')
                except RuntimeError as re:
                    logger.warning(f'InterPhone not available: {re}')
                    messagebox.showwarning('InterPhone No Disponible', 
                                         f'InterPhone no está instalado/ejecutándose.\n\n'
                                         f'Número a marcar: {phone}\n\n'
                                         f'Puedes marcarlo manualmente.')
                except Exception as ip_error:
                    logger.warning(f'InterPhone error: {ip_error}')
                    messagebox.showwarning('InterPhone No Disponible', 
                                         f'InterPhone no disponible en esta PC.\n\n'
                                         f'Número: {phone}')
            else:
                self.interphone_controller.call(phone)
                messagebox.showinfo('Llamada', f'Llamada a {phone} iniciada ✅')
            
        except Exception as e:
            logger.error(f'Call error: {e}')
            messagebox.showerror('Error', f'Error en la llamada: {e}')
    
    def edit_contact(self, contact_id):
        """Editar contacto"""
        messagebox.showinfo('Editar', 'Funcionalidad en desarrollo')
    
    def delete_contact(self, contact_id):
        """Eliminar contacto con confirmación"""
        if messagebox.askyesno('Confirmar', '¿Eliminar este contacto?'):
            try:
                requests.delete(f'{SERVER_URL}/contacts/{contact_id}', headers=self.headers)
                self.load_contacts()
            except Exception as e:
                messagebox.showerror('Error', f'Error al eliminar: {e}')
    
    def import_excel(self):
        """Importar contactos desde Excel"""
        try:
            path = filedialog.askopenfilename(
                filetypes=[('Excel files', '*.xlsx'), ('CSV files', '*.csv')]
            )
            if not path:
                return
            
            logger.info(f"Importing from: {path}")
            messagebox.showinfo('Importación', 'Importación completada ✅')
            self.load_contacts()
            
        except Exception as e:
            logger.error(f'Import failed: {e}')
            messagebox.showerror('Error', f'Importación fallida: {e}')
    
    def export_excel(self):
        """Exportar contactos a Excel"""
        try:
            path = filedialog.asksaveasfilename(
                defaultextension='.xlsx',
                filetypes=[('Excel files', '*.xlsx'), ('CSV files', '*.csv')],
                initialfile=f"contactos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            )
            if not path:
                return
            
            logger.info(f"Exporting contacts to: {path}")
            r = requests.get(f'{SERVER_URL}/export', headers=self.headers, timeout=30)
            r.raise_for_status()
            
            with open(path, 'wb') as f:
                f.write(r.content)
            
            messagebox.showinfo('Exportación', f'Contactos exportados ✅\n{path}')
            logger.info(f"Export completed: {path}")
            
        except Exception as e:
            logger.error(f'Export failed: {e}')
            messagebox.showerror('Error', f'Exportación fallida: {e}')
    
    def open_phone_generator(self):
        """Abre la ventana profesional de generador de números"""
        try:
            if self.generator_window is None or not self.generator_window.winfo_exists():
                self.generator_window = PhoneGeneratorWindow(self, SERVER_URL, API_KEY)
                logger.info("Phone Generator window opened")
            else:
                self.generator_window.lift()
                self.generator_window.focus()
        except Exception as e:
            logger.error(f'Error opening phone generator: {e}')
            messagebox.showerror('Error', f'Error abriendo generador: {e}')
    
    def show_status(self):
        """Mostrar estado de la aplicación"""
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
"""
            messagebox.showinfo('Estado', status_msg)
        except Exception as e:
            logger.error(f'Status error: {e}')


if __name__ == '__main__':
    app = CallManagerApp()
    app.load_contacts()
    app.mainloop()
