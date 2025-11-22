import threading
import time
import requests
import socketio
import customtkinter as ctk
from tkinter import filedialog, messagebox
from datetime import datetime
import pandas as pd
import json
import logging
import os
import re
from interphone_controller import InterPhoneController, normalize_phone_for_interphone
from config_loader import load_config
from phone_generator_window import PhoneGeneratorWindow

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

logger.info(f"Client configuration loaded")
logger.info(f"Server URL: {SERVER_URL}")


class CallManagerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title('Call Manager - Gestor de Llamadas')
        self.geometry('1000x700')
        self.sio = socketio.Client()
        self.contacts = {}
        self.interphone_controller = None
        self.headers = {'X-API-Key': API_KEY}
        self.generator_window = None  # Referencia a ventana generador
        
        logger.info("Initializing CallManagerApp")
        self.build_ui()
        self.setup_socket()
        
    def build_ui(self):
        """Construir interfaz gráfica"""
        # Barra superior con botones
        top = ctk.CTkFrame(self)
        top.pack(fill='x', padx=8, pady=8)

        lbl_title = ctk.CTkLabel(top, text=f"Servidor: {SERVER_URL}", font=("Arial", 10))
        lbl_title.pack(side='left', padx=4)

        import_btn = ctk.CTkButton(top, text='📥 Importar Excel', command=self.import_excel)
        import_btn.pack(side='left', padx=4)

        export_btn = ctk.CTkButton(top, text='📤 Exportar Excel', command=self.export_excel)
        export_btn.pack(side='left', padx=4)

        generator_btn = ctk.CTkButton(
            top,
            text='📱 Generar CR',
            command=self.open_phone_generator,
            width=120,
            fg_color="#2ecc71",
            hover_color="#27ae60"
        )
        generator_btn.pack(side='left', padx=4)

        refresh_btn = ctk.CTkButton(top, text='🔄 Refrescar', command=self.load_contacts)
        refresh_btn.pack(side='left', padx=4)
        
        status_btn = ctk.CTkButton(top, text='ℹ️ Estado', command=self.show_status)
        status_btn.pack(side='left', padx=4)

        # Marco scrollable para contactos
        self.list_frame = ctk.CTkScrollableFrame(self)
        self.list_frame.pack(fill='both', expand=True, padx=8, pady=8)
        
        # Mostrar estado inicial
        self.status_label = ctk.CTkLabel(self.list_frame, text="Cargando contactos...", font=("Arial", 12))
        self.status_label.pack(padx=8, pady=8)

    def setup_socket(self):
        """Configurar eventos Socket.IO"""
        @self.sio.event
        def connect():
            logger.info('Connected to server')
            messagebox.showinfo('Conexión', 'Conectado al servidor')
            self.load_contacts()

        @self.sio.event
        def disconnect():
            logger.warning('Disconnected from server')
            messagebox.showwarning('Conexión', 'Desconectado del servidor')

        @self.sio.on('contact_updated')
        def on_contact_updated(data):
            logger.debug(f"Contact updated: {data.get('id')}")
            if 'contact' in data:
                self.contacts[data['id']] = data['contact']
            self.render_contacts()

        @self.sio.on('contact_locked')
        def on_contact_locked(data):
            logger.info(f"Contact {data.get('id')} locked by {data.get('locked_by')}")
            messagebox.showinfo('Bloqueado', f"Contacto bloqueado por {data.get('locked_by')}")
            self.render_contacts()

        @self.sio.on('contact_unlocked')
        def on_contact_unlocked(data):
            logger.info(f"Contact {data.get('id')} unlocked")
            self.render_contacts()

        @self.sio.on('error')
        def on_error(data):
            logger.error(f"Server error: {data.get('message')}")
            messagebox.showerror('Error', data.get('message', 'Error desconocido'))

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
        try:
            logger.info("Loading contacts from server")
            r = requests.get(f'{SERVER_URL}/contacts', headers=self.headers, timeout=10)
            r.raise_for_status()
            arr = r.json()
            self.contacts = {c['id']: c for c in arr}
            logger.info(f"Loaded {len(arr)} contacts")
            self.render_contacts()
        except requests.exceptions.ConnectionError:
            logger.error("Cannot connect to server")
            messagebox.showerror('Error', f'No se puede conectar a {SERVER_URL}\nVerifica que el servidor esté activo')
        except requests.exceptions.Timeout:
            logger.error("Server request timeout")
            messagebox.showerror('Error', 'Timeout: El servidor no respondió a tiempo')
        except Exception as e:
            logger.error(f'Error loading contacts: {e}')
            messagebox.showerror('Error', f'No se pudieron cargar los contactos: {e}')

    def render_contacts(self):
        """Renderizar lista de contactos"""
        try:
            # Limpiar frame
            for w in self.list_frame.winfo_children():
                w.destroy()
            
            if not self.contacts:
                lbl = ctk.CTkLabel(self.list_frame, text="No hay contactos. Importa desde Excel.", font=("Arial", 12))
                lbl.pack(padx=8, pady=8)
                return
            
            # Renderizar cada contacto
            for cid, c in sorted(self.contacts.items(), key=lambda x: x[1].get('name', '')):
                self.render_contact_card(cid, c)
                
        except Exception as e:
            logger.error(f'Error rendering contacts: {e}')
    
    def render_contact_card(self, cid, contact):
        """Renderizar tarjeta individual de contacto con información de visibilidad"""
        try:
            frame = ctk.CTkFrame(self.list_frame, border_width=1, corner_radius=8)
            frame.pack(fill='x', pady=6, padx=4)

            # Información principal
            info_frame = ctk.CTkFrame(frame)
            info_frame.pack(side='left', fill='both', expand=True, padx=8, pady=8)

            name = contact.get('name', 'N/A')
            phone = contact.get('phone', 'N/A')
            # ⭐ Mostrar teléfono normalizado (sin +506)
            phone_normalized = normalize_phone_for_interphone(phone)
            status = contact.get('status', 'SIN GESTIONAR')
            note = contact.get('note', '')
            locked_by = contact.get('locked_by', None)
            visibility_months = contact.get('visibility_months_ago')  # ⭐ NUEVO: Información de visibilidad

            lbl_name = ctk.CTkLabel(info_frame, text=f"📱 {name}", font=("Arial", 11, "bold"))
            lbl_name.pack(anchor='w')

            # Mostrar teléfono con formato: número original (número para llamar)
            if phone_normalized != phone:
                phone_display = f"☎️ {phone} ({phone_normalized})"
            else:
                phone_display = f"☎️ {phone}"
            lbl_phone = ctk.CTkLabel(info_frame, text=phone_display, font=("Arial", 10))
            lbl_phone.pack(anchor='w')

            # ⭐ NUEVO: Mostrar estado con información de visibilidad
            visibility_text = ""
            if visibility_months is not None:
                if visibility_months >= 8:
                    visibility_text = f" [❌ {visibility_months} meses sin contacto]"
                elif visibility_months >= 6:
                    visibility_text = f" [⚠️ {visibility_months} meses sin red]"
                elif visibility_months >= 3:
                    visibility_text = f" [⏰ {visibility_months} meses no existe]"
            
            lbl_status = ctk.CTkLabel(info_frame, text=f"Status: {status}{visibility_text}", font=("Arial", 9), text_color="gray")
            lbl_status.pack(anchor='w')

            if note:
                lbl_note = ctk.CTkLabel(info_frame, text=f"Nota: {note[:50]}...", font=("Arial", 9), text_color="gray")
                lbl_note.pack(anchor='w')

            if locked_by:
                lbl_locked = ctk.CTkLabel(info_frame, text=f"🔒 Bloqueado por {locked_by}", font=("Arial", 9), text_color="red")
                lbl_locked.pack(anchor='w')

            # Botones de acción
            btn_frame = ctk.CTkFrame(frame)
            btn_frame.pack(side='right', padx=8, pady=8)

            call_btn = ctk.CTkButton(btn_frame, text='📞 Llamar', 
                                     command=lambda p=phone: self.do_call(p),
                                     width=80, height=30)
            call_btn.pack(side='left', padx=2)

            lock_btn = ctk.CTkButton(btn_frame, text='🔒 Bloquear' if not locked_by else '🔓 Desbloquear',
                                    command=lambda id=cid, lb=locked_by: self.toggle_lock(id, lb),
                                    width=90, height=30)
            lock_btn.pack(side='left', padx=2)

        except Exception as e:
            logger.error(f'Error rendering contact card {cid}: {e}')

    def import_excel(self):
        """Importar contactos desde archivo Excel/CSV"""
        path = filedialog.askopenfilename(
            filetypes=[('Excel files', '*.xlsx;*.xls;*.csv'), ('All files', '*.*')]
        )
        if not path:
            return
        try:
            logger.info(f"Importing from: {path}")
            
            # Leer archivo
            if path.endswith('.csv'):
                df = pd.read_csv(path)
            else:
                df = pd.read_excel(path)
            
            logger.info(f"Read {len(df)} rows from file")
            
            # Construir lista de contactos
            contacts = []
            for idx, row in df.iterrows():
                try:
                    # Intentar encontrar columnas comunes
                    phone = str(row.get('phone') or row.get('telefono') or row.get('Phone') or '').strip()
                    name = str(row.get('name') or row.get('nombre') or row.get('Name') or '').strip()
                    note = str(row.get('note') or row.get('nota') or row.get('Note') or '').strip()
                    status = str(row.get('status') or row.get('estado') or 'SIN GESTIONAR').strip()
                    
                    if phone:  # Solo si hay teléfono
                        contacts.append({
                            'phone': phone,
                            'name': name or f'Contacto {phone}',
                            'note': note,
                            'status': status
                        })
                except Exception as e:
                    logger.warning(f"Error processing row {idx}: {e}")
            
            if not contacts:
                messagebox.showwarning('Advertencia', 'No se encontraron contactos válidos en el archivo')
                return
            
            logger.info(f"Importing {len(contacts)} contacts")
            r = requests.post(f'{SERVER_URL}/import', 
                            json=contacts, 
                            headers=self.headers,
                            timeout=30)
            r.raise_for_status()
            
            result = r.json()
            msg = f"Importación completada:\n- Insertados: {result.get('inserted', 0)}\n- Actualizados: {result.get('updated', 0)}"
            logger.info(msg)
            messagebox.showinfo('Importación', msg)
            self.load_contacts()
            
        except Exception as e:
            logger.error(f'Import failed: {e}')
            messagebox.showerror('Error', f'Importación fallida: {e}')

    def export_excel(self):
        """Exportar contactos a archivo Excel"""
        try:
            # Seleccionar ubicación de guardado
            path = filedialog.asksaveasfilename(
                defaultextension='.xlsx',
                filetypes=[('Excel files', '*.xlsx'), ('CSV files', '*.csv'), ('All files', '*.*')],
                initialfile=f"contactos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            )
            if not path:
                return
            
            logger.info(f"Exporting contacts to: {path}")
            
            # Descargar archivo del servidor
            r = requests.get(f'{SERVER_URL}/export', 
                            headers=self.headers,
                            timeout=30)
            r.raise_for_status()
            
            # Guardar archivo
            with open(path, 'wb') as f:
                f.write(r.content)
            
            messagebox.showinfo('Exportación', f'Contactos exportados correctamente a:\n{path}')
            logger.info(f"Export completed: {path}")
            
        except Exception as e:
            logger.error(f'Export failed: {e}')
            messagebox.showerror('Error', f'Exportación fallida: {e}')

    def do_call(self, phone):
        """Realizar llamada a través de InterPhone con reintentos y manejo de errores"""
        try:
            logger.info(f"Attempting to call: {phone}")
            
            if not self.interphone_controller:
                self.interphone_controller = InterPhoneController()
            
            # Intentar conectar (con reintentos)
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    logger.debug(f"Connect attempt {attempt + 1}/{max_retries}")
                    self.interphone_controller.connect()
                    break
                except Exception as e:
                    logger.warning(f"Connect attempt {attempt + 1} failed: {e}")
                    if attempt == max_retries - 1:
                        raise RuntimeError(f"No se pudo conectar a InterPhone después de {max_retries} intentos")
                    time.sleep(1)
            
            # Realizar llamada
            self.interphone_controller.call(phone)
            logger.info(f"Call initiated to {phone}")
            messagebox.showinfo('Llamada', f'Llamada a {phone} iniciada')
            
        except RuntimeError as e:
            logger.error(f'InterPhone not found: {e}')
            messagebox.showerror('Error InterPhone', 
                               f'No se encontró InterPhone:\n{str(e)}\n\n'
                               'Asegúrate de que InterPhone esté abierto')
        except Exception as e:
            logger.error(f'Call error: {e}')
            messagebox.showerror('Error', f'Error en la llamada: {e}')

    def toggle_lock(self, contact_id, locked_by):
        """Bloquear o desbloquear contacto"""
        try:
            logger.info(f"Toggle lock for {contact_id}, currently locked by: {locked_by}")
            
            if locked_by:
                # Desbloquear
                self.sio.emit('unlock_contact', {
                    'id': contact_id,
                    'user': 'usuario_local'  # En producción, usar usuario real
                })
                logger.info(f"Unlock request sent for {contact_id}")
            else:
                # Bloquear
                self.sio.emit('lock_contact', {
                    'id': contact_id,
                    'user': 'usuario_local',
                    'duration_minutes': 10
                })
                logger.info(f"Lock request sent for {contact_id}")
        except Exception as e:
            logger.error(f'Lock toggle error: {e}')
            messagebox.showerror('Error', f'Error toggling lock: {e}')

    def open_phone_generator(self):
        """Abre la ventana profesional de generador de números"""
        try:
            if self.generator_window is None or not self.generator_window.winfo_exists():
                self.generator_window = PhoneGeneratorWindow(
                    self,
                    SERVER_URL,
                    API_KEY
                )
                logger.info("Phone Generator window opened")
            else:
                # Si ya existe, traerla al frente
                self.generator_window.lift()
                self.generator_window.focus()
        except Exception as e:
            logger.error(f'Error opening phone generator: {e}')
            messagebox.showerror('Error', f'Error abriendo generador: {e}')

    def show_status(self):
        """Mostrar estado de la aplicación"""
        try:
            status_msg = f"""
Estado de la Aplicación
========================
Servidor: {SERVER_URL}
Socket.IO: {'Conectado' if self.sio.connected else 'Desconectado'}
Contactos: {len(self.contacts)}
InterPhone: {'Disponible' if self.interphone_controller else 'No inicializado'}

Configuración:
API Key: {API_KEY[:20]}...
"""
            messagebox.showinfo('Estado', status_msg)
        except Exception as e:
            logger.error(f'Status error: {e}')


if __name__ == '__main__':
    app = CallManagerApp()
    app.load_contacts()
    app.mainloop()

