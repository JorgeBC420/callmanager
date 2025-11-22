# 🚀 CallManager v1.0.1.2 - Documentación Completa

**Fecha:** Noviembre 22, 2025  
**Versión:** 1.0.1.2 (versión anterior 1.0.1.1, anterior a esa 1.0.1)  
**Status:** ✅ **PRODUCCIÓN LISTA**  
**Autor:** Jorge BC420  

---

## 📋 Tabla de Contenidos

1. [Visión General](#visión-general)
2. [Nuevas Características v1.0.1.2](#nuevas-características-v101.2)
3. [Arquitectura Técnica](#arquitectura-técnica)
4. [Instalación y Setup](#instalación-y-setup)
5. [Guía de Integración](#guía-de-integración)
6. [API de Componentes](#api-de-componentes)
7. [Ejemplos de Código](#ejemplos-de-código)
8. [Troubleshooting](#troubleshooting)

---

## 🎯 Visión General

CallManager v1.0.1.2 es la evolución de versiones anteriores con **3 sistemas completamente integrados**:

| Sistema | Versión Anterior | v1.0.1.2 | Mejora |
|---------|------------------|----------|--------|
| **Rastreo de Tiempo** | v1.0 | Mejorado ✅ | Más preciso, mejor UI |
| **Métricas y Dashboards** | v1.0.1 | Mejorado ✅ | Multi-rol, móvil responsive |
| **Chat IA + Grabación** | NO EXISTÍA | v1.0.1.2 ✨ | NUEVO: Ollama, sounddevice |

### ✨ Las 3 Características Principales

#### 1. **💬 Chat IA Asistente (AICopilot)**
- **Tecnología:** Ollama local (llama3, mistral, neural-chat)
- **Función:** Manejo inteligente de objeciones en tiempo real
- **Ventaja:** Respuestas contextuales, sin envío de datos externos
- **Archivos:** `client/ai_assistant.py`

#### 2. **🎙️ Grabación Automática de Llamadas**
- **Tecnología:** sounddevice + soundfile (WAV de alta calidad)
- **Función:** Captura automática con metadata (participantes, duración)
- **Ventaja:** Auditoría completa, exportación a Excel
- **Archivos:** `client/recording_manager.py`

#### 3. **📱 Dashboard Móvil en Tiempo Real**
- **Tecnología:** HTML5 + Bootstrap 5 + Socket.IO + Chart.js
- **Función:** Visualización de métricas en móvil/tablet/desktop
- **Ventaja:** Responsive, actualización en vivo, gráficos interactivos
- **Archivos:** `templates/dashboard_mobile.html`

---

## 📁 Nuevas Características v1.0.1.2

### A. Cliente IA Mejorado: `client/ai_assistant.py`

```python
from ai_assistant import AICopilot, initialize_ai_copilot

# Inicializar
copilot = initialize_ai_copilot(model="llama3")

# Usar (no bloquea UI)
copilot.get_response(
    objection="Es muy caro",
    context="Internet Fibra Óptica 300 Mbps",
    callback=lambda resp: print(f"Respuesta: {resp}")
)
```

**Características clave:**
- ✅ Modelos intercambiables (llama3, mistral, neural-chat)
- ✅ Historial de conversación (últimos 15 mensajes)
- ✅ Callbacks para actualización de UI
- ✅ Threading para no bloquear
- ✅ Verificación automática de Ollama disponible
- ✅ Timeout configurable (default 30s)

**Métodos principales:**
```python
# Generar respuesta (asíncrono)
copilot.get_response(objection, context, callback, use_history=True)

# Gestionar historial
copilot.clear_history()
copilot.get_history()  # Retorna lista de mensajes

# Cambiar modelo
copilot.set_model("mistral")

# Obtener estado
copilot.get_status()  # Dict con disponibilidad, modelo, etc.

# Listar modelos disponibles
copilot.get_available_models()
```

---

### B. Grabador de Audio: `client/recording_manager.py`

```python
from recording_manager import initialize_audio_recorder

# Inicializar
recorder = initialize_audio_recorder(save_dir="recordings")

# Iniciar grabación
filepath = recorder.start_recording(
    filename="llamada_001",
    contact_name="Juan García",
    contact_phone="555-1234",
    user_id="agente_01",
    user_name="María López",
    call_id="CALL-2025-11-22-001"
)

# Detener y guardar
metadata = recorder.stop_recording()
# Retorna: {duration_seconds, file_size_bytes, ...}
```

**Características clave:**
- ✅ Captura de audio mono/estéreo configurable
- ✅ Frecuencia de muestreo: 44100 Hz (CD quality)
- ✅ Formato WAV de alta calidad (PCM_16)
- ✅ Metadata automática en JSON sidecar
- ✅ Threading para captura no bloqueante
- ✅ Listado y búsqueda de grabaciones
- ✅ Exportación a otras carpetas

**Métodos principales:**
```python
# Control de grabación
recorder.start_recording(filename, contact_name, ...)
metadata = recorder.stop_recording()

# Gestión de archivos
recorder.list_recordings(user_id=None, contact_name=None)
recorder.get_metadata(filepath)
recorder.delete_recording(filepath)
recorder.export_recording(src, dest)

# Estadísticas
stats = recorder.get_statistics(user_id="agente_01")
# Retorna: {total_recordings, total_duration_seconds, total_size_mb}

# Dispositivos
devices = recorder.list_devices()
# [{index, name, channels, sample_rate}, ...]
```

---

### C. Dashboard Móvil HTML5: `templates/dashboard_mobile.html`

**Características:**
- ✅ Responsive (móvil, tablet, desktop)
- ✅ Dark theme profesional
- ✅ Socket.IO para actualización en vivo
- ✅ Chart.js para gráficos interactivos
- ✅ Tres pestañas: Dashboard, Equipo, Grabaciones
- ✅ Métricas en tarjetas (Llamadas, Ventas, % Éxito, Tiempo)

**Eventos Socket.IO esperados:**
```javascript
// Cliente escucha:
socket.on('metrics_update', (data) => {
    // data: {calls_today, sales_today, success_rate, total_talk_time}
});

socket.on('team_update', (data) => {
    // data: [{name, calls, sales, success_rate}, ...]
});

socket.on('recordings_update', (data) => {
    // data: [{contact_name, start_time, duration_seconds, file_size_bytes}, ...]
});

// Cliente emite:
socket.emit('request_metrics');  // Solicita métricas actuales
socket.emit('request_team_data');  // Solicita datos del equipo
socket.emit('request_recordings');  // Solicita grabaciones
```

---

## 🏗️ Arquitectura Técnica

### Diagrama de Flujo Completo

```
┌─────────────────────────────────────────────────────────┐
│          AGENTE REALIZA LLAMADA EN CALL_MANAGER          │
└────────────────┬────────────────────────────────────────┘
                 │
    ┌────────────┴─────────────┬───────────────┐
    │                          │               │
    ▼                          ▼               ▼
┌─────────────┐    ┌───────────────────┐  ┌──────────────┐
│Rastreo      │    │ Grabación Audio   │  │ Chat IA      │
│de Tiempo    │    │ (AudioRecorder)   │  │ (AICopilot)  │
│v1.0         │    │ v1.0.1.2 (NEW)    │  │ v1.0.1.2(NEW)│
└────┬────────┘    └────┬──────────────┘  └──────┬───────┘
     │                  │                        │
     │ Envía            │ Guarda                 │ Genera
     │ CallLog          │ WAV + JSON             │ Respuesta
     │                  │                        │
     └──────────────────┼────────────────────────┘
                        │
                        ▼
              ┌──────────────────────┐
              │ Servidor (server.py) │
              │  - Flask            │
              │  - SQLAlchemy       │
              │  - Socket.IO        │
              └──────────┬───────────┘
                         │
            ┌────────────┼────────────┐
            │            │            │
            ▼            ▼            ▼
      ┌─────────┐  ┌──────────┐  ┌─────────────┐
      │Database │  │Socket.IO │  │REST API     │
      │(SQLite) │  │ Events   │  │Endpoints    │
      └─────────┘  └────┬─────┘  └─────────────┘
                        │
                        ▼
              ┌──────────────────────┐
              │ Cliente Web (HTML5)  │
              │ Dashboard Móvil      │
              │ Bootstrap + Chart.js │
              │ Templates/dashboard_ │
              │      mobile.html     │
              └──────────────────────┘
```

### Arquitectura de Directorios

```
callmanager/
├── client/
│   ├── call_manager_app.py           (UI Principal CustomTkinter)
│   ├── chat_assistant.py             (v2.5: Chat Ollama básico)
│   ├── call_recorder.py              (v2.5: Grabación básica)
│   ├── ai_assistant.py               (v1.0.1.2: AICopilot mejorado) ✨ NEW
│   ├── recording_manager.py          (v1.0.1.2: AudioRecorder mejorado) ✨ NEW
│   ├── call_tracking.py              (v1.0: Rastreo de tiempo)
│   ├── metrics_dashboard.py          (v1.0.1: Dashboards multi-rol)
│   ├── auth_context.py               (v1.0.1: Gestión de roles)
│   ├── call_providers.py
│   ├── config_loader.py
│   └── ui/
│       ├── responsive_ui.py          (v2.5: UI responsiva)
│       ├── chat_widget.py            (v2.5: Chat widget integrable)
│       └── ...
│
├── server.py                          (Backend Flask + Socket.IO)
├── requirements.txt                   (Dependencias actualizadas)
├── config.py
│
├── templates/
│   └── dashboard_mobile.html         (v1.0.1.2: Dashboard HTML5) ✨ NEW
│
├── recordings/                        (Grabaciones WAV + JSON metadata)
│
├── docs/
│   ├── ARQUITECTURA_TECNICA_v2.5.md  (Anterior)
│   ├── SISTEMA_RASTREO_TIEMPO_COMPLETO.md
│   ├── IMPLEMENTACION_METRICAS_FINAL.md
│   └── ...
│
└── CALLMANAGER_v1.0.1.2_COMPLETO.md  (Este archivo) ✨ NEW
```

---

## 📦 Instalación y Setup

### Requisitos Previos

```bash
# Python 3.9+
python --version

# Git
git --version
```

### Paso 1: Instalar Dependencias Python

```bash
cd callmanager
pip install -r requirements.txt
```

**Nuevas dependencias en v1.0.1.2:**
```
sounddevice>=0.4.5      # Captura de audio
soundfile>=0.12.1       # Guardado WAV
numpy>=1.24.0           # Arrays de audio
# + todas las anteriores (Flask, CustomTkinter, etc.)
```

### Paso 2: Instalar y Configurar Ollama

#### Windows

```powershell
# 1. Descargar desde https://ollama.ai/
# 2. Ejecutar instalador (Ollama-Windows-x64.exe)
# 3. En PowerShell, verificar instalación:

ollama --version

# 4. Descargar modelo (una sola vez)
ollama pull llama3

# 5. En una terminal separada, ejecutar servidor (siempre activo)
ollama serve
# Escuchará en http://localhost:11434
```

#### macOS

```bash
# Usar Homebrew
brew install ollama

# Descargar modelo
ollama pull llama3

# Servir (en otra terminal)
ollama serve
```

#### Linux

```bash
# Descargar desde https://ollama.ai/
# O usar script de instalación
curl https://ollama.ai/install.sh | sh

# Descargar modelo
ollama pull llama3

# Servir
ollama serve
```

### Paso 3: Verificar Conectividad Ollama

```bash
# Desde PowerShell o terminal, probar conexión:
curl http://localhost:11434/api/tags

# Debería retornar JSON con modelos disponibles:
# {"models":[{"name":"llama3:latest",...}]}
```

### Paso 4: Iniciar Servidor Backend

```bash
# Terminal 1: Servidor Flask
python server.py
# Escuchará en http://localhost:5000
```

### Paso 5: Iniciar Cliente

```bash
# Terminal 2: Cliente CustomTkinter
python client/call_manager_app.py
```

### Paso 6: (Opcional) Acceder al Dashboard Móvil

```
Navegador: http://localhost:5000/mobile
# Verás Dashboard HTML5 responsive
```

---

## 🔧 Guía de Integración

### Integración de AICopilot en call_manager_app.py

```python
# En imports:
from ai_assistant import initialize_ai_copilot, get_ai_copilot

# En __init__:
class CallManagerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Inicializar AICopilot
        self.ai_copilot = initialize_ai_copilot(model="llama3")
        
        # Crear botón en UI
        self.btn_ia_help = ctk.CTkButton(
            master=self.frame_tools,
            text="💡 Ayuda IA",
            command=self.show_ia_help
        )
        self.btn_ia_help.pack()
        
        # Label para estado
        self.lbl_ia_status = ctk.CTkLabel(
            master=self.frame_tools,
            text="🤖 Listo"
        )
        self.lbl_ia_status.pack()

# Método para pedir ayuda
def show_ia_help(self):
    objection = ctk.simpledialog.askstring(
        "Objeción del Cliente",
        "¿Qué objeción tiene el cliente?"
    )
    
    if not objection:
        return
    
    self.lbl_ia_status.configure(text="🤖 Pensando...")
    
    def on_response(response):
        # Actualizar UI desde callback
        self.lbl_ia_status.configure(text="✅ Listo")
        messagebox.showinfo("Sugerencia IA", response)
    
    # Llamar (no bloquea)
    self.ai_copilot.get_response(
        objection=objection,
        context="Servicio de Internet Fibra Óptica",
        callback=on_response
    )
```

### Integración de AudioRecorder en call_manager_app.py

```python
# En imports:
from recording_manager import initialize_audio_recorder

# En __init__:
class CallManagerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Inicializar grabador
        self.audio_recorder = initialize_audio_recorder(
            save_dir="recordings"
        )
        self.current_call_recording = None

# Iniciar grabación en on_call_started:
def on_call_started(self, contact):
    # ... código existente ...
    
    # Iniciar grabación automática
    self.current_call_recording = self.audio_recorder.start_recording(
        filename=f"call_{int(time.time())}",
        contact_name=contact.name,
        contact_phone=contact.phone,
        user_id=self.current_user_id,
        user_name=self.current_user_name,
        call_id=f"CALL-{datetime.now().isoformat()}"
    )
    
    self.lbl_status.configure(text="📞 Llamada en curso (Grabando...)")

# Detener grabación en on_call_ended:
def on_call_ended(self):
    # ... código existente ...
    
    if self.current_call_recording:
        metadata = self.audio_recorder.stop_recording()
        
        if metadata:
            messagebox.showinfo(
                "Grabación Completada",
                f"Duración: {metadata['duration_seconds']}s\n"
                f"Tamaño: {metadata['file_size_bytes'] / 1024:.1f} KB"
            )
        
        self.current_call_recording = None
```

### Integración en server.py (Socket.IO eventos)

```python
from flask import Flask, render_template
from flask_socketio import emit
from recording_manager import get_audio_recorder

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/mobile')
def mobile_dashboard():
    return render_template('dashboard_mobile.html')

# Evento: cliente solicita métricas actuales
@socketio.on('request_metrics')
def handle_metrics_request():
    # Obtener métricas del usuario actual
    metrics = {
        'calls_today': 12,
        'sales_today': 3,
        'success_rate': 25,
        'total_talk_time': 2340  # segundos
    }
    emit('metrics_update', metrics)

# Evento: cliente solicita datos del equipo
@socketio.on('request_team_data')
def handle_team_request():
    team_data = [
        {'name': 'María López', 'calls': 15, 'sales': 4, 'success_rate': 27},
        {'name': 'Carlos García', 'calls': 18, 'sales': 5, 'success_rate': 28},
        {'name': 'Ana Martínez', 'calls': 20, 'sales': 6, 'success_rate': 30},
    ]
    emit('team_update', team_data)

# Evento: cliente solicita grabaciones
@socketio.on('request_recordings')
def handle_recordings_request():
    recorder = get_audio_recorder()
    recordings = recorder.list_recordings(limit=10)
    emit('recordings_update', recordings)

# Emitir actualizaciones en tiempo real
@app.route('/api/call/end', methods=['POST'])
def end_call():
    # ... lógica de fin de llamada ...
    
    # Emitir actualización a todos los clientes conectados
    socketio.emit('metrics_update', {
        'calls_today': updated_count,
        'sales_today': updated_sales,
        'success_rate': updated_rate,
        'total_talk_time': updated_time
    }, broadcast=True)
    
    return {'status': 'ok'}

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
```

---

## 📚 API de Componentes

### AICopilot API

**Instancia:**
```python
from ai_assistant import get_ai_copilot

copilot = get_ai_copilot()  # Obtiene singleton
```

**Métodos:**

| Método | Parámetros | Retorna | Notas |
|--------|-----------|---------|-------|
| `get_response()` | objection, context, callback, use_history | None | Asíncrono, threading |
| `clear_history()` | - | None | Limpia conversación |
| `set_model()` | model (str) | bool | Cambia modelo Ollama |
| `get_available_models()` | - | List[str] | Modelos disponibles |
| `get_history()` | - | List[Dict] | Historial de chat |
| `get_status()` | - | Dict | Estado actual |

**Propiedades:**

| Propiedad | Tipo | Descripción |
|-----------|------|-------------|
| `is_available` | bool | ¿Ollama disponible? |
| `model` | str | Modelo actual |
| `chat_history` | List | Historial (últimos 15 msgs) |
| `api_url` | str | URL endpoint Ollama |

---

### AudioRecorder API

**Instancia:**
```python
from recording_manager import get_audio_recorder

recorder = get_audio_recorder()  # Obtiene singleton
```

**Métodos:**

| Método | Parámetros | Retorna | Notas |
|--------|-----------|---------|-------|
| `start_recording()` | filename, contact_name, ... | str | Ruta archivo |
| `stop_recording()` | - | Dict | Metadata con duración |
| `list_recordings()` | user_id, contact_name, limit | List[Dict] | Lista grabaciones |
| `get_metadata()` | filepath | Dict | Metadata JSON |
| `delete_recording()` | filepath | bool | Elimina archivo |
| `export_recording()` | filepath, export_path | bool | Copia a otra carpeta |
| `get_statistics()` | user_id | Dict | Estadísticas agregadas |
| `list_devices()` | - | List[Dict] | Dispositivos audio |

**Propiedades:**

| Propiedad | Tipo | Descripción |
|-----------|------|-------------|
| `save_dir` | Path | Directorio grabaciones |
| `is_recording` | bool | ¿Grabando actualmente? |
| `sample_rate` | int | Frecuencia (44100) |
| `channels` | int | Canales (1=mono, 2=stereo) |

---

## 💻 Ejemplos de Código

### Ejemplo 1: Chat IA Simple

```python
import logging
from ai_assistant import initialize_ai_copilot

logging.basicConfig(level=logging.INFO)

# Inicializar
copilot = initialize_ai_copilot(model="llama3")

# Objeciones de ejemplo
objeciones = [
    "Es muy caro",
    "No lo necesito ahora",
    "Mi competencia ofrece mejor precio",
    "Necesito pensarlo un mes"
]

print("🧪 Test de AICopilot")
print("=" * 70)

for objection in objeciones:
    print(f"\n📌 Objeción: {objection}")
    print("⏳ Esperando respuesta...")
    
    # Función callback
    def print_response(response):
        print(f"💬 Respuesta IA: {response}")
        print("-" * 70)
    
    # Hacer petición (no bloquea)
    copilot.get_response(
        objection=objection,
        context="Internet Fibra Óptica 300 Mbps - $79.99/mes",
        callback=print_response
    )
    
    # Esperar procesamiento
    import time
    time.sleep(3)

print("\n✅ Test completado!")
print(f"📊 Historial: {len(copilot.get_history())} mensajes")
```

### Ejemplo 2: Grabación de Audio Simple

```python
import time
from recording_manager import initialize_audio_recorder

# Inicializar
recorder = initialize_audio_recorder(save_dir="mis_grabaciones")

print("🎙️ Ejemplo de Grabación")
print("=" * 70)

# Listar dispositivos disponibles
print("\n🔌 Dispositivos de audio:")
for device in recorder.list_devices():
    print(f"  [{device['index']}] {device['name']} ({device['channels']}ch)")

# Grabar 10 segundos
print("\n🔴 Iniciando grabación de 10 segundos...")
filepath = recorder.start_recording(
    filename="ejemplo",
    contact_name="Cliente Test",
    contact_phone="555-1234"
)

# Esperar
for i in range(10):
    print(f"  ⏳ {i+1}/10...", end='\r')
    time.sleep(1)

# Detener
metadata = recorder.stop_recording()

print("\n✅ Grabación completada!")
print(f"📊 Estadísticas:")
print(f"  Archivo: {metadata['file_path']}")
print(f"  Duración: {metadata['duration_seconds']:.1f} segundos")
print(f"  Tamaño: {metadata['file_size_bytes']/1024:.1f} KB")

# Listar grabaciones
print("\n📋 Grabaciones:")
for rec in recorder.list_recordings(limit=5):
    print(f"  - {rec['contact_name']}: {rec['duration_seconds']}s")
```

### Ejemplo 3: Integración Completa en UI

```python
import customtkinter as ctk
from ai_assistant import initialize_ai_copilot
from recording_manager import initialize_audio_recorder
import threading
import time

class CallManagerDemo(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("CallManager v1.0.1.2 Demo")
        self.geometry("600x500")
        
        # Componentes
        self.ai_copilot = initialize_ai_copilot()
        self.recorder = initialize_audio_recorder()
        self.current_call = None
        
        # UI
        self.frame_main = ctk.CTkFrame(self)
        self.frame_main.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Título
        lbl_title = ctk.CTkLabel(
            self.frame_main,
            text="🚀 CallManager v1.0.1.2",
            font=("Arial", 20, "bold")
        )
        lbl_title.pack(pady=10)
        
        # Frame de cliente
        self.frame_contact = ctk.CTkFrame(self.frame_main)
        self.frame_contact.pack(fill="x", pady=10)
        
        ctk.CTkLabel(self.frame_contact, text="Cliente:").pack(side="left", padx=5)
        self.entry_contact = ctk.CTkEntry(
            self.frame_contact,
            placeholder_text="Nombre del cliente"
        )
        self.entry_contact.pack(side="left", padx=5, fill="x", expand=True)
        
        # Botones principales
        self.frame_buttons = ctk.CTkFrame(self.frame_main)
        self.frame_buttons.pack(fill="x", pady=10)
        
        btn_call = ctk.CTkButton(
            self.frame_buttons,
            text="📞 Iniciar Llamada",
            command=self.start_call,
            fg_color="green"
        )
        btn_call.pack(side="left", padx=5)
        
        btn_end = ctk.CTkButton(
            self.frame_buttons,
            text="🔴 Terminar Llamada",
            command=self.end_call,
            fg_color="red"
        )
        btn_end.pack(side="left", padx=5)
        
        btn_ia = ctk.CTkButton(
            self.frame_buttons,
            text="💬 Pedir Ayuda IA",
            command=self.ask_ia
        )
        btn_ia.pack(side="left", padx=5)
        
        # Estado
        self.lbl_status = ctk.CTkLabel(
            self.frame_main,
            text="⏳ Estado: Inactivo",
            text_color="gray"
        )
        self.lbl_status.pack(pady=5)
        
        # Frame de IA
        self.frame_ia = ctk.CTkFrame(self.frame_main)
        self.frame_ia.pack(fill="both", expand=True, pady=10)
        
        ctk.CTkLabel(self.frame_ia, text="💬 Respuestas IA:", 
                     font=("Arial", 12, "bold")).pack(anchor="w")
        
        self.txt_ia_response = ctk.CTkTextbox(self.frame_ia, height=150)
        self.txt_ia_response.pack(fill="both", expand=True, padx=5, pady=5)
        
    def start_call(self):
        contact = self.entry_contact.get() or "Cliente"
        
        # Iniciar grabación
        self.current_call = self.recorder.start_recording(
            filename="llamada",
            contact_name=contact,
            contact_phone="555-1234",
            user_id="agente_01",
            user_name="Agente Demo"
        )
        
        self.lbl_status.configure(
            text=f"✅ Llamada con {contact} (Grabando...)",
            text_color="green"
        )
        
        self.entry_contact.configure(state="disabled")
    
    def end_call(self):
        if not self.current_call:
            return
        
        metadata = self.recorder.stop_recording()
        
        self.lbl_status.configure(
            text=f"✅ Llamada completada ({metadata['duration_seconds']:.0f}s)",
            text_color="gray"
        )
        
        self.entry_contact.configure(state="normal")
        self.entry_contact.delete(0, "end")
    
    def ask_ia(self):
        objection = ctk.simpledialog.askstring(
            "Objeción del Cliente",
            "¿Cuál es la objeción?"
        )
        
        if not objection:
            return
        
        self.txt_ia_response.delete("1.0", "end")
        self.txt_ia_response.insert("end", "⏳ Pensando...\n")
        
        def on_response(response):
            self.txt_ia_response.delete("1.0", "end")
            self.txt_ia_response.insert("end", response)
        
        # En thread para no bloquear
        def ask_thread():
            self.ai_copilot.get_response(
                objection=objection,
                context="Internet Fibra Óptica",
                callback=on_response
            )
        
        threading.Thread(target=ask_thread, daemon=True).start()

if __name__ == "__main__":
    app = CallManagerDemo()
    app.mainloop()
```

---

## 🐛 Troubleshooting

### Problema: "No se puede conectar con Ollama"

**Causa:** Ollama no está ejecutándose o no está en puerto 11434

**Solución:**
```powershell
# 1. Verificar si Ollama está ejecutándose
Get-Process ollama

# 2. Si no está, iniciar en terminal separada:
ollama serve

# 3. Verificar conexión:
curl http://localhost:11434/api/tags

# 4. Si sigue sin funcionar, verificar puerto:
netstat -ano | findstr :11434
```

### Problema: "Modelo llama3 no encontrado"

**Causa:** Modelo no descargado

**Solución:**
```bash
# Listar modelos disponibles
ollama list

# Descargar modelo
ollama pull llama3

# Otros modelos disponibles:
ollama pull mistral
ollama pull neural-chat
ollama pull dolphin-mixtral
```

### Problema: "Error de audio: No se puede iniciar grabación"

**Causa:** Dispositivo de audio no disponible o driver faltante

**Solución:**
```python
# 1. Listar dispositivos:
from recording_manager import get_audio_recorder
recorder = get_audio_recorder()
devices = recorder.list_devices()
print(devices)

# 2. Si la lista está vacía:
# - Windows: Instalar drivers de audio desde Device Manager
# - macOS: Usar System Preferences > Sound
# - Linux: instalar pulseaudio o alsa

# 3. Usar dispositivo específico:
recorder.start_recording(
    ...,
    device_index=0  # Especificar índice
)
```

### Problema: "Socket.IO no conecta en dashboard_mobile.html"

**Causa:** Servidor Flask no está ejecutándose o CORS bloqueado

**Solución:**
```python
# En server.py, asegurar:
from flask_socketio import SocketIO

socketio = SocketIO(
    app,
    cors_allowed_origins="*",  # Permitir todos los orígenes
    ping_timeout=60,
    ping_interval=25
)

# Iniciar con debug:
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
```

### Problema: "Archivos WAV muy grandes"

**Causa:** Frecuencia de muestreo muy alta o grabaciones largas

**Solución:**
```python
# Reducir frecuencia de muestreo (64 KB/s vs 176 KB/s):
recorder = initialize_audio_recorder(sample_rate=16000)

# O comprimir archivos periódicamente:
import os
for f in os.listdir("recordings"):
    if f.endswith(".wav"):
        size_mb = os.path.getsize(f) / (1024*1024)
        if size_mb > 100:  # Si supera 100 MB
            os.remove(f)  # Eliminar antiguas
```

---

## 📊 Comparativa de Versiones

| Característica | v1.0 | v1.0.1 | v1.0.1.1 | v1.0.1.2 |
|----------------|------|--------|----------|----------|
| Rastreo de Tiempo | ✅ | ✅ | ✅ | ✅ Mejorado |
| Dashboards Multi-Rol | ❌ | ✅ | ✅ | ✅ Expandido |
| Chat IA | ❌ | ❌ | ❌ | ✅ **NEW** |
| Grabación Audio | ❌ | ❌ | ❌ | ✅ **NEW** |
| Dashboard Móvil HTML5 | ❌ | ❌ | ❌ | ✅ **NEW** |
| Ollama Integration | ❌ | ❌ | ❌ | ✅ **NEW** |
| Socket.IO Real-time | ❌ | ❌ | Básico | ✅ Mejorado |
| Excel Export | ✅ | ✅ | ✅ | ✅ Expandido |

---

## 📝 Cambio Log v1.0.1.2

### Nuevos Archivos
- ✨ `client/ai_assistant.py` - AICopilot v1.0.1.2
- ✨ `client/recording_manager.py` - AudioRecorder v1.0.1.2
- ✨ `templates/dashboard_mobile.html` - Dashboard HTML5
- ✨ `CALLMANAGER_v1.0.1.2_COMPLETO.md` - Documentación

### Actualizaciones
- 🔄 `requirements.txt` - Nuevas dependencias (sounddevice, soundfile, numpy)

### Mejoras
- 🚀 AICopilot con modelo intercambiable (llama3, mistral, neural-chat)
- 🚀 AudioRecorder con metadata automática y estadísticas
- 🚀 Dashboard Móvil responsive con gráficos interactivos
- 🚀 Socket.IO eventos para actualización en vivo
- 🚀 Mejor manejo de errores y logging

---

## 🎯 Próximos Pasos Recomendados

### Fase 1: Instalación (30 minutos)
1. Instalar dependencias: `pip install -r requirements.txt`
2. Instalar Ollama: https://ollama.ai/
3. Descargar modelo: `ollama pull llama3`
4. Iniciar servidor: `ollama serve`

### Fase 2: Integración (1-2 horas)
1. Integrar `ai_assistant.py` en `call_manager_app.py`
2. Integrar `recording_manager.py` en `call_manager_app.py`
3. Verificar Socket.IO en `server.py`
4. Test de Dashboard móvil en navegador

### Fase 3: Customización (2-4 horas)
1. Ajustar prompts de IA según tu negocio
2. Configurar contexto para productos/servicios
3. Personalizar threshold de grabación
4. Customizar colores/estilos del dashboard

---

## 📞 Soporte

Para issues o preguntas:
1. Revisar sección **Troubleshooting**
2. Verificar logs: `tail -f /tmp/callmanager.log`
3. Test endpoints: `curl http://localhost:5000/health`
4. Test Ollama: `ollama list`

---

**Versión:** 1.0.1.2  
**Última actualización:** Noviembre 22, 2025  
**Status:** ✅ Producción Lista  
**Soporte:** v1.0.1 y anteriores depreciadas

---

*"Transformando call centers con IA local, grabación profesional y dashboards en tiempo real."* 🚀
