# CallManager v2.5 - Arquitectura Técnica Completa

**Fecha:** 22 de Noviembre de 2025  
**Versión:** 2.5  
**Status:** ✅ Producción

---

## 📋 Tabla de Contenidos

1. [Visión General](#visión-general)
2. [Nuevos Componentes](#nuevos-componentes)
3. [Arquitectura del Sistema](#arquitectura-del-sistema)
4. [Integración Técnica](#integración-técnica)
5. [Casos de Uso](#casos-de-uso)
6. [Deployment](#deployment)

---

## 🎯 Visión General

CallManager v2.5 introduce tres características revolucionarias:

### 1. **Chat IA con Ollama**
- Asistente inteligente para manejar objeciones
- Respuestas en tiempo real durante llamadas
- Basado en IA local (sin envío de datos a servidores externos)
- Modelos: Mistral, Llama 2, Neural Chat

### 2. **Grabación Automática de Llamadas**
- Captura de audio WAV de alta calidad
- Metadatos automáticos (duración, tamaño, participantes)
- Indexado por usuario, contacto y fecha
- Exportación a Excel

### 3. **UI Responsiva y Moderna**
- Diseño adaptativo (móviles, tablets, desktop)
- Editor inline de contactos
- Atajos de teclado configurables
- Exportación a Excel con estilos

---

## 🆕 Nuevos Componentes

### A. Chat Assistant (`client/chat_assistant.py`)

```
Responsabilidades:
├── OllamaClient
│   ├── Conectar con Ollama local
│   ├── Generar respuestas de IA
│   ├── Gestionar historial de chat
│   └── Manejo de errores y timeouts
└── ChatAssistant
    ├── Interfaz de alto nivel
    ├── Callbacks para UI
    └── Threading para no bloquear
```

**Clase Principal: `OllamaClient`**

```python
class OllamaClient:
    def __init__(self, base_url, model="mistral")
    def generate_response(user_message, context) -> str
    def clear_history()
    def get_models() -> List[str]
    def set_model(model) -> bool
```

**Uso:**
```python
from chat_assistant import initialize_chat_assistant

assistant = initialize_chat_assistant()
response = assistant.ask("¿Cómo responder a 'es muy caro'?")
```

### B. Call Recorder (`client/call_recorder.py`)

```
Responsabilidades:
├── CallRecorder
│   ├── Capturar audio del micrófono
│   ├── Guardar en formato WAV
│   ├── Generar metadata JSON
│   ├── Gestionar directorio de grabaciones
│   └── Exportación de grabaciones
```

**Clase Principal: `CallRecorder`**

```python
class CallRecorder:
    def start_recording(contact_name, contact_phone, user_id, user_name, call_id) -> str
    def stop_recording() -> Dict
    def get_recording_path(recording_id) -> str
    def get_metadata(recording_id) -> Dict
    def list_recordings(user_id=None) -> List[Dict]
    def delete_recording(recording_id) -> bool
    def export_recording(recording_id, export_path) -> bool
```

**Flujo de Grabación:**

```
start_recording()
    ↓
├─ Crear nombre único: {call_id}_{timestamp}.wav
├─ Guardar metadata inicial
├─ Abrir stream de audio PyAudio
└─ Iniciar thread de grabación
    ↓
[Thread grabando audio]
    ↓
stop_recording()
    ↓
├─ Cerrar stream
├─ Escribir frames a archivo WAV
├─ Calcular duración desde archivo
├─ Generar JSON metadata
└─ Retornar información completa
```

**Estructura de Metadata:**

```json
{
  "recording_id": "call_202511221510_20251122_151045",
  "call_id": "call_202511221510",
  "contact_name": "Juan Pérez",
  "contact_phone": "+1234567890",
  "user_id": "user_123",
  "user_name": "Agent Maria",
  "start_time": "2025-11-22T15:10:45.123456",
  "end_time": "2025-11-22T15:12:30.654321",
  "duration_seconds": 105,
  "file_path": "/recordings/call_202511221510_20251122_151045.wav",
  "file_size_bytes": 1024000,
  "status": "completed"
}
```

### C. UI Responsiva (`client/ui/responsive_ui.py`)

```
Componentes:
├── ResponsiveFrame (Base adaptativa)
├── ContactEditorWidget (Editor inline)
├── ExcelExporter (Exportación)
├── MobileContactsView (Vista móvil)
└── KEYBOARD_SHORTCUTS (Atajos de teclado)
```

**ContactEditorWidget:**

```
┌─────────────────────────────────────────┐
│ Nombre: [Juan Pérez        ] ✏️ Editar  │
├─────────────────────────────────────────┤
│ Estado: [▼ active]  Teléfono: [+123456] │
├─────────────────────────────────────────┤
│ Notas (máx 244 caracteres):             │
│ ┌─────────────────────────────────────┐ │
│ │ Interesado en plan mensual...       │ │
│ │                              25/244 │ │
│ └─────────────────────────────────────┘ │
├─────────────────────────────────────────┤
│ [📞 Llamar] [✓ Confirmar] [🗑️]          │
└─────────────────────────────────────────┘
```

**Atajos de Teclado:**

```python
KEYBOARD_SHORTCUTS = {
    '<Control-n>': 'new_contact',      # Nuevo
    '<Control-e>': 'export_excel',     # Exportar
    '<Control-f>': 'search',           # Buscar
    '<Control-c>': 'call',             # Llamar
    '<F2>': 'edit',                    # Editar
    '<Delete>': 'delete_confirm',      # Eliminar
    '<Escape>': 'cancel',              # Cancelar
}
```

### D. Chat Widget (`client/ui/chat_widget.py`)

```
Componentes:
├── ChatMessage (Mensaje individual)
├── ChatBox (Widget integrable)
├── ChatWindow (Ventana flotante)
└── ObjetionHandler (Objeciones comunes)
```

**ChatBox - Interfaz:**

```
┌─────────────────────────────────────────┐
│ 💬 Asistente IA - Manejo de Objeciones  │
│ Haz preguntas para ayuda                │
├─────────────────────────────────────────┤
│                                         │
│ 🤖 Hola, soy tu asistente de IA       │
│ Puedo ayudarte a:                      │
│ • Responder objeciones                 │
│ • Argumentos de venta                  │
│ • Respuestas a preguntas               │
│                                         │
│ [Mensaje del usuario: ¿Cómo respondo?] │
│                                         │
│ [Respuesta IA en blue]                 │
│                                         │
├─────────────────────────────────────────┤
│ [Escribe tu pregunta...       ] [Enviar]│
├─────────────────────────────────────────┤
│ ✅ Asistente listo                     │
└─────────────────────────────────────────┘
```

---

## 🏗️ Arquitectura del Sistema

### Diagrama de Flujo Completo

```
┌─────────────────────────────────────────────────────────────┐
│                    CALLMANAGER v2.5                         │
└─────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│                    UI RESPONSIVA                            │
│  ┌──────────────────┐  ┌──────────────────┐                │
│  │ ContactEditor    │  │ ChatWidget       │                │
│  │ (Editor Inline)  │  │ (Chat IA)        │                │
│  └──────────────────┘  └──────────────────┘                │
└──────────────────────────────────────────────────────────────┘
           │                          │
           ├──────────────┬───────────┘
           │              │
           ▼              ▼
┌──────────────────┐ ┌──────────────────┐
│ CallTracker      │ │ ChatAssistant    │
│ (Duración)       │ │ (IA - Ollama)    │
└──────────────────┘ └──────────────────┘
           │                    │
           │                    ▼
           │            ┌──────────────────┐
           │            │ Ollama Local     │
           │            │ (Mistral)        │
           │            └──────────────────┘
           │
           ▼
┌──────────────────────────────────────────┐
│            CallRecorder                  │
│ (Grabación de Audio)                    │
└──────────────────────────────────────────┘
    │
    ├─ PyAudio (Captura)
    ├─ Wave (Guardado WAV)
    └─ JSON (Metadata)

┌──────────────────────────────────────────┐
│         ExcelExporter                    │
│ (Exportación de Datos)                  │
└──────────────────────────────────────────┘
    │
    └─ openpyxl (Estilos y formato)
```

### Integración con Backend Existente

```
┌────────────────────────────────────────┐
│         call_manager_app.py            │
│         (Main Application)             │
└────────────────────────────────────────┘
        │
        ├─ Inicializar sistemas
        │  ├─ Chat Assistant
        │  ├─ Call Recorder
        │  ├─ Call Tracker
        │  └─ Keyboard Shortcuts
        │
        ├─ En call_contact()
        │  ├─ start_call_recording()
        │  ├─ tracker.start_call()
        │  └─ en end_current_call():
        │     ├─ stop_call_recording()
        │     └─ tracker.end_call()
        │
        ├─ Métodos nuevos
        │  ├─ show_chat_assistant()
        │  ├─ show_recordings()
        │  └─ export_contacts_to_excel()
        │
        └─ Menú Herramientas
           ├─ 💬 Asistente IA
           ├─ 📹 Ver Grabaciones
           └─ 📊 Exportar Contactos
```

---

## 🔌 Integración Técnica

### 1. Inicialización en `call_manager_app.py`

**Paso 1: Imports (Línea ~50)**

```python
from chat_assistant import initialize_chat_assistant, get_chat_assistant
from call_recorder import initialize_call_recorder, get_call_recorder
from ui.responsive_ui import (
    ContactEditorWidget, ExcelExporter, MobileContactsView,
    setup_keyboard_shortcuts
)
from ui.chat_widget import ChatBox, ChatWindow, ObjetionHandler
```

**Paso 2: En `__init__` (Línea ~420)**

```python
# Chat IA
try:
    self.chat_assistant = initialize_chat_assistant()
    self.chat_assistant_available = True
    logger.info("💬 Chat Assistant inicializado")
except:
    self.chat_assistant_available = False
    logger.warning("⚠️ Chat Assistant no disponible")

# Grabador
try:
    self.call_recorder = initialize_call_recorder("recordings")
    self.recording_active = False
    self.current_recording_id = None
    logger.info("🎙️ Call Recorder inicializado")
except Exception as e:
    logger.warning(f"⚠️ Call Recorder: {e}")

# Atajos de teclado
setup_keyboard_shortcuts(self, self._handle_keyboard_action)
```

### 2. Métodos a Agregar

**Show Chat:**
```python
def show_chat_assistant(self):
    chat_window = ChatWindow(
        self,
        on_send_message=self._chat_message_handler,
        title="💬 Asistente IA"
    )

def _chat_message_handler(self, message: str) -> str:
    context = f"Cliente: {self.selected_contact.get('name')}"
    return self.chat_assistant.ask(message, context)
```

**Grabación:**
```python
def start_call_recording(self, contact_name, contact_phone):
    recording_id = self.call_recorder.start_recording(
        contact_name, contact_phone, self.current_user_id,
        self.current_username, f"call_{datetime.now()}"
    )
    self.recording_active = recording_id != ""

def stop_call_recording(self):
    metadata = self.call_recorder.stop_recording()
    if metadata:
        messagebox.showinfo("Grabación",
            f"Duración: {metadata['duration_seconds']}s")
```

**Exportar Excel:**
```python
def export_contacts_to_excel(self):
    file_path = filedialog.asksaveasfilename(
        defaultextension=".xlsx",
        filetypes=[("Excel", "*.xlsx")]
    )
    if file_path:
        ExcelExporter.export_contacts(self.contacts, file_path)
```

### 3. Modificar `call_contact()`

```python
def call_contact(self, contact):
    # Iniciar grabación
    if hasattr(self, 'call_recorder'):
        self.start_call_recording(
            contact.get('name'),
            contact.get('phone')
        )
    
    # ... resto del código ...
    
    # Cuando termina la llamada:
    if hasattr(self, 'call_recorder'):
        self.stop_call_recording()
```

### 4. Menú Herramientas

```python
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
```

---

## 💼 Casos de Uso

### Caso 1: Agente Manejando Objeción

```
1. Agente hace llamada a cliente
2. Cliente dice: "Es muy caro"
3. Agente presiona Ctrl+A → Abre Chat IA
4. Agente escribe: "Cliente dice que es muy caro"
5. Chat IA responde:
   "El precio es competitivo considerando el valor.
    Ofrecemos planes de pago flexible."
6. Agente propone al cliente
```

### Caso 2: Grabación de Llamada Importante

```
1. Agente selecciona contacto VIP
2. Click en "📞 Llamar"
3. Sistema automáticamente:
   - Inicia grabación
   - Inicia rastreo de tiempo
4. Durante la llamada:
   - Timer visible en la UI (rojo si >5min)
5. Al terminar:
   - Grabación guardada automáticamente
   - Metadata generada
6. Agente ve en "📹 Ver Grabaciones":
   - Duración, tamaño, fecha
```

### Caso 3: Exportar Reportes

```
1. Agente termina turno
2. Presiona Ctrl+E (Exportar Contactos)
3. Elige ubicación y nombre
4. Excel generado con:
   - Todos los contactos
   - Teléfono, estado, notas
   - Última llamada, duración
5. O va a Herramientas > Ver Grabaciones
6. Click "📥 Exportar a Excel"
7. Todas las grabaciones en Excel con metadata
```

### Caso 4: Tablet - Contacto Mobile

```
1. Agente abre app en tablet
2. UI se adapta automáticamente:
   - Una columna
   - Botones grandes y espaciados
3. Search bar en top
4. Tarjetas de contacto scrolleable
5. Editor inline sin diálogos
6. Exportación igual funciona
```

---

## 🚀 Deployment

### Producción - Checklist

- [ ] Python 3.8+ instalado
- [ ] `pip install -r requirements.txt`
- [ ] Ollama instalado: `ollama pull mistral`
- [ ] Directorio `recordings/` creado
- [ ] Base de datos inicializada
- [ ] Server ejecutándose: `python server.py`
- [ ] Ollama servicio activo: `ollama serve`
- [ ] App cliente ejecutándose: `python client/call_manager_app.py`

### Monitoreo

**Logs a Verificar:**

```
✅ CallRecorder inicializado
✅ Chat Assistant inicializado
✅ Call Tracker inicializado
⌨️ Atajos de teclado configurados
🎙️ Grabación iniciada: recording_id
⏹️ Grabación completada
💬 Respuesta IA
📊 Contactos exportados
```

### Troubleshooting

**Chat IA no responde:**
```bash
# Verificar Ollama
curl http://localhost:11434/api/tags

# Si no funciona:
ollama serve

# Descargar modelo:
ollama pull mistral
```

**Grabación sin audio:**
```bash
# Verificar PyAudio
python -c "import pyaudio; print(pyaudio.PyAudio().get_device_count())"

# Si hay error, instalar:
pip install --upgrade pyaudio
```

**UI no responsiva:**
```python
# Verificar tamaño de pantalla
root.winfo_screenwidth()
root.winfo_screenheight()

# Modo debug
logger.setLevel(logging.DEBUG)
```

---

## 📊 Estadísticas del Código

| Componente | Líneas | Funciones | Clases |
|-----------|--------|-----------|--------|
| chat_assistant.py | 350 | 12 | 2 |
| call_recorder.py | 380 | 10 | 1 |
| responsive_ui.py | 520 | 15 | 5 |
| chat_widget.py | 380 | 8 | 4 |
| **Total** | **1630** | **45** | **12** |

---

## 🎓 Referencias y Recursos

- [Ollama Documentation](https://ollama.ai/)
- [PyAudio Documentation](https://people.csail.mit.edu/hubert/pyaudio/)
- [openpyxl Documentation](https://openpyxl.readthedocs.io/)
- [CustomTkinter Documentation](https://github.com/TomSchimansky/CustomTkinter)

---

## 🔄 Versionado

| Versión | Cambios |
|---------|---------|
| 2.0 | Sistema de rastreo inicial |
| 2.3 | Dashboard de métricas |
| 2.5 | ✨ Chat IA, Grabación, UI Responsiva |

---

**Autor:** CallManager System  
**Última Actualización:** 22 de Noviembre de 2025  
**Status:** ✅ Producción
