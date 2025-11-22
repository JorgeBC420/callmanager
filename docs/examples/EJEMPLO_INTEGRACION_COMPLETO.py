"""
Ejemplo Completo de Integración - CallManager v2.5
Muestra cómo integrar Chat IA, Grabación y UI Responsiva

Autor: CallManager System
Versión: 1.0
Fecha: 2025-11-22

INSTRUCCIONES:
1. Ver este archivo para entender la integración
2. Copiar y pegar el código en call_manager_app.py
3. Seguir los comentarios ### PASO X ###
"""

# ============================================================================
# PASO 1: AGREGAR IMPORTS (después de línea 60)
# ============================================================================

"""
Agregar estas líneas después de los imports existentes:

# Chat IA
from chat_assistant import initialize_chat_assistant, get_chat_assistant
from call_recorder import initialize_call_recorder, get_call_recorder

# UI Responsiva
from ui.responsive_ui import (
    ContactEditorWidget, ExcelExporter, MobileContactsView,
    setup_keyboard_shortcuts, ResponsiveFrame
)

# Chat Widget
from ui.chat_widget import ChatBox, ChatWindow, ObjetionHandler
"""

# ============================================================================
# PASO 2: AGREGAR EN __init__ (buscar la clase CallManagerApp)
# ============================================================================

"""
En def __init__(self, root):
    
    Después de inicializar call_tracker, agregar:
    
    # ========== INICIALIZAR CHAT IA ==========
    try:
        self.chat_assistant = initialize_chat_assistant()
        self.chat_assistant_available = True
        logger.info("💬 Chat Assistant inicializado")
        # Callback para mensajes del chat
        if self.chat_assistant:
            self.chat_assistant.set_response_callback(self._on_chat_response)
    except Exception as e:
        self.chat_assistant = None
        self.chat_assistant_available = False
        logger.warning(f"⚠️ Chat Assistant no disponible: {e}")
    
    # ========== INICIALIZAR GRABADOR DE LLAMADAS ==========
    try:
        self.call_recorder = initialize_call_recorder("recordings")
        self.recording_active = False
        self.current_recording_id = None
        logger.info("🎙️ Call Recorder inicializado")
    except Exception as e:
        self.call_recorder = None
        logger.warning(f"⚠️ Call Recorder no disponible: {e}")
    
    # ========== VARIABLES DE RESPONSIVE ==========
    self.screen_width = root.winfo_screenwidth()
    self.screen_height = root.winfo_screenheight()
    self.is_mobile = self.screen_width < 768
    self.is_tablet = 768 <= self.screen_width < 1024
    self.is_desktop = self.screen_width >= 1024
    
    logger.info(f"📱 Modo detectado: {'Mobile' if self.is_mobile else 'Tablet' if self.is_tablet else 'Desktop'}")
    
    # ========== CONFIGURAR ATAJOS DE TECLADO ==========
    try:
        setup_keyboard_shortcuts(root, self._handle_keyboard_action)
        logger.info("⌨️ Atajos de teclado configurados")
    except Exception as e:
        logger.warning(f"⚠️ Atajos de teclado: {e}")
"""

# ============================================================================
# PASO 3: AGREGAR MÉTODOS NUEVOS AL FINAL DE LA CLASE
# ============================================================================

"""
Agregar estos métodos al final de la clase CallManagerApp:

# ========== CHAT IA ==========

def show_chat_assistant(self):
    '''Mostrar ventana flotante de chat'''
    if not self.chat_assistant_available:
        messagebox.showerror(
            "Error",
            "Chat Assistant no disponible.\\n"
            "Verifica que Ollama esté ejecutándose.\\n"
            "Descarga desde: https://ollama.ai/"
        )
        return
    
    # Crear ventana de chat
    chat_window = ChatWindow(
        self,
        on_send_message=self._chat_message_handler,
        title="💬 Asistente IA - Manejo de Objeciones",
        width=500,
        height=600
    )
    return chat_window

def _chat_message_handler(self, message: str) -> str:
    '''Handler para procesar mensajes del chat'''
    if not self.chat_assistant_available or not message:
        return "❌ Error procesando solicitud"
    
    try:
        # Obtener contexto de la llamada actual
        context = ""
        
        if hasattr(self, 'selected_contact') and self.selected_contact:
            contact = self.selected_contact
            context = f"Cliente: {contact.get('name', 'Unknown')}, "
            context += f"Teléfono: {contact.get('phone', 'N/A')}"
        
        # Solicitar respuesta al IA
        response = self.chat_assistant.ask(message, context, run_async=False)
        
        if response:
            return response
        else:
            return "❌ No se pudo generar respuesta. Intenta de nuevo."
    
    except Exception as e:
        logger.error(f"Error en chat: {e}")
        return f"❌ Error: {str(e)[:100]}"

def _on_chat_response(self, response: str):
    '''Callback cuando el chat recibe respuesta (async)'''
    logger.info(f"Chat response: {response[:50]}...")

# ========== GRABACIÓN DE LLAMADAS ==========

def start_call_recording(self, contact_name: str, contact_phone: str):
    '''Iniciar grabación de una llamada'''
    if not hasattr(self, 'call_recorder') or self.call_recorder is None:
        logger.warning("Call recorder no disponible")
        return
    
    try:
        # Generar ID de llamada único
        call_id = f"call_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Obtener datos del usuario actual
        user_id = getattr(self, 'current_user_id', 'unknown')
        user_name = getattr(self, 'current_username', 'Unknown Agent')
        
        # Iniciar grabación
        recording_id = self.call_recorder.start_recording(
            contact_name=contact_name or "Unknown",
            contact_phone=contact_phone or "N/A",
            user_id=user_id,
            user_name=user_name,
            call_id=call_id
        )
        
        if recording_id:
            self.recording_active = True
            self.current_recording_id = recording_id
            logger.info(f"🔴 Grabación iniciada: {recording_id}")
            return True
        
        return False
    
    except Exception as e:
        logger.error(f"Error iniciando grabación: {e}")
        return False

def stop_call_recording(self):
    '''Detener la grabación actual'''
    if not hasattr(self, 'call_recorder') or self.call_recorder is None:
        return
    
    if not self.recording_active:
        return
    
    try:
        # Detener grabación
        metadata = self.call_recorder.stop_recording()
        
        if metadata:
            duration = metadata.get('duration_seconds', 0)
            size_mb = metadata.get('file_size_bytes', 0) / (1024 * 1024)
            
            logger.info(f"⏹️ Grabación completada: {metadata.get('recording_id')}")
            logger.info(f"   Duración: {duration}s, Tamaño: {size_mb:.2f}MB")
            
            # Mostrar notificación
            messagebox.showinfo(
                "Grabación Completada",
                f"Llamada grabada exitosamente\\n\\n"
                f"Duración: {duration} segundos\\n"
                f"Tamaño: {size_mb:.2f} MB"
            )
        
        self.recording_active = False
        self.current_recording_id = None
    
    except Exception as e:
        logger.error(f"Error deteniendo grabación: {e}")

def show_recordings_window(self):
    '''Mostrar ventana con todas las grabaciones'''
    if not hasattr(self, 'call_recorder') or self.call_recorder is None:
        messagebox.showerror("Error", "Sistema de grabación no disponible")
        return
    
    try:
        # Obtener grabaciones del usuario actual
        user_id = getattr(self, 'current_user_id', None)
        recordings = self.call_recorder.list_recordings(user_id)
        
        if not recordings:
            messagebox.showinfo("Grabaciones", "No hay grabaciones disponibles")
            return
        
        # Crear ventana
        rec_window = ctk.CTkToplevel(self)
        rec_window.title("📹 Grabaciones de Llamadas")
        rec_window.geometry("1000x600")
        
        # --- Header ---
        header_frame = ctk.CTkFrame(rec_window, fg_color="#1f1f1f")
        header_frame.pack(fill='x', padx=10, pady=10)
        
        ctk.CTkLabel(
            header_frame,
            text=f"📹 Total: {len(recordings)} grabaciones",
            font=("Arial", 13, "bold")
        ).pack(anchor='w')
        
        # --- Tabla de grabaciones ---
        from tkinter import ttk
        
        table_frame = ctk.CTkFrame(rec_window)
        table_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        columns = ('ID', 'Contacto', 'Fecha', 'Duración', 'Tamaño')
        tree = ttk.Treeview(table_frame, columns=columns, height=15)
        
        tree.column('#0', width=0, stretch='no')
        tree.column('ID', width=200)
        tree.column('Contacto', width=150)
        tree.column('Fecha', width=150)
        tree.column('Duración', width=100)
        tree.column('Tamaño', width=100)
        
        tree.heading('#0', text='', anchor='w')
        tree.heading('ID', text='ID Grabación', anchor='w')
        tree.heading('Contacto', text='Contacto', anchor='w')
        tree.heading('Fecha', text='Fecha', anchor='w')
        tree.heading('Duración', text='Segundos', anchor='w')
        tree.heading('Tamaño', text='MB', anchor='w')
        
        # Agregar datos
        for recording in recordings:
            start_time = recording.get('start_time', '')[:10]
            duration = recording.get('duration_seconds', 0)
            size_mb = f"{recording.get('file_size_bytes', 0)/(1024*1024):.2f}"
            
            tree.insert('', 'end',
                       values=(
                           recording.get('recording_id', ''),
                           recording.get('contact_name', ''),
                           start_time,
                           duration,
                           size_mb
                       ))
        
        tree.pack(fill='both', expand=True)
        
        # --- Botones ---
        button_frame = ctk.CTkFrame(rec_window)
        button_frame.pack(fill='x', padx=10, pady=10)
        
        def export_recordings():
            '''Exportar grabaciones a Excel'''
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
            )
            
            if file_path:
                success = ExcelExporter.export_recordings(recordings, file_path)
                if success:
                    messagebox.showinfo(
                        "Éxito",
                        f"Grabaciones exportadas a:\\n{file_path}"
                    )
                else:
                    messagebox.showerror("Error", "No se pudieron exportar las grabaciones")
        
        def delete_selected():
            '''Eliminar grabación seleccionada'''
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Seleccionar", "Selecciona una grabación")
                return
            
            item = tree.item(selected[0])
            recording_id = item['values'][0]
            
            if messagebox.askyesno("Confirmar", f"¿Eliminar grabación {recording_id}?"):
                if self.call_recorder.delete_recording(recording_id):
                    tree.delete(selected[0])
                    messagebox.showinfo("Éxito", "Grabación eliminada")
                else:
                    messagebox.showerror("Error", "No se pudo eliminar")
        
        ctk.CTkButton(
            button_frame,
            text="📥 Exportar a Excel",
            command=export_recordings,
            fg_color="#4CAF50"
        ).pack(side='left', padx=5)
        
        ctk.CTkButton(
            button_frame,
            text="🗑️ Eliminar Seleccionada",
            command=delete_selected,
            fg_color="#FF6B6B"
        ).pack(side='left', padx=5)
        
        ctk.CTkButton(
            button_frame,
            text="❌ Cerrar",
            command=rec_window.destroy
        ).pack(side='left', padx=5)
    
    except Exception as e:
        logger.error(f"Error mostrando grabaciones: {e}")
        messagebox.showerror("Error", f"Error: {str(e)}")

# ========== EXPORTACIÓN A EXCEL ==========

def export_contacts_to_excel(self):
    '''Exportar contactos a Excel'''
    if not hasattr(self, 'contacts') or not self.contacts:
        messagebox.showwarning(
            "Exportar",
            "No hay contactos para exportar"
        )
        return
    
    try:
        # Pedir ubicación
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            initialfile=f"contactos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        )
        
        if not file_path:
            return
        
        # Exportar
        success = ExcelExporter.export_contacts(self.contacts, file_path)
        
        if success:
            messagebox.showinfo(
                "Exportación Exitosa",
                f"✅ Contactos exportados a:\\n\\n{file_path}"
            )
            logger.info(f"Contactos exportados a: {file_path}")
        else:
            messagebox.showerror("Error", "No se pudieron exportar los contactos")
    
    except Exception as e:
        logger.error(f"Error exportando: {e}")
        messagebox.showerror("Error", f"Error: {str(e)}")

# ========== ATAJOS DE TECLADO ==========

def _handle_keyboard_action(self, action: str):
    '''Manejar acciones desde atajos de teclado'''
    try:
        if action == 'new_contact':
            self.add_contact()
        
        elif action == 'export_excel':
            self.export_contacts_to_excel()
        
        elif action == 'search':
            # Enfocar en search si existe
            if hasattr(self, 'search_entry'):
                self.search_entry.focus()
        
        elif action == 'call':
            # Llamar al contacto seleccionado
            if hasattr(self, 'selected_contact') and self.selected_contact:
                self.call_contact(self.selected_contact)
        
        elif action == 'edit':
            # Editar contacto seleccionado
            if hasattr(self, 'selected_contact') and self.selected_contact:
                self.edit_contact(self.selected_contact)
        
        elif action == 'delete_confirm':
            # Eliminar con confirmación
            if hasattr(self, 'selected_contact') and self.selected_contact:
                if messagebox.askyesno("Confirmar", "¿Eliminar contacto?"):
                    self.delete_contact(self.selected_contact)
        
        elif action == 'cancel':
            # Cancelar operación actual
            pass
    
    except Exception as e:
        logger.error(f"Error en acción de teclado: {e}")

# ========== MÉTODOS PARA LLAMADAS MODIFICADOS ==========

def call_contact(self, contact):
    '''
    MODIFICADO: Llamar a contacto
    Ahora inicia grabación automáticamente
    '''
    if not contact:
        messagebox.showwarning("Error", "Selecciona un contacto")
        return
    
    # Iniciar grabación
    if hasattr(self, 'call_recorder') and self.call_recorder:
        self.start_call_recording(
            contact_name=contact.get('name', 'Unknown'),
            contact_phone=contact.get('phone', 'N/A')
        )
    
    # ... RESTO DEL CÓDIGO ORIGINAL DE call_contact ...
    
    # Al terminar la llamada, agregar:
    # self.stop_call_recording()

# ========== MÉTODOS HELPER ==========

def _detect_screen_size(self):
    '''Detectar tamaño de pantalla y modo responsivo'''
    self.screen_width = self.root.winfo_screenwidth()
    self.screen_height = self.root.winfo_screenheight()
    
    self.is_mobile = self.screen_width < 768
    self.is_tablet = 768 <= self.screen_width < 1024
    self.is_desktop = self.screen_width >= 1024
    
    mode = "Mobile" if self.is_mobile else "Tablet" if self.is_tablet else "Desktop"
    logger.info(f"📱 Screen size: {self.screen_width}x{self.screen_height} ({mode})")
"""

# ============================================================================
# PASO 4: AGREGAR AL MENÚ
# ============================================================================

"""
Si tienes una barra de menú, agregar:

# En el método que crea el menú principal:

# Menú Herramientas (nuevo)
tools_menu = tkinter.Menu(menubar, tearoff=0)
menubar.add_cascade(label="Herramientas", menu=tools_menu)

tools_menu.add_command(
    label="💬 Asistente IA (Ctrl+A)",
    command=self.show_chat_assistant,
    accelerator="Ctrl+A"
)
tools_menu.add_command(
    label="📹 Ver Grabaciones",
    command=self.show_recordings_window
)
tools_menu.add_separator()
tools_menu.add_command(
    label="📊 Exportar Contactos (Ctrl+E)",
    command=self.export_contacts_to_excel,
    accelerator="Ctrl+E"
)
"""

# ============================================================================
# PASO 5: MODIFICAR call_contact()
# ============================================================================

"""
Buscar la función def call_contact(self, contact):

Agregar al INICIO (después de validaciones):

    # Iniciar grabación de llamada
    if hasattr(self, 'call_recorder') and self.call_recorder:
        self.start_call_recording(
            contact_name=contact.get('name', 'Unknown'),
            contact_phone=contact.get('phone', 'N/A')
        )

Agregar al FINAL (después de terminar la llamada):

    # Detener grabación
    if hasattr(self, 'call_recorder'):
        self.stop_call_recording()
"""

# ============================================================================
# PASO 6: MODIFICAR end_current_call()
# ============================================================================

"""
Buscar la función def end_current_call(self):

Agregar al FINAL:

    # Detener grabación si está activa
    if hasattr(self, 'call_recorder'):
        self.stop_call_recording()
"""

# ============================================================================
# EJEMPLO DE USO COMPLETO
# ============================================================================

"""
FLUJO COMPLETO DE UN AGENTE:

1. Abrir CallManager
   ✓ Chat Assistant inicializado
   ✓ Call Recorder inicializado
   ✓ Atajos de teclado configurados

2. Buscar contacto "Juan Pérez"
   - Presionar Ctrl+F
   - Escribir "Juan"
   - Hacer click en el contacto

3. Hacer llamada
   - Click en "📞 Llamar"
   - Sistema AUTOMÁTICAMENTE:
     * Inicia grabación
     * Inicia rastreo de tiempo
     * Muestra timer

4. Durante la llamada
   - Cliente dice: "Es muy caro"
   - Agente presiona Ctrl+A
   - Se abre Chat IA flotante
   - Agente escribe: "El cliente dice que es muy caro"
   - Chat IA responde: "El precio es competitivo..."
   - Agente usa la sugerencia

5. Terminar llamada
   - Click en "✓ Confirmar"
   - Sistema AUTOMÁTICAMENTE:
     * Para grabación
     * Calcula duración
     * Guarda metadata

6. Exportar reportes
   - Presionar Ctrl+E para exportar contactos
   - O ir a Herramientas → Ver Grabaciones
   - Click en "📥 Exportar a Excel"
   - Obtiene reporte en Excel
"""

print(__doc__)
