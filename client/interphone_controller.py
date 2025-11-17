import logging
import time
import re
from typing import Optional, Tuple

try:
    from pywinauto import Application, findwindows
    from pywinauto.findbestmatch import MatchError
    PYWINAUTO_AVAILABLE = True
except ImportError:
    PYWINAUTO_AVAILABLE = False
    logging.warning("pywinauto not installed. InterPhone integration will fail.")

# ========== LOGGING ==========
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ========== CONFIGURACIÓN ==========
INTERPHONE_WINDOW_REGEX = r"InterPhone\s*-\s*.*"
MAX_CONNECT_RETRIES = 3
CONNECT_RETRY_DELAY = 2
CALL_TIMEOUT = 5


def normalize_phone_for_interphone(phone_number: str) -> str:
    """
    Normalizar número para InterPhone.
    - Remover caracteres especiales
    - Remover prefijo de país (+506, +1, etc.)
    - Remover caracteres no válidos
    
    Ejemplos de transformación:
    +506-5123-4567 → 51234567
    +1-555-123-4567 → 5551234567
    (506) 5123-4567 → 51234567
    5123-4567 → 51234567
    """
    if not phone_number:
        return ""
    
    # Remover espacios
    phone_number = phone_number.strip()
    
    # Remover todos los caracteres que no sean dígitos
    cleaned = re.sub(r'\D', '', phone_number)
    
    if not cleaned:
        return ""
    
    # Si comienza con prefijo de país (más de 10 dígitos típicamente)
    # Remover primeros 1-3 dígitos (códigos de país)
    if len(cleaned) > 10:
        # Asumir que los primeros 1-3 dígitos son código de país
        # Para +506 (Costa Rica): 506 = 3 dígitos
        # Para +1 (USA): 1 = 1 dígito
        # Para +34 (España): 34 = 2 dígitos
        # Estrategia: si hay más de 10, remover primeros 3 y quedarse con los últimos 10
        cleaned = cleaned[-10:]  # Tomar últimos 10 dígitos
    
    logger.debug(f"Normalized phone: {phone_number} → {cleaned}")
    return cleaned


class InterPhoneController:
    """Controlador para interactuar con InterPhone de forma robusta"""
    
    def __init__(self):
        if not PYWINAUTO_AVAILABLE:
            raise RuntimeError("pywinauto is required. Install with: pip install pywinauto")
        
        self.app: Optional[Application] = None
        self.window = None
        self.is_connected = False
        logger.info("InterPhoneController initialized")

    def connect(self, retries: int = MAX_CONNECT_RETRIES) -> bool:
        """
        Buscar y conectar a la ventana de InterPhone con reintentos.
        
        Args:
            retries: Número de intentos de conexión
            
        Returns:
            True si se conectó exitosamente, False si no
            
        Raises:
            RuntimeError: Si falla después de todos los reintentos
        """
        for attempt in range(1, retries + 1):
            try:
                logger.debug(f"Connect attempt {attempt}/{retries}")
                
                # Buscar ventana por regex
                windows = findwindows.find_windows(title_re=INTERPHONE_WINDOW_REGEX)
                
                if not windows:
                    logger.warning(f"No InterPhone window found (attempt {attempt}/{retries})")
                    if attempt < retries:
                        time.sleep(CONNECT_RETRY_DELAY)
                    continue

                # Conectar a la primera ventana encontrada
                handle = windows[0]
                logger.debug(f"Found InterPhone window: {handle}")
                
                try:
                    self.app = Application(backend="uia").connect(handle=handle)
                    self.window = self.app.window(handle=handle)
                    
                    # Validar que la ventana está accesible
                    window_title = self.window.window_text()
                    logger.info(f"Connected to InterPhone: {window_title}")
                    
                    self.is_connected = True
                    return True
                    
                except Exception as e:
                    logger.error(f"Failed to connect to InterPhone window: {e}")
                    self.window = None
                    self.app = None
                    if attempt < retries:
                        time.sleep(CONNECT_RETRY_DELAY)
                    continue

            except Exception as e:
                logger.error(f"Connection attempt {attempt} failed: {e}")
                if attempt < retries:
                    time.sleep(CONNECT_RETRY_DELAY)
                continue

        # Si llegamos aquí, todos los intentos fallaron
        self.is_connected = False
        error_msg = (f"Failed to connect to InterPhone after {retries} attempts. "
                    "Make sure InterPhone is open and its window title matches: "
                    f"'{INTERPHONE_WINDOW_REGEX}'")
        logger.error(error_msg)
        raise RuntimeError(error_msg)

    def is_window_valid(self) -> bool:
        """Verificar si la ventana sigue siendo válida y accesible"""
        try:
            if not self.window or not self.is_connected:
                return False
            # Intentar acceder a una propiedad para verificar que está viva
            _ = self.window.window_text()
            return True
        except Exception as e:
            logger.warning(f"Window validation failed: {e}")
            self.is_connected = False
            return False

    def find_input_field(self):
        """Encontrar el campo de entrada de número de teléfono"""
        try:
            # Buscar campo Edit
            edit_field = self.window.child_window(control_type="Edit", found_index=0)
            if edit_field and edit_field.exists():
                logger.debug("Found Edit input field")
                return edit_field
        except Exception as e:
            logger.warning(f"Error finding Edit field: {e}")
        
        return None

    def find_call_button(self) -> Optional:
        """Encontrar botón de llamada con búsqueda flexible"""
        try:
            # Intentar encontrar botón por nombre exacto
            for title in ["Llamada", "Llamar", "Call", "LLAMADA", "LLAMAR"]:
                try:
                    button = self.window.child_window(title=title, control_type="Button", found_index=0)
                    if button and button.exists():
                        logger.debug(f"Found call button: '{title}'")
                        return button
                except Exception:
                    pass
            
            # Si no encuentra por nombre, intentar por tipo únicamente
            logger.debug("Attempting to find button by control type only")
            buttons = self.window.child_window(control_type="Button")
            if buttons:
                logger.debug(f"Found {len(buttons) if hasattr(buttons, '__len__') else 1} buttons")
                return buttons
                
        except Exception as e:
            logger.warning(f"Error finding call button: {e}")
        
        return None

    def call(self, phone_number: str) -> bool:
        """
        Realizar llamada a un número específico.
        
        Args:
            phone_number: Número telefónico a llamar (puede incluir +506, espacios, etc.)
            
        Returns:
            True si la llamada se inició exitosamente
            
        Raises:
            RuntimeError: Si hay error durante la llamada
        """
        try:
            # ⭐ NORMALIZAR número para InterPhone
            # Esto limpia +506, espacios, guiones, etc.
            clean_phone = normalize_phone_for_interphone(phone_number)
            
            logger.info(f"Initiating call to {phone_number} (cleaned: {clean_phone})")

            # Validar conexión
            if not self.is_window_valid():
                logger.warning("Window is no longer valid, reconnecting...")
                self.connect()

            # Establecer foco en ventana
            try:
                self.window.set_focus()
                logger.debug("Window focus set")
            except Exception as e:
                logger.warning(f"Could not set focus: {e}")
            
            time.sleep(0.2)

            # Encontrar y completar campo de entrada
            edit_field = self.find_input_field()
            if not edit_field:
                raise RuntimeError(
                    "Could not find phone number input field in InterPhone. "
                    "The application interface may have changed."
                )

            try:
                # ⭐ Usar número LIMPIO sin +506
                edit_field.set_edit_text(clean_phone)
                logger.debug(f"Entered phone number: {clean_phone} (original: {phone_number})")
            except Exception as e:
                logger.warning(f"Could not set text via set_edit_text, trying clear + type: {e}")
                try:
                    # Alternativa: seleccionar todo y tipo
                    edit_field.click_input()
                    edit_field.type_keys("^a")  # Ctrl+A (Select all)
                    edit_field.type_keys(clean_phone)
                    logger.debug(f"Entered phone number via type_keys: {clean_phone}")
                except Exception as e2:
                    raise RuntimeError(f"Could not input phone number: {e2}")

            time.sleep(0.3)

            # Intentar presionar botón de llamada
            call_button = self.find_call_button()
            if call_button:
                try:
                    call_button.click_input()
                    logger.info(f"Call button clicked for {clean_phone}")
                    return True
                except Exception as e:
                    logger.warning(f"Could not click button, trying Enter key: {e}")
            
            # Fallback: presionar Enter
            try:
                edit_field.type_keys("{ENTER}")
                logger.info(f"Call initiated via Enter key for {clean_phone}")
                return True
            except Exception as e:
                raise RuntimeError(f"Could not initiate call: {e}")

        except RuntimeError:
            logger.error(f"RuntimeError during call: phone={phone_number}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during call: {e}")
            raise RuntimeError(f"Unexpected error during call: {e}")

    def disconnect(self):
        """Desconectar de InterPhone"""
        try:
            if self.window:
                self.window = None
            if self.app:
                self.app = None
            self.is_connected = False
            logger.info("Disconnected from InterPhone")
        except Exception as e:
            logger.warning(f"Error during disconnect: {e}")

    def __del__(self):
        """Limpiar al destruir objeto"""
        self.disconnect()
