"""
Chat Widget para CallManager - Interfaz de usuario para Chat con IA
Componente integrado para mostrar chat de objeciones/ayuda en llamadas

Autor: CallManager System
Versión: 1.0
"""

import customtkinter as ctk
from tkinter import ttk
import logging
from typing import Optional, Callable, Dict
from datetime import datetime
import threading

logger = logging.getLogger(__name__)


class ChatMessage(ctk.CTkFrame):
    """Widget para un mensaje de chat individual"""
    
    def __init__(self, master, message: str, is_user: bool = True, **kwargs):
        super().__init__(master, **kwargs)
        
        self.is_user = is_user
        bg_color = "#4CAF50" if is_user else "#2196F3"
        text_color = "white"
        
        # Crear frame del mensaje
        msg_frame = ctk.CTkFrame(
            self,
            fg_color=bg_color,
            corner_radius=12
        )
        msg_frame.pack(
            fill='x',
            pady=5,
            padx=10,
            anchor='e' if is_user else 'w'
        )
        
        # Texto del mensaje
        label = ctk.CTkLabel(
            msg_frame,
            text=message,
            font=("Arial", 11),
            text_color=text_color,
            wraplength=400,
            justify='left'
        )
        label.pack(padx=12, pady=8)


class ChatBox(ctk.CTkFrame):
    """Widget de chat para interacción con IA"""
    
    def __init__(
        self,
        master,
        on_send_message: Callable = None,
        **kwargs
    ):
        super().__init__(master, **kwargs)
        
        self.on_send_message = on_send_message
        self.chat_history = []
        self.is_loading = False
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Crear widgets del chat"""
        
        # --- Header ---
        header = ctk.CTkFrame(self, fg_color="#1f1f1f")
        header.pack(fill='x', padx=10, pady=10)
        
        ctk.CTkLabel(
            header,
            text="💬 Asistente IA - Manejo de Objeciones",
            font=("Arial", 13, "bold")
        ).pack(anchor='w')
        
        ctk.CTkLabel(
            header,
            text="Haz preguntas para ayuda durante la llamada",
            font=("Arial", 9),
            text_color="gray"
        ).pack(anchor='w')
        
        # --- Área de mensajes (scrollable) ---
        self.chat_display = ctk.CTkScrollableFrame(
            self,
            fg_color="#2b2b2b"
        )
        self.chat_display.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Mensaje inicial
        welcome_msg = ctk.CTkFrame(self.chat_display, fg_color="transparent")
        welcome_msg.pack(fill='x', pady=20)
        
        ctk.CTkLabel(
            welcome_msg,
            text="🤖 Hola, soy tu asistente de IA",
            font=("Arial", 11, "bold"),
            text_color="#4CAF50"
        ).pack()
        
        ctk.CTkLabel(
            welcome_msg,
            text="Puedo ayudarte a:\n• Responder objeciones\n• Argumentos de venta\n• Respuestas a preguntas",
            font=("Arial", 10),
            text_color="gray"
        ).pack(pady=10)
        
        # --- Input area ---
        input_frame = ctk.CTkFrame(self)
        input_frame.pack(fill='x', padx=10, pady=10)
        
        self.input_field = ctk.CTkEntry(
            input_frame,
            placeholder_text="Escribe tu pregunta u objeción...",
            font=("Arial", 11),
            height=40
        )
        self.input_field.pack(side='left', fill='both', expand=True, padx=(0, 10))
        self.input_field.bind('<Return>', self._on_send)
        
        self.send_btn = ctk.CTkButton(
            input_frame,
            text="Enviar",
            font=("Arial", 11, "bold"),
            width=80,
            height=40,
            command=self._on_send
        )
        self.send_btn.pack(side='left')
        
        # --- Status bar ---
        status_frame = ctk.CTkFrame(self, fg_color="#1f1f1f")
        status_frame.pack(fill='x', padx=10, pady=5)
        
        self.status_label = ctk.CTkLabel(
            status_frame,
            text="✅ Asistente listo",
            font=("Arial", 9),
            text_color="#4CAF50"
        )
        self.status_label.pack(anchor='w')
    
    def _on_send(self, event=None):
        """Enviar mensaje al asistente"""
        message = self.input_field.get().strip()
        
        if not message:
            return
        
        # Mostrar mensaje del usuario
        self._add_message(message, is_user=True)
        self.input_field.delete(0, 'end')
        
        # Deshabilitar input mientras procesa
        self.send_btn.configure(state='disabled')
        self.input_field.configure(state='disabled')
        self.is_loading = True
        self.status_label.configure(text="⏳ Pensando...", text_color="#FFC107")
        
        # Procesar en thread separado
        if self.on_send_message:
            thread = threading.Thread(
                target=self._process_message,
                args=(message,),
                daemon=True
            )
            thread.start()
    
    def _process_message(self, message: str):
        """Procesar mensaje (thread separado)"""
        try:
            if self.on_send_message:
                response = self.on_send_message(message)
                
                # Agregar respuesta al chat (desde el main thread)
                self.after(0, lambda: self._add_message(response, is_user=False))
                self.after(0, lambda: self._set_ready())
        except Exception as e:
            logger.error(f"Error procesando mensaje: {e}")
            self.after(0, lambda: self._set_error(str(e)))
    
    def _add_message(self, message: str, is_user: bool = True):
        """Agregar mensaje al chat"""
        msg_widget = ChatMessage(
            self.chat_display,
            message,
            is_user=is_user,
            fg_color="transparent"
        )
        
        self.chat_history.append({
            'message': message,
            'is_user': is_user,
            'timestamp': datetime.now().isoformat()
        })
        
        # Scroll al final
        self.chat_display._parent_canvas.yview_moveto(1)
    
    def _set_ready(self):
        """Asistente listo"""
        self.is_loading = False
        self.send_btn.configure(state='normal')
        self.input_field.configure(state='normal')
        self.status_label.configure(text="✅ Asistente listo", text_color="#4CAF50")
        self.input_field.focus()
    
    def _set_error(self, error_msg: str):
        """Error al procesar"""
        self.is_loading = False
        self.send_btn.configure(state='normal')
        self.input_field.configure(state='normal')
        self.status_label.configure(
            text=f"❌ Error: {error_msg[:50]}",
            text_color="#FF6B6B"
        )
        
        self._add_message(
            f"❌ Error: {error_msg}",
            is_user=False
        )
    
    def clear_chat(self):
        """Limpiar historial de chat"""
        self.chat_history.clear()
        
        # Limpiar display
        for widget in self.chat_display.winfo_children():
            widget.destroy()
        
        # Mostrar mensaje de bienvenida nuevamente
        welcome_msg = ctk.CTkFrame(self.chat_display, fg_color="transparent")
        welcome_msg.pack(fill='x', pady=20)
        
        ctk.CTkLabel(
            welcome_msg,
            text="🤖 Chat limpiado",
            font=("Arial", 11, "bold"),
            text_color="#4CAF50"
        ).pack()
        
        logger.info("📝 Chat limpiado")
    
    def get_history(self) -> list:
        """Obtener historial de chat"""
        return self.chat_history.copy()


class ChatWindow(ctk.CTkToplevel):
    """Ventana flotante de chat"""
    
    def __init__(
        self,
        master,
        on_send_message: Callable = None,
        title: str = "Asistente IA",
        width: int = 500,
        height: int = 600
    ):
        super().__init__(master)
        self.title(title)
        self.geometry(f"{width}x{height}")
        
        # Frame principal
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill='both', expand=True)
        
        # Chat
        self.chat_box = ChatBox(
            main_frame,
            on_send_message=on_send_message
        )
        self.chat_box.pack(fill='both', expand=True)
        
        # Toolbar
        toolbar = ctk.CTkFrame(main_frame, fg_color="#1f1f1f")
        toolbar.pack(fill='x', padx=10, pady=10)
        
        clear_btn = ctk.CTkButton(
            toolbar,
            text="🗑️ Limpiar Chat",
            font=("Arial", 10),
            command=self.chat_box.clear_chat,
            width=100
        )
        clear_btn.pack(side='left', padx=5)
        
        self.geometry("+200+200")  # Posición inicial


class ObjetionHandler:
    """Manejador de objeciones común"""
    
    COMMON_OBJECTIONS = {
        'precio': [
            'El precio es competitivo considerando el valor que proporciona',
            'Ofrecemos planes de pago flexible',
            'El ROI justifica la inversión inicial'
        ],
        'no necesito': [
            'Muchos clientes pensaban igual antes de probar',
            'Nuestro producto resuelve X problema específico',
            'Te invito a una demostración sin compromiso'
        ],
        'competencia': [
            'Nuestro diferenciador es X característica',
            'Ofrecemos mejor soporte que la competencia',
            'Tenemos más clientes satisfechos'
        ],
        'tiempo': [
            'Puedo agendar un follow-up en otro momento',
            'Solo necesito 5 minutos para mostrar lo importante',
            'Los beneficios valen la inversión de tiempo'
        ]
    }
    
    @staticmethod
    def get_suggestion(objection_type: str) -> str:
        """Obtener sugerencia para una objeción"""
        suggestions = ObjetionHandler.COMMON_OBJECTIONS.get(
            objection_type.lower(),
            ['Mantén la calma', 'Escucha activamente', 'Proporciona datos']
        )
        return suggestions[0] if suggestions else ""


# Ejemplo de integración
def create_chat_widget_example():
    """Ejemplo de uso del ChatBox"""
    
    root = ctk.CTk()
    root.title("Chat Example")
    root.geometry("500x600")
    
    def handle_message(msg: str) -> str:
        """Handler de ejemplo"""
        response = f"Respuesta IA a: {msg}"
        return response
    
    chat = ChatBox(root, on_send_message=handle_message)
    chat.pack(fill='both', expand=True)
    
    root.mainloop()


if __name__ == "__main__":
    create_chat_widget_example()
