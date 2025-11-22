"""
Guía de Integración - Nuevos Componentes
CallManager con Chat IA, Grabación de Llamadas y UI Responsiva

Versión: 1.0
Fecha: 2025-11-22
"""

# ============================================================================
# 1. INSTALACIÓN DE DEPENDENCIAS
# ============================================================================

"""
Ejecutar en terminal:

pip install customtkinter requests socketio pyaudio openpyxl

Para Ollama:
1. Descargar desde https://ollama.ai/
2. Ejecutar: ollama pull mistral
3. Verificar: ollama serve (en otra terminal)
"""

# ============================================================================
# 2. ARCHIVOS NUEVOS CREADOS
# ============================================================================

"""
✅ client/chat_assistant.py
   - OllamaClient: Cliente para comunicarse con Ollama
   - ChatAssistant: Asistente de chat con historial
   
✅ client/call_recorder.py
   - CallRecorder: Grabador de audio WAV con metadata
   - Métodos: start_recording(), stop_recording(), list_recordings()
   
✅ client/ui/responsive_ui.py
   - ResponsiveFrame: Frame base adaptativo
   - ContactEditorWidget: Editor inline de contactos
   - ExcelExporter: Exportación a Excel
   - MobileContactsView: Vista optimizada para móviles
   - KEYBOARD_SHORTCUTS: Mapa de atajos de teclado
   
✅ client/ui/chat_widget.py
   - ChatBox: Widget de chat integrable
   - ChatWindow: Ventana flotante de chat
   - ChatMessage: Mensaje individual
   - ObjetionHandler: Manejador de objeciones comunes
"""

# ============================================================================
# 3. MODIFICACIONES EN call_manager_app.py
# ============================================================================

"""
A) AGREGAR IMPORTS (después de línea 60):

from chat_assistant import initialize_chat_assistant, get_chat_assistant
from call_recorder import initialize_call_recorder, get_call_recorder
from ui.responsive_ui import (
    ContactEditorWidget, ExcelExporter, MobileContactsView,
    setup_keyboard_shortcuts
)
from ui.chat_widget import ChatBox, ChatWindow, ObjetionHandler
"""

# ============================================================================
# 4. EN __init__ DE CallManagerApp (alrededor de línea 400)
# ============================================================================

"""
Agregar después de inicializar tracking:

# Inicializar Chat IA
try:
    self.chat_assistant = initialize_chat_assistant()
    self.chat_assistant_available = True
    logger.info("💬 Chat Assistant inicializado")
except:
    self.chat_assistant_available = False
    logger.warning("⚠️ Chat Assistant no disponible")

# Inicializar Grabador de Llamadas
try:
    self.call_recorder = initialize_call_recorder("recordings")
    self.recording_active = False
    self.current_recording_id = None
    logger.info("🎙️ Call Recorder inicializado")
except Exception as e:
    logger.warning(f"⚠️ Call Recorder no disponible: {e}")

# Configurar atajos de teclado
setup_keyboard_shortcuts(self, self._handle_keyboard_action)
"""

# ============================================================================
# 5. NUEVOS MÉTODOS A AGREGAR EN CallManagerApp
# ============================================================================

"""
# Mostrar Chat IA flotante
def show_chat_assistant(self):
    chat_window = ChatWindow(
        self,
        on_send_message=self._chat_message_handler,
        title="💬 Asistente IA - Manejo de Objeciones"
    )
    return chat_window

# Handler de mensajes del chat
def _chat_message_handler(self, message: str) -> str:
    if not self.chat_assistant_available:
        return "❌ Chat Assistant no disponible. Verifica que Ollama esté ejecutándose."
    
    # Contexto de la llamada actual
    context = ""
    if hasattr(self, 'selected_contact') and self.selected_contact:
        context = f"Cliente: {self.selected_contact.get('name')}, Teléfono: {self.selected_contact.get('phone')}"
    
    response = self.chat_assistant.ask(message, context)
    return response if response else "❌ No se pudo generar respuesta"

# Iniciar grabación de llamada
def start_call_recording(self, contact_name: str, contact_phone: str):
    if not hasattr(self, 'call_recorder'):
        return
    
    recording_id = self.call_recorder.start_recording(
        contact_name=contact_name,
        contact_phone=contact_phone,
        user_id=self.current_user_id,
        user_name=self.current_username,
        call_id=f"call_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )
    
    if recording_id:
        self.recording_active = True
        self.current_recording_id = recording_id
        logger.info(f"🔴 Grabación iniciada: {recording_id}")

# Detener grabación de llamada
def stop_call_recording(self):
    if not hasattr(self, 'call_recorder') or not self.recording_active:
        return
    
    metadata = self.call_recorder.stop_recording()
    if metadata:
        logger.info(f"⏹️ Grabación completada: {metadata.get('recording_id')}")
        messagebox.showinfo("Grabación", f"Llamada grabada exitosamente\\n"
                          f"Duración: {metadata.get('duration_seconds')}s\\n"
                          f"Tamaño: {metadata.get('file_size_bytes')/(1024*1024):.2f}MB")
    
    self.recording_active = False
    self.current_recording_id = None

# Handler de atajos de teclado
def _handle_keyboard_action(self, action: str):
    if action == 'new_contact':
        self.add_contact()
    elif action == 'export_excel':
        self.export_contacts_to_excel()
    elif action == 'search':
        self.focus_search()
    elif action == 'call':
        self.call_selected_contact()
    elif action == 'edit':
        self.edit_selected_contact()
    elif action == 'delete_confirm':
        self.delete_contact_with_confirmation()
    elif action == 'cancel':
        self.cancel_operation()

# Exportar contactos a Excel
def export_contacts_to_excel(self):
    if not hasattr(self, 'contacts') or not self.contacts:
        messagebox.showwarning("Exportar", "No hay contactos para exportar")
        return
    
    file_path = filedialog.asksaveasfilename(
        defaultextension=".xlsx",
        filetypes=[("Excel files", "*.xlsx")]
    )
    
    if file_path:
        success = ExcelExporter.export_contacts(self.contacts, file_path)
        if success:
            messagebox.showinfo("Éxito", f"Contactos exportados a:\\n{file_path}")
        else:
            messagebox.showerror("Error", "No se pudieron exportar los contactos")

# Ver grabaciones de llamadas
def show_recordings(self):
    if not hasattr(self, 'call_recorder'):
        messagebox.showerror("Error", "Sistema de grabación no disponible")
        return
    
    recordings = self.call_recorder.list_recordings(self.current_user_id)
    
    if not recordings:
        messagebox.showinfo("Grabaciones", "No hay grabaciones disponibles")
        return
    
    # Crear ventana de grabaciones
    rec_window = ctk.CTkToplevel(self)
    rec_window.title("📹 Grabaciones de Llamadas")
    rec_window.geometry("900x500")
    
    # Tabla de grabaciones
    tree_frame = ctk.CTkFrame(rec_window)
    tree_frame.pack(fill='both', expand=True, padx=10, pady=10)
    
    from tkinter import ttk
    columns = ('Contacto', 'Fecha', 'Duración', 'Tamaño')
    tree = ttk.Treeview(tree_frame, columns=columns, height=15)
    tree.column('#0', width=150)
    tree.column('Contacto', width=150)
    tree.column('Fecha', width=150)
    tree.column('Duración', width=100)
    tree.column('Tamaño', width=100)
    
    tree.heading('#0', text='ID')
    tree.heading('Contacto', text='Contacto')
    tree.heading('Fecha', text='Fecha')
    tree.heading('Duración', text='Duración (s)')
    tree.heading('Tamaño', text='Tamaño (MB)')
    
    for rec in recordings:
        tree.insert('', 'end', text=rec.get('recording_id', ''),
                   values=(
                       rec.get('contact_name'),
                       rec.get('start_time', '')[:10],
                       rec.get('duration_seconds'),
                       f"{rec.get('file_size_bytes', 0)/(1024*1024):.2f}"
                   ))
    
    tree.pack(fill='both', expand=True)
    
    # Botones
    button_frame = ctk.CTkFrame(rec_window)
    button_frame.pack(fill='x', padx=10, pady=10)
    
    def export_recordings():
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")]
        )
        if file_path:
            ExcelExporter.export_recordings(recordings, file_path)
            messagebox.showinfo("Éxito", f"Grabaciones exportadas a:\\n{file_path}")
    
    ctk.CTkButton(button_frame, text="📥 Exportar a Excel", command=export_recordings).pack(
        side='left', padx=5
    )
"""

# ============================================================================
# 6. MODIFICAR MÉTODO call_contact()
# ============================================================================

"""
Antes de realizar la llamada, agregar:

# Iniciar grabación
if hasattr(self, 'call_recorder'):
    self.start_call_recording(
        contact_name=contact.get('name', 'Unknown'),
        contact_phone=contact.get('phone', '')
    )

# ... resto del código de llamada ...

# Al terminar la llamada, agregar:
if hasattr(self, 'call_recorder'):
    self.stop_call_recording()
"""

# ============================================================================
# 7. ACTUALIZAR BARRA DE MENÚ
# ============================================================================

"""
En el método que crea el menú, agregar:

# Menú Herramientas
tools_menu = tkinter.Menu(menubar, tearoff=0)
menubar.add_cascade(label="Herramientas", menu=tools_menu)

tools_menu.add_command(
    label="💬 Asistente IA (Ctrl+A)",
    command=self.show_chat_assistant
)
tools_menu.add_command(
    label="📹 Ver Grabaciones",
    command=self.show_recordings
)
tools_menu.add_separator()
tools_menu.add_command(
    label="📊 Exportar Contactos (Ctrl+E)",
    command=self.export_contacts_to_excel
)
"""

# ============================================================================
# 8. COMPATIBILIDAD CON MÓVILES/TABLETS
# ============================================================================

"""
Para hacer la app responsive:

A) En __init__, detectar tamaño de pantalla:

screen_width = self.winfo_screenwidth()
self.is_mobile = screen_width < 768
self.is_tablet = 768 <= screen_width < 1024

B) Usar ResponsiveFrame en lugar de ctk.CTkFrame para layouts adaptables

C) Las vistas se adaptan automáticamente según el tamaño:
   - Móvil (<768px): Una columna, botones grandes
   - Tablet (768-1024px): Dos columnas
   - Desktop (>1024px): Interfaz completa
"""

# ============================================================================
# 9. CONFIGURACIÓN DE requirements.txt
# ============================================================================

"""
Agregar a requirements.txt:

# Chat IA
requests>=2.31.0

# Grabación de Llamadas
pyaudio>=0.2.13

# Exportación Excel
openpyxl>=3.11.0

# Valores ya existentes:
customtkinter>=5.0.0
socketio>=5.9.0
python-socketio>=5.9.0
"""

# ============================================================================
# 10. EJEMPLO DE USO COMPLETO
# ============================================================================

"""
# Flujo de trabajo para un agente:

1. Abrir CallManager
2. Buscar/Seleccionar contacto
3. Click "📞 Llamar"
   - Se inicia grabación automática
   - Se inicia rastreo de tiempo
4. Durante la llamada:
   - Si hay objeción: Ctrl+A → Abrir Chat IA
   - Chat IA sugiere argumentos/respuestas
5. Al terminar:
   - Confirmar datos de contacto
   - Agregar notas (max 244 caracteres)
   - Cambiar estado
6. Exportar reportes:
   - Contactos: Ctrl+E (Excel)
   - Grabaciones: Herramientas → Ver Grabaciones
   - Métricas: Ver dashboard

Atajos de teclado:
- Ctrl+N: Nuevo contacto
- Ctrl+E: Exportar Excel
- Ctrl+F: Buscar
- Ctrl+C: Llamar
- F2: Editar
- Delete: Eliminar
- Escape: Cancelar
- Ctrl+A: Asistente IA
"""

# ============================================================================
# 11. ESTRUCTURA DE DIRECTORIOS FINAL
# ============================================================================

"""
callmanager/
├── client/
│   ├── call_manager_app.py (modificado)
│   ├── call_tracking.py ✅
│   ├── call_recorder.py ✨ NUEVO
│   ├── chat_assistant.py ✨ NUEVO
│   ├── config_loader.py
│   ├── interphone_controller.py
│   ├── call_providers.py
│   └── ui/
│       ├── metrics_dashboard.py
│       ├── responsive_ui.py ✨ NUEVO
│       └── chat_widget.py ✨ NUEVO
├── recordings/ (creado automáticamente)
└── requirements.txt (actualizado)
"""

# ============================================================================
# 12. TESTING
# ============================================================================

"""
Para probar cada componente:

A) Chat IA:
   - Ejecutar: python -c "from client.chat_assistant import *; initialize_chat_assistant()"
   - O en app: Ctrl+A para abrir chat

B) Grabación de Llamadas:
   - Llamar a un contacto
   - Verificar que se cree archivo en /recordings/

C) UI Responsiva:
   - Redimensionar ventana de la app
   - Verificar que los layouts se adapten

D) Exportación Excel:
   - Ctrl+E para exportar contactos
   - Verificar archivo generado
"""

print(__doc__)
