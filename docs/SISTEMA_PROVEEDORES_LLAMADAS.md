# ☎️ SISTEMA DE PROVEEDORES DE LLAMADAS - CallManager v2.0

## Descripción General

Se ha implementado un **sistema extensible y modular de proveedores de llamadas** que permite usar múltiples servicios y aplicaciones para realizar llamadas, no solo InterPhone.

---

## Proveedores Incluidos

### 1. **InterPhone** 
- ✅ Integración directa con aplicación InterPhone
- ✅ Normalización de números locales
- ✅ Llamadas automáticas por aplicación de escritorio
- **Mejor para:** Empresas que ya usan InterPhone

### 2. **Skype**
- ✅ Llamadas vía protocolo skype://
- ✅ Soporte para números de teléfono
- ✅ No requiere integración API
- **Mejor para:** Usuarios con Skype instalado

### 3. **Google Meet**
- ✅ Crear salas de videollamada automáticamente
- ✅ Integración web (no requiere instalación)
- ✅ Ideal para reuniones remotas
- **Mejor para:** Equipos que prefieren videollamadas

### 4. **Zoom**
- ✅ Crear salas de videoconferencia
- ✅ Integración web simple
- ✅ Generar IDs únicos por contacto
- **Mejor para:** Organizaciones con licencia Zoom

### 5. **Twilio** (API)
- ✅ Realizar llamadas vía API Twilio
- ✅ Requiere credenciales: Account SID, Auth Token, From Number
- ✅ Soporte para cualquier número telefónico
- **Mejor para:** Operaciones grandes con presupuesto

### 6. **Vonage/Nexmo** (API)
- ✅ Realizar llamadas vía API Vonage
- ✅ Requiere credenciales: API Key, API Secret, From Number
- ✅ Cobertura global
- **Mejor para:** Empresas multinacionales

---

## Arquitectura

### Interfaz Base

```python
class CallProvider(ABC):
    def initialize() -> bool          # Inicializar proveedor
    def make_call(phone) -> (bool, str)   # Realizar llamada
    def normalize_number(phone) -> str    # Normalizar número
    def get_info() -> Dict            # Información del proveedor
```

### Gestor de Proveedores

```python
class CallProviderManager:
    def register_provider(name, provider)  # Registrar nuevo proveedor
    def make_call(phone, provider=None)    # Realizar llamada
    def set_default_provider(name)        # Establecer proveedor por defecto
    def get_available_providers()         # Listar disponibles
```

---

## Cómo Usar

### Desde la UI

1. **Botón "☎️ Proveedor"** en la barra de herramientas
2. **Seleccionar** el proveedor deseado
3. **Hacer click** en cualquier contacto para llamar
4. Se usará el proveedor seleccionado automáticamente

### Desde Código

```python
from call_providers import call_provider_manager

# Hacer llamada con proveedor por defecto
success, message = call_provider_manager.make_call("+506XXXXXXXX")

# Hacer llamada con proveedor específico
success, message = call_provider_manager.make_call("+506XXXXXXXX", "skype")

# Cambiar proveedor por defecto
call_provider_manager.set_default_provider("google_meet")

# Obtener info de proveedores disponibles
providers = call_provider_manager.get_available_providers()
```

---

## Configuración Avanzada

### Agregar Twilio

```python
from call_providers import call_provider_manager

call_provider_manager.add_twilio(
    account_sid="YOUR_ACCOUNT_SID",
    auth_token="YOUR_AUTH_TOKEN",
    from_number="+1234567890"
)
```

### Agregar Vonage

```python
call_provider_manager.add_vonage(
    api_key="YOUR_API_KEY",
    api_secret="YOUR_API_SECRET",
    from_number="+506XXXXXXXX"
)
```

### Crear Proveedor Personalizado

```python
from call_providers import CallProvider, call_provider_manager

class MiProveedor(CallProvider):
    def __init__(self):
        super().__init__()
        self.name = "Mi Proveedor"
        self.version = "1.0"
    
    def initialize(self) -> bool:
        # Lógica de inicialización
        self.is_available = True
        return True
    
    def make_call(self, phone_number: str):
        # Lógica de llamada
        return True, "Llamada realizada"
    
    def normalize_number(self, phone_number: str) -> str:
        # Normalizar número
        return phone_number.strip()

# Registrarlo
mi_prov = MiProveedor()
mi_prov.initialize()
call_provider_manager.register_provider("mi_proveedor", mi_prov)
```

---

## Flujo de Selección Automática

Cuando no se especifica proveedor, se usa este orden de preferencia:

```
1. InterPhone (si disponible)
   └─ Si funciona: usar
   
2. Skype (si disponible)
   └─ Si funciona: usar
   
3. Google Meet (siempre disponible)
   └─ Fallback por defecto
```

---

## Normalización de Números

Cada proveedor normaliza números de forma diferente:

| Proveedor | Entrada | Salida | Formato |
|-----------|---------|--------|---------|
| InterPhone | +506-5123-4567 | 51234567 | Local sin prefijo |
| Skype | 5123-4567 | +50651234567 | Con prefijo país |
| Google Meet | +506XXXXXXXX | +506XXXXXXXX | Sin cambios |
| Twilio | (506) 512-3456 | +506512-3456 | E.164 format |
| Vonage | 51234567 | +50651234567 | Con prefijo país |

---

## Estados y Mensajes

### Respuestas Exitosas

```python
(True, "Llamada a +506XXXXXXXX iniciada vía InterPhone")
(True, "Llamada a +506XXXXXXXX iniciada vía Skype")
(True, "Google Meet abierto para +506XXXXXXXX")
```

### Errores

```python
(False, "Proveedor 'interphone' no disponible")
(False, "InterPhone no inicializado")
(False, "Error: [mensaje de excepción]")
```

---

## Instalación de Dependencias

### InterPhone
```bash
pip install pywinauto
```

### Skype
```bash
# No requiere instalación especial si Skype está en Windows
```

### Twilio
```bash
pip install twilio
```

### Vonage
```bash
pip install vonage
```

### Google Meet & Zoom
```bash
# No requieren instalación
```

---

## Troubleshooting

### "Proveedor no disponible"
**Causa:** Aplicación/librería no instalada
**Solución:** Instalar dependencias (ver arriba)

### "Error normalizando número"
**Causa:** Formato de número no válido
**Solución:** Validar que el número tenga 10+ dígitos

### "Twilio: credenciales inválidas"
**Causa:** Account SID o Auth Token incorrectos
**Solución:** Verificar credenciales en dashboard Twilio

### "Google Meet no abre"
**Causa:** Navegador web no configurado
**Solución:** Establecer navegador por defecto en Windows

---

## Casos de Uso

### Caso 1: Centro de Llamadas
```python
# Usar Twilio como proveedor principal
call_provider_manager.add_twilio(...)
call_provider_manager.set_default_provider("twilio")
```

### Caso 2: Empresa Distribuida
```python
# Usar Google Meet para reuniones remotas
call_provider_manager.set_default_provider("google_meet")
```

### Caso 3: Usuario Individual
```python
# Fallback automático: InterPhone → Skype → Google Meet
# No requiere configuración
```

---

## API Reference

### CallProvider

```python
class CallProvider(ABC):
    name: str                           # Nombre del proveedor
    version: str                        # Versión
    is_available: bool                  # Está disponible
    
    def initialize() -> bool            # Inicializar
    def make_call(phone) -> (bool, str) # Llamar
    def normalize_number(phone) -> str  # Normalizar
    def get_info() -> Dict              # Info
```

### CallProviderManager

```python
class CallProviderManager:
    providers: Dict[str, CallProvider]      # Registrados
    default_provider: str                   # Por defecto
    
    def register_provider(name, provider)   # Registrar
    def add_twilio(sid, token, from)       # Agregar Twilio
    def add_vonage(key, secret, from)      # Agregar Vonage
    def make_call(phone, provider) -> (bool, str)
    def get_available_providers() -> List
    def get_default_provider_info() -> Dict
    def set_default_provider(name) -> bool
```

---

## Ejemplos Completos

### Ejemplo 1: Cambiar Proveedor Dinámicamente

```python
from call_providers import call_provider_manager

# Listar disponibles
available = call_provider_manager.get_available_providers()
print("Proveedores disponibles:")
for p in available:
    print(f"  - {p['name']} (v{p['info']['version']})")

# Elegir uno
call_provider_manager.set_default_provider("skype")

# Usar
success, msg = call_provider_manager.make_call("+506XXXXXXXX")
print(msg)
```

### Ejemplo 2: Proveedor Personalizado

```python
from call_providers import CallProvider, call_provider_manager

class WhatsAppProvider(CallProvider):
    def __init__(self):
        super().__init__()
        self.name = "WhatsApp"
        self.version = "1.0"
    
    def initialize(self) -> bool:
        self.is_available = True
        return True
    
    def make_call(self, phone_number: str):
        import webbrowser
        normalized = self.normalize_number(phone_number)
        url = f"https://wa.me/{normalized}?text=Hola%20desde%20CallManager"
        webbrowser.open(url)
        return True, f"WhatsApp abierto para {phone_number}"
    
    def normalize_number(self, phone_number: str) -> str:
        import re
        cleaned = re.sub(r'\D', '', phone_number)
        if not cleaned.startswith('+'):
            cleaned = f"506{cleaned}"
        return cleaned

# Registrar
wp = WhatsAppProvider()
wp.initialize()
call_provider_manager.register_provider("whatsapp", wp)

# Usar
success, msg = call_provider_manager.make_call("+506XXXXXXXX", "whatsapp")
```

---

## Próximas Mejoras

- [ ] Soporte para SIP/VoIP
- [ ] Integración con Microsoft Teams
- [ ] Soporte para WhatsApp API
- [ ] Grabación de llamadas
- [ ] Transcripción automática
- [ ] Historial de proveedores usados

---

## Conclusión

El sistema de proveedores ofrece:

✅ **Flexibilidad:** Soporta múltiples servicios
✅ **Extensibilidad:** Fácil agregar nuevos proveedores  
✅ **Fallback Automático:** Busca alternativa si falla
✅ **Sin Cambios en UI:** La interfaz se adapta automáticamente
✅ **Configuración Fácil:** Desde UI o código

Tu aplicación ahora puede soportar cualquier servicio de llamadas sin cambios arquitectónicos importantes.

