"""
Chat Assistant con Ollama - CallManager
Sistema de IA para manejar objeciones y preguntas de agentes

Autor: CallManager System
Versión: 1.0
"""

import requests
import logging
import threading
from typing import Optional, Callable, List, Dict
from datetime import datetime

logger = logging.getLogger(__name__)


class OllamaClient:
    """Cliente para comunicarse con Ollama localmente"""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "mistral"):
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.is_available = False
        self.chat_history: List[Dict] = []
        self.max_history = 10
        
        # Verificar disponibilidad
        self._check_availability()
    
    def _check_availability(self) -> bool:
        """Verificar si Ollama está disponible"""
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=2
            )
            
            if response.status_code == 200:
                self.is_available = True
                logger.info(f"✅ Ollama disponible con modelo: {self.model}")
                return True
        except Exception as e:
            logger.warning(f"⚠️ Ollama no disponible: {e}")
        
        self.is_available = False
        return False
    
    def generate_response(self, user_message: str, context: str = "") -> Optional[str]:
        """
        Generar respuesta de IA para una pregunta o objeción
        
        Args:
            user_message: Pregunta o objeción del agente
            context: Contexto adicional (nombre cliente, producto, etc)
        
        Returns:
            Respuesta de la IA o None si error
        """
        if not self.is_available:
            return None
        
        try:
            # Construir prompt con contexto
            system_prompt = """Eres un asistente experto en ventas y servicio al cliente.
Tu objetivo es ayudar a los agentes a:
1. Manejar objeciones de clientes
2. Responder preguntas sobre productos/servicios
3. Proporcionar argumentos de venta convincentes
4. Ser empático y profesional

Responde de forma breve (máximo 2-3 oraciones) y directa."""
            
            if context:
                system_prompt += f"\n\nContexto: {context}"
            
            # Agregar a historial
            self.chat_history.append({
                "role": "user",
                "content": user_message
            })
            
            # Limitar historial
            if len(self.chat_history) > self.max_history:
                self.chat_history = self.chat_history[-self.max_history:]
            
            # Realizar llamada a Ollama
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": self._format_prompt(user_message, system_prompt),
                    "stream": False,
                    "temperature": 0.7,
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                ai_response = data.get('response', '').strip()
                
                # Agregar respuesta al historial
                self.chat_history.append({
                    "role": "assistant",
                    "content": ai_response
                })
                
                logger.info(f"🤖 Respuesta IA: {ai_response[:50]}...")
                return ai_response
            else:
                logger.error(f"Error Ollama: {response.status_code}")
                return None
        
        except requests.exceptions.Timeout:
            logger.error("Timeout: Ollama tardó demasiado en responder")
            return None
        except Exception as e:
            logger.error(f"Error generando respuesta: {e}")
            return None
    
    def _format_prompt(self, user_message: str, system_prompt: str) -> str:
        """Formatear prompt con historial"""
        prompt = f"{system_prompt}\n\n"
        
        # Agregar historial (últimas 5 mensajes)
        for msg in self.chat_history[-5:]:
            if msg["role"] == "user":
                prompt += f"Agente: {msg['content']}\n"
            else:
                prompt += f"Asistente: {msg['content']}\n"
        
        return prompt
    
    def clear_history(self):
        """Limpiar historial de chat"""
        self.chat_history.clear()
        logger.info("📝 Historial de chat limpiado")
    
    def get_models(self) -> List[str]:
        """Obtener lista de modelos disponibles en Ollama"""
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                models = [m['name'].split(':')[0] for m in data.get('models', [])]
                return list(set(models))
            
            return []
        except Exception as e:
            logger.error(f"Error obteniendo modelos: {e}")
            return []
    
    def set_model(self, model: str) -> bool:
        """Cambiar modelo de Ollama"""
        self.model = model
        logger.info(f"✅ Modelo cambiado a: {model}")
        return True


class ChatAssistant:
    """Asistente de chat para la UI"""
    
    def __init__(self, ollama_base_url: str = "http://localhost:11434"):
        self.client = OllamaClient(ollama_base_url)
        self.messages: List[Dict] = []
        self.on_response_callback: Optional[Callable] = None
    
    def set_response_callback(self, callback: Callable):
        """Registrar callback para respuestas (para actualizar UI)"""
        self.on_response_callback = callback
    
    def ask(self, question: str, context: str = "", run_async: bool = True):
        """
        Hacer pregunta al asistente
        
        Args:
            question: Pregunta del agente
            context: Contexto (cliente, producto, etc)
            run_async: Ejecutar en thread separado
        """
        if run_async:
            thread = threading.Thread(
                target=self._ask_thread,
                args=(question, context),
                daemon=True
            )
            thread.start()
        else:
            self._ask_thread(question, context)
    
    def _ask_thread(self, question: str, context: str = ""):
        """Thread para procesar pregunta"""
        try:
            # Agregar pregunta al historial
            self.messages.append({
                'type': 'user',
                'content': question,
                'timestamp': datetime.now().isoformat()
            })
            
            # Generar respuesta
            response = self.client.generate_response(question, context)
            
            if response:
                self.messages.append({
                    'type': 'assistant',
                    'content': response,
                    'timestamp': datetime.now().isoformat()
                })
                
                # Llamar callback
                if self.on_response_callback:
                    self.on_response_callback(response)
            else:
                if self.on_response_callback:
                    self.on_response_callback("❌ No se pudo generar respuesta. Verifica que Ollama esté ejecutándose.")
        
        except Exception as e:
            logger.error(f"Error en ask: {e}")
            if self.on_response_callback:
                self.on_response_callback(f"❌ Error: {str(e)}")
    
    def clear(self):
        """Limpiar chat"""
        self.messages.clear()
        self.client.clear_history()
    
    def get_history(self) -> List[Dict]:
        """Obtener historial de chat"""
        return self.messages.copy()


# Instancia global
chat_assistant: Optional[ChatAssistant] = None


def initialize_chat_assistant(ollama_url: str = "http://localhost:11434") -> ChatAssistant:
    """Inicializar asistente de chat global"""
    global chat_assistant
    chat_assistant = ChatAssistant(ollama_url)
    logger.info("💬 Chat Assistant inicializado")
    return chat_assistant


def get_chat_assistant() -> Optional[ChatAssistant]:
    """Obtener instancia del asistente"""
    global chat_assistant
    return chat_assistant
