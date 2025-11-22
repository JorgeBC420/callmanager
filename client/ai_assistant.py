"""
AICopilot - Asistente de IA para CallManager v1.0.1.2
Integración mejorada con Ollama para manejo de objeciones
Modelos soportados: llama3, mistral, neural-chat

Autor: CallManager System
Versión: 1.0.1.2
"""

import requests
import threading
import json
import logging
from typing import Optional, Callable, List, Dict
from datetime import datetime

logger = logging.getLogger(__name__)


class AICopilot:
    """
    Copiloto de IA para manejar objeciones en tiempo real
    Integrado con Ollama local (sin envío de datos a servidores externos)
    """
    
    def __init__(
        self,
        model: str = "llama3",
        api_url: str = "http://localhost:11434/api/generate",
        timeout: int = 30
    ):
        """
        Inicializar AICopilot
        
        Args:
            model: Modelo Ollama (llama3, mistral, neural-chat)
            api_url: URL del endpoint Ollama
            timeout: Timeout en segundos para requests
        """
        self.model = model
        self.api_url = api_url
        self.timeout = timeout
        self.is_available = False
        self.chat_history: List[Dict[str, str]] = []
        self.max_history = 15
        
        # Verificar disponibilidad de Ollama
        self._check_availability()
    
    def _check_availability(self) -> bool:
        """Verificar si Ollama está disponible y tiene el modelo"""
        try:
            # Endpoint para verificar modelos disponibles
            response = requests.get(
                self.api_url.replace("/api/generate", "/api/tags"),
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [m.get("name", "") for m in models]
                
                if any(self.model in name for name in model_names):
                    self.is_available = True
                    logger.info(f"✅ AICopilot disponible con modelo: {self.model}")
                    return True
                else:
                    logger.warning(f"⚠️ Modelo {self.model} no encontrado. Disponibles: {model_names}")
        except Exception as e:
            logger.warning(f"⚠️ Ollama no disponible: {str(e)}")
        
        self.is_available = False
        return False
    
    def get_response(
        self,
        objection: str,
        context: str = "Venta de servicios",
        callback: Optional[Callable[[str], None]] = None,
        use_history: bool = True
    ):
        """
        Genera una respuesta a una objeción en un hilo separado
        
        Args:
            objection: La objeción del cliente
            context: Contexto del producto/servicio
            callback: Función para actualizar la UI cuando llegue la respuesta
            use_history: Usar historial de conversación
        
        Ejemplo:
            >>> copilot = AICopilot()
            >>> copilot.get_response(
            ...     objection="Es muy caro",
            ...     context="Servicio de Internet Fibra Óptica 300 Mbps",
            ...     callback=lambda resp: print(f"Respuesta: {resp}")
            ... )
        """
        
        def _worker():
            try:
                # Construir contexto de historial
                history_context = ""
                if use_history and self.chat_history:
                    history_context = "\n\nHistorial reciente:\n"
                    for msg in self.chat_history[-5:]:  # Últimos 5 mensajes
                        history_context += f"- {msg['role']}: {msg['content'][:100]}\n"
                
                # Prompt mejorado para respuestas más naturales y cortas
                prompt = f"""Eres un vendedor experto, empático y profesional en un Call Center.

CONTEXTO ACTUAL:
- Producto/Servicio: {context}
- Modelo de IA: {self.model}
{history_context}

OBJECIÓN DEL CLIENTE: "{objection}"

INSTRUCCIONES:
1. Responde en MAX 2 frases cortas (20-40 palabras)
2. Sé persuasivo pero empático
3. Aborda la objeción directamente
4. NO incluyas explicaciones ni preámbulos
5. Mantén un tono profesional y amable
6. Usa el nombre del producto si aplica

RESPUESTA PARA DECIR AL CLIENTE:"""
                
                # Preparar payload
                payload = {
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.7,  # Creatividad moderada
                    "num_predict": 100,  # Máximo 100 tokens
                }
                
                # Hacer request
                response = requests.post(
                    self.api_url,
                    json=payload,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    result = response.json().get('response', '').strip()
                    
                    # Agregar al historial
                    self.chat_history.append({
                        "role": "user",
                        "content": objection,
                        "timestamp": datetime.now().isoformat()
                    })
                    self.chat_history.append({
                        "role": "assistant",
                        "content": result,
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    # Mantener tamaño de historial
                    if len(self.chat_history) > self.max_history:
                        self.chat_history = self.chat_history[-self.max_history:]
                    
                    if callback:
                        callback(result)
                    else:
                        logger.info(f"📝 Respuesta generada: {result[:50]}...")
                else:
                    error_msg = f"Error Ollama: {response.status_code}"
                    logger.error(error_msg)
                    if callback:
                        callback(error_msg)
                        
            except requests.exceptions.Timeout:
                error_msg = "⏱️ Timeout: Ollama tarda demasiado. Asegúrate de que está ejecutando."
                logger.error(error_msg)
                if callback:
                    callback(error_msg)
                    
            except requests.exceptions.ConnectionError:
                error_msg = "❌ No se puede conectar con Ollama. ¿Está ejecutando? (ollama serve)"
                logger.error(error_msg)
                if callback:
                    callback(error_msg)
                    
            except Exception as e:
                error_msg = f"❌ Error: {str(e)}"
                logger.error(error_msg)
                if callback:
                    callback(error_msg)
        
        # Ejecutar en hilo separado para no bloquear UI
        thread = threading.Thread(target=_worker, daemon=True)
        thread.start()
    
    def clear_history(self):
        """Limpiar historial de conversación"""
        self.chat_history = []
        logger.info("🧹 Historial limpiado")
    
    def set_model(self, model: str) -> bool:
        """
        Cambiar modelo de Ollama
        
        Args:
            model: Nombre del nuevo modelo
            
        Returns:
            True si el cambio fue exitoso
        """
        old_model = self.model
        self.model = model
        
        if self._check_availability():
            logger.info(f"✅ Modelo cambiado de {old_model} a {model}")
            self.clear_history()  # Limpiar historial con cambio de modelo
            return True
        else:
            self.model = old_model
            logger.error(f"❌ No se pudo cambiar a modelo {model}")
            return False
    
    def get_available_models(self) -> List[str]:
        """
        Obtener lista de modelos disponibles en Ollama
        
        Returns:
            Lista de nombres de modelos
        """
        try:
            response = requests.get(
                self.api_url.replace("/api/generate", "/api/tags"),
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                models = response.json().get("models", [])
                return [m.get("name", "") for m in models]
        except Exception as e:
            logger.error(f"Error obteniendo modelos: {str(e)}")
        
        return []
    
    def get_history(self) -> List[Dict[str, str]]:
        """Obtener historial de conversación"""
        return self.chat_history.copy()
    
    def get_status(self) -> Dict[str, any]:
        """Obtener estado actual del copiloto"""
        return {
            "available": self.is_available,
            "model": self.model,
            "history_length": len(self.chat_history),
            "api_url": self.api_url
        }


# Instancia global singleton
_copilot_instance: Optional[AICopilot] = None


def initialize_ai_copilot(
    model: str = "llama3",
    api_url: str = "http://localhost:11434/api/generate"
) -> AICopilot:
    """
    Inicializar AICopilot singleton
    
    Args:
        model: Modelo Ollama a usar
        api_url: URL del endpoint
        
    Returns:
        Instancia de AICopilot
    """
    global _copilot_instance
    
    if _copilot_instance is None:
        _copilot_instance = AICopilot(model=model, api_url=api_url)
        logger.info(f"🤖 AICopilot inicializado con modelo {model}")
    
    return _copilot_instance


def get_ai_copilot() -> Optional[AICopilot]:
    """Obtener instancia global de AICopilot"""
    global _copilot_instance
    
    if _copilot_instance is None:
        _copilot_instance = AICopilot()
    
    return _copilot_instance


if __name__ == "__main__":
    # Test simple
    logging.basicConfig(level=logging.INFO)
    
    copilot = initialize_ai_copilot()
    
    objeciones_test = [
        "Es muy caro",
        "No lo necesito ahora",
        "Mi competencia ofrece mejor precio",
        "Necesito pensarlo"
    ]
    
    print("🧪 Test de AICopilot")
    print("=" * 60)
    
    for objection in objeciones_test[:1]:  # Solo primera para test
        print(f"\n📌 Objeción: {objection}")
        print("⏳ Esperando respuesta...")
        
        def print_response(resp):
            print(f"💬 Respuesta: {resp}")
            print("-" * 60)
        
        copilot.get_response(
            objection=objection,
            context="Internet Fibra Óptica 300 Mbps",
            callback=print_response
        )
        
        # Esperar a que se procese
        import time
        time.sleep(2)
    
    print("\n✅ Test completado")
