"""
Sistema de Proveedores de Llamadas - CallManager
Arquitectura extensible para múltiples aplicaciones y servicios de llamada
Versión: 1.0
"""

from abc import ABC, abstractmethod
from typing import Optional, Tuple, Dict, List
import logging
import json
import requests

logger = logging.getLogger(__name__)

# ========== INTERFAZ BASE ==========

class CallProvider(ABC):
    """Interfaz base para proveedores de llamadas"""
    
    def __init__(self):
        self.name = "Base Provider"
        self.version = "1.0"
        self.is_available = False
    
    @abstractmethod
    def initialize(self) -> bool:
        """Inicializa el proveedor. Retorna True si está disponible"""
        pass
    
    @abstractmethod
    def make_call(self, phone_number: str) -> Tuple[bool, str]:
        """
        Realiza una llamada.
        Retorna: (success, message)
        """
        pass
    
    @abstractmethod
    def normalize_number(self, phone_number: str) -> str:
        """Normaliza un número para este proveedor"""
        pass
    
    def get_info(self) -> Dict:
        """Retorna información del proveedor"""
        return {
            'name': self.name,
            'version': self.version,
            'available': self.is_available
        }

# ========== PROVEEDOR: INTERPHONE ==========

class InterPhoneProvider(CallProvider):
    """Proveedor para integración con InterPhone"""
    
    def __init__(self):
        super().__init__()
        self.name = "InterPhone"
        self.version = "1.0"
        self.app = None
    
    def initialize(self) -> bool:
        """Intenta inicializar InterPhone"""
        try:
            from interphone_controller import InterPhoneController
            self.app = InterPhoneController()
            self.is_available = True
            logger.info("✅ InterPhone inicializado correctamente")
            return True
        except Exception as e:
            logger.warning(f"⚠️ InterPhone no disponible: {e}")
            self.is_available = False
            return False
    
    def make_call(self, phone_number: str) -> Tuple[bool, str]:
        """Realiza llamada mediante InterPhone"""
        if not self.is_available:
            return False, "InterPhone no inicializado"
        
        try:
            normalized = self.normalize_number(phone_number)
            self.app.call(normalized)
            return True, f"Llamada a {phone_number} iniciada vía InterPhone"
        except Exception as e:
            logger.error(f"Error en InterPhone: {e}")
            return False, f"Error: {str(e)}"
    
    def normalize_number(self, phone_number: str) -> str:
        """Normaliza número para InterPhone"""
        import re
        phone_number = phone_number.strip()
        cleaned = re.sub(r'\D', '', phone_number)
        # Remover prefijo país si existe
        if len(cleaned) > 10:
            cleaned = cleaned[-10:]
        return cleaned

# ========== PROVEEDOR: SKYPE ==========

class SkypeProvider(CallProvider):
    """Proveedor para integración con Skype"""
    
    def __init__(self):
        super().__init__()
        self.name = "Skype"
        self.version = "1.0"
    
    def initialize(self) -> bool:
        """Intenta inicializar Skype"""
        try:
            import skype
            self.is_available = True
            logger.info("✅ Skype inicializado correctamente")
            return True
        except ImportError:
            logger.warning("⚠️ Skype no disponible (instala: pip install skype)")
            self.is_available = False
            return False
    
    def make_call(self, phone_number: str) -> Tuple[bool, str]:
        """Realiza llamada mediante Skype"""
        if not self.is_available:
            return False, "Skype no inicializado"
        
        try:
            # URL de protocolo Skype: skype:+506XXXXXXXX?call
            import webbrowser
            normalized = self.normalize_number(phone_number)
            url = f"skype:{normalized}?call"
            webbrowser.open(url)
            return True, f"Llamada a {phone_number} iniciada vía Skype"
        except Exception as e:
            logger.error(f"Error en Skype: {e}")
            return False, f"Error: {str(e)}"
    
    def normalize_number(self, phone_number: str) -> str:
        """Normaliza número para Skype"""
        import re
        phone_number = phone_number.strip()
        # Skype prefiere números con prefijo país
        if not phone_number.startswith('+'):
            cleaned = re.sub(r'\D', '', phone_number)
            if len(cleaned) >= 10:
                phone_number = f"+{cleaned}"
        return phone_number

# ========== PROVEEDOR: GOOGLE MEET ==========

class GoogleMeetProvider(CallProvider):
    """Proveedor para Google Meet (videollamadas)"""
    
    def __init__(self):
        super().__init__()
        self.name = "Google Meet"
        self.version = "1.0"
    
    def initialize(self) -> bool:
        """Verifica disponibilidad de Google Meet"""
        try:
            import webbrowser
            self.is_available = True
            logger.info("✅ Google Meet disponible")
            return True
        except Exception as e:
            logger.warning(f"⚠️ Google Meet no disponible: {e}")
            return False
    
    def make_call(self, phone_number: str) -> Tuple[bool, str]:
        """Abre Google Meet para videollamada"""
        if not self.is_available:
            return False, "Google Meet no disponible"
        
        try:
            import webbrowser
            import uuid
            # Crear sala única basada en el número
            meeting_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"meet{phone_number}"))[:12]
            url = f"https://meet.google.com/{meeting_id}"
            webbrowser.open(url)
            return True, f"Google Meet abierto para {phone_number}"
        except Exception as e:
            logger.error(f"Error en Google Meet: {e}")
            return False, f"Error: {str(e)}"
    
    def normalize_number(self, phone_number: str) -> str:
        """Google Meet no necesita normalización"""
        return phone_number.strip()

# ========== PROVEEDOR: TWILIO ==========

class TwilioProvider(CallProvider):
    """Proveedor para Twilio (API-based)"""
    
    def __init__(self, account_sid: str = None, auth_token: str = None, from_number: str = None):
        super().__init__()
        self.name = "Twilio"
        self.version = "1.0"
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.from_number = from_number
    
    def initialize(self) -> bool:
        """Inicializa Twilio con credenciales"""
        try:
            from twilio.rest import Client
            if self.account_sid and self.auth_token and self.from_number:
                self.client = Client(self.account_sid, self.auth_token)
                self.is_available = True
                logger.info("✅ Twilio inicializado correctamente")
                return True
            else:
                logger.warning("⚠️ Credenciales de Twilio no configuradas")
                return False
        except ImportError:
            logger.warning("⚠️ Twilio no disponible (instala: pip install twilio)")
            return False
    
    def make_call(self, phone_number: str) -> Tuple[bool, str]:
        """Realiza llamada mediante Twilio"""
        if not self.is_available:
            return False, "Twilio no inicializado"
        
        try:
            normalized = self.normalize_number(phone_number)
            call = self.client.calls.create(
                to=normalized,
                from_=self.from_number,
                url="http://demo.twilio.com/docs/voice.xml"
            )
            return True, f"Llamada a {phone_number} iniciada vía Twilio (SID: {call.sid})"
        except Exception as e:
            logger.error(f"Error en Twilio: {e}")
            return False, f"Error: {str(e)}"
    
    def normalize_number(self, phone_number: str) -> str:
        """Normaliza número para Twilio"""
        import re
        phone_number = phone_number.strip()
        cleaned = re.sub(r'\D', '', phone_number)
        # Twilio prefiere formato +COUNTRYCODE...
        if not phone_number.startswith('+'):
            phone_number = f"+{cleaned}"
        return phone_number

# ========== PROVEEDOR: ZOOM ==========

class ZoomProvider(CallProvider):
    """Proveedor para Zoom (videollamadas)"""
    
    def __init__(self):
        super().__init__()
        self.name = "Zoom"
        self.version = "1.0"
    
    def initialize(self) -> bool:
        """Verifica disponibilidad de Zoom"""
        try:
            import webbrowser
            self.is_available = True
            logger.info("✅ Zoom disponible")
            return True
        except Exception as e:
            logger.warning(f"⚠️ Zoom no disponible: {e}")
            return False
    
    def make_call(self, phone_number: str) -> Tuple[bool, str]:
        """Abre Zoom para videollamada"""
        if not self.is_available:
            return False, "Zoom no disponible"
        
        try:
            import webbrowser
            import uuid
            # Generar ID de reunión único
            meeting_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"zoom{phone_number}"))[:12]
            url = f"https://zoom.us/wc/join/{meeting_id}"
            webbrowser.open(url)
            return True, f"Zoom abierto para {phone_number}"
        except Exception as e:
            logger.error(f"Error en Zoom: {e}")
            return False, f"Error: {str(e)}"
    
    def normalize_number(self, phone_number: str) -> str:
        """Zoom no necesita normalización"""
        return phone_number.strip()

# ========== PROVEEDOR: VONAGE (NEXMO) ==========

class VonageProvider(CallProvider):
    """Proveedor para Vonage/Nexmo (API-based)"""
    
    def __init__(self, api_key: str = None, api_secret: str = None, from_number: str = None):
        super().__init__()
        self.name = "Vonage"
        self.version = "1.0"
        self.api_key = api_key
        self.api_secret = api_secret
        self.from_number = from_number
    
    def initialize(self) -> bool:
        """Inicializa Vonage con credenciales"""
        try:
            import vonage
            if self.api_key and self.api_secret:
                self.client = vonage.Client(key=self.api_key, secret=self.api_secret)
                self.is_available = True
                logger.info("✅ Vonage inicializado correctamente")
                return True
            else:
                logger.warning("⚠️ Credenciales de Vonage no configuradas")
                return False
        except ImportError:
            logger.warning("⚠️ Vonage no disponible (instala: pip install vonage)")
            return False
    
    def make_call(self, phone_number: str) -> Tuple[bool, str]:
        """Realiza llamada mediante Vonage"""
        if not self.is_available:
            return False, "Vonage no inicializado"
        
        try:
            normalized = self.normalize_number(phone_number)
            response = self.client.voice.create_call({
                "to": [{"type": "phone", "number": normalized}],
                "from": {"type": "phone", "number": self.from_number},
                "ncco": [{"action": "talk", "text": "Llamada desde CallManager"}]
            })
            return True, f"Llamada a {phone_number} iniciada vía Vonage"
        except Exception as e:
            logger.error(f"Error en Vonage: {e}")
            return False, f"Error: {str(e)}"
    
    def normalize_number(self, phone_number: str) -> str:
        """Normaliza número para Vonage"""
        import re
        phone_number = phone_number.strip()
        cleaned = re.sub(r'\D', '', phone_number)
        if not phone_number.startswith('+'):
            phone_number = f"+{cleaned}"
        return phone_number

# ========== GESTOR DE PROVEEDORES ==========

class CallProviderManager:
    """Gestiona múltiples proveedores de llamadas"""
    
    def __init__(self):
        self.providers: Dict[str, CallProvider] = {}
        self.default_provider: Optional[str] = None
        self._initialize_default_providers()
    
    def _initialize_default_providers(self):
        """Inicializa proveedores por defecto"""
        # Intentar cargar InterPhone
        interphone = InterPhoneProvider()
        interphone.initialize()
        self.register_provider("interphone", interphone)
        
        # Cargar proveedores de videollamada
        google_meet = GoogleMeetProvider()
        google_meet.initialize()
        self.register_provider("google_meet", google_meet)
        
        zoom = ZoomProvider()
        zoom.initialize()
        self.register_provider("zoom", zoom)
        
        # Cargar Skype
        skype = SkypeProvider()
        skype.initialize()
        self.register_provider("skype", skype)
        
        # Establecer proveedor por defecto
        if self.providers.get("interphone", {}).is_available:
            self.default_provider = "interphone"
        elif self.providers.get("skype", {}).is_available:
            self.default_provider = "skype"
        else:
            self.default_provider = "google_meet"
    
    def register_provider(self, name: str, provider: CallProvider):
        """Registra un nuevo proveedor"""
        self.providers[name] = provider
        logger.info(f"Proveedor registrado: {name}")
    
    def add_twilio(self, account_sid: str, auth_token: str, from_number: str):
        """Agrega Twilio como proveedor"""
        twilio = TwilioProvider(account_sid, auth_token, from_number)
        twilio.initialize()
        self.register_provider("twilio", twilio)
    
    def add_vonage(self, api_key: str, api_secret: str, from_number: str):
        """Agrega Vonage como proveedor"""
        vonage = VonageProvider(api_key, api_secret, from_number)
        vonage.initialize()
        self.register_provider("vonage", vonage)
    
    def make_call(self, phone_number: str, provider: str = None) -> Tuple[bool, str]:
        """Realiza una llamada con el proveedor especificado"""
        provider_name = provider or self.default_provider
        
        if provider_name not in self.providers:
            return False, f"Proveedor '{provider_name}' no disponible"
        
        provider_obj = self.providers[provider_name]
        
        if not provider_obj.is_available:
            return False, f"{provider_obj.name} no está disponible"
        
        return provider_obj.make_call(phone_number)
    
    def get_available_providers(self) -> List[Dict]:
        """Retorna lista de proveedores disponibles"""
        return [
            {
                'name': name,
                'info': provider.get_info()
            }
            for name, provider in self.providers.items()
            if provider.is_available
        ]
    
    def get_default_provider_info(self) -> Dict:
        """Retorna información del proveedor por defecto"""
        if self.default_provider and self.default_provider in self.providers:
            return self.providers[self.default_provider].get_info()
        return {}
    
    def set_default_provider(self, provider_name: str) -> bool:
        """Establece el proveedor por defecto"""
        if provider_name in self.providers and self.providers[provider_name].is_available:
            self.default_provider = provider_name
            logger.info(f"Proveedor por defecto cambiado a: {provider_name}")
            return True
        return False

# Instancia global del gestor de proveedores
call_provider_manager = CallProviderManager()
