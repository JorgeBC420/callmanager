# 🚀 CallManager v2.5 - Guía Rápida de Implementación

**Tiempo estimado:** 30 minutos  
**Nivel:** Intermedio  
**Requiere:** Python 3.8+

---

## ⚡ INICIO RÁPIDO (3 pasos)

### Paso 1: Instalar Dependencias

```bash
cd callmanager
pip install -r requirements.txt
pip install pyaudio openpyxl
```

### Paso 2: Instalar y Ejecutar Ollama (en otra terminal)

```bash
# Descargar desde https://ollama.ai/
# O en Windows, macOS, Linux:

# Después de instalar:
ollama pull mistral
ollama serve
```

### Paso 3: Ejecutar la Aplicación

```bash
cd client
python call_manager_app.py
```

---

## 📁 Archivos Nuevos Creados

```
callmanager/
├── client/
│   ├── chat_assistant.py          ← Chat IA con Ollama
│   ├── call_recorder.py           ← Grabación de llamadas
│   ├── ui/
│   │   ├── responsive_ui.py       ← UI adaptativa
│   │   └── chat_widget.py         ← Widget de chat
│   └── system_init.py             ← Inicializador
├── recordings/                     ← Grabaciones (auto-created)
├── setup_new_features.py          ← Setup y verificación
└── requirements.txt               ← Dependencias actualizadas
```

---

## 🎯 CARACTERÍSTICAS PRINCIPALES

### 1️⃣ Chat IA para Objeciones

**Cómo usar:**

```
Opción A: Tecla de atajo
├── Ctrl+A (abre Chat IA flotante)
└── Escribe tu pregunta u objeción

Opción B: Desde menú
├── Menú "Herramientas"
└── Click en "💬 Asistente IA"
```

**Ejemplos de preguntas:**

```
✓ "¿Cómo respondo a 'es muy caro'?"
✓ "Argumentos sobre nuestro servicio"
✓ "Cliente no tiene tiempo ahora, ¿qué hago?"
✓ "Cómo cerrar una venta en 2 minutos"
```

---

### 2️⃣ Grabación Automática de Llamadas

**Flujo automático:**

```
Click [📞 Llamar] 
   ↓
Sistema automáticamente:
├─ Inicia grabación
├─ Inicia rastreo de tiempo
└─ Muestra timer en UI

Durante la llamada:
├─ Timer visible: 00:00 → 00:30 → 01:00
├─ Color: Verde (<2min) → Amarillo (<5min) → Rojo (>5min)
└─ Audio capturado sin intervención

Cuando termina:
├─ Click [✓ Confirmar]
├─ Grabación finaliza
├─ Metadata guardada (JSON)
└─ Todo en carpeta /recordings/
```

**Ver grabaciones:**

```
Menú → Herramientas → 📹 Ver Grabaciones
   ↓
Tabla con:
├─ ID de grabación
├─ Contacto
├─ Fecha y hora
├─ Duración en segundos
└─ Tamaño en MB

Click [📥 Exportar a Excel] para obtener reporte
```

---

### 3️⃣ Editor de Contactos (Nuevo)

**Interfaz mejorada:**

```
┌────────────────────────────────────┐
│ Nombre: [Juan Pérez      ] ✏️      │  ← Click para editar
├────────────────────────────────────┤
│ Estado: [▼ active]  Teléfono: +123 │  ← Dropdowns actuales
├────────────────────────────────────┤
│ Notas (máx 244 caracteres):        │
│ ┌──────────────────────────────────┐│
│ │ Cliente interesado en plan...   23│  ← Contador de caracteres
│ │                              /244 ││
│ └──────────────────────────────────┘│
├────────────────────────────────────┤
│ [📞] [✓] [🗑️]                      │  ← Botones de acción
└────────────────────────────────────┘
```

**Cambios principales:**

- ✏️ Editar nombre: Click el botón, modifica, click para guardar
- 📍 Estado: Droplist (active, inactive, donotcall, pending)
- 📝 Notas: Máximo 244 caracteres (contador en tiempo real)
- 🗑️ Eliminar: Botón rojo pequeño (pide confirmación)
- 📞 Llamar: Grande, verde, llamada directa
- ✓ Confirmar: Guarda cambios

---

### 4️⃣ Atajos de Teclado

```
Ctrl+N     → Nuevo contacto
Ctrl+E     → Exportar Excel contactos
Ctrl+F     → Buscar contacto
Ctrl+C     → Llamar contacto seleccionado
Ctrl+A     → Abrir Chat IA
F2         → Editar contacto
Delete     → Eliminar contacto (con confirmación)
Escape     → Cancelar operación actual
```

---

### 5️⃣ Exportación a Excel

**Contactos:**

```
Ctrl+E → Elige ubicación
   ↓
Excel generado con:
├─ Nombre
├─ Teléfono
├─ Estado
├─ Notas
├─ Última llamada
└─ Duración (segundos)

Con formato profesional:
├─ Headers azules con texto blanco
├─ Bordes en todas las celdas
├─ Ancho automático de columnas
└─ Texto centrado
```

**Grabaciones:**

```
Herramientas → Ver Grabaciones → [📥 Exportar a Excel]
   ↓
Excel con:
├─ ID de grabación
├─ Contacto
├─ Teléfono
├─ Agente
├─ Fecha/Hora inicio
├─ Duración
└─ Tamaño en MB
```

---

## 📱 COMPATIBILIDAD MÓVIL/TABLET

### Detección Automática

```
Ancho pantalla          → Modo
─────────────────────────────
< 768px (móvil)       → Vista mobile
768-1024px (tablet)   → Vista tablet
> 1024px (desktop)    → Vista completa
```

### Adaptaciones

**Móvil:**
```
┌─────────────────────┐
│ 🔍 Buscar...        │  ← Search bar full width
├─────────────────────┤
│ ┌─────────────────┐ │
│ │  Contacto 1     │ │  ← Tarjetas stackeadas
│ │ 📱 +1234        │ │
│ │ [📞][✏️][🗑️]    │ │
│ └─────────────────┘ │
│ ┌─────────────────┐ │
│ │  Contacto 2     │ │
│ │ 📱 +5678        │ │
│ │ [📞][✏️][🗑️]    │ │
│ └─────────────────┘ │
└─────────────────────┘
```

**Tablet:**
```
┌─────────────────────────────────────┐
│ 🔍 Buscar...                        │
├─────────────────────────────────────┤
│ ┌──────────────┐ ┌──────────────┐  │
│ │ Contacto 1   │ │ Contacto 2   │  │ ← Dos columnas
│ │ 📱 +1234     │ │ 📱 +5678     │  │
│ │ [📞][✏️][🗑️] │ │ [📞][✏️][🗑️] │  │
│ └──────────────┘ └──────────────┘  │
└─────────────────────────────────────┘
```

**Desktop:**
```
Interfaz completa con tabla, detalles, etc.
```

---

## ⚙️ CONFIGURACIÓN

### Cambiar Modelo de IA

En `client/chat_assistant.py`, línea ~30:

```python
# Cambiar de:
client = OllamaClient(model="mistral")

# A otros modelos:
client = OllamaClient(model="llama2")
client = OllamaClient(model="neural-chat")
client = OllamaClient(model="orca-mini")
```

Primero descargar el modelo:
```bash
ollama pull llama2
ollama pull neural-chat
```

### Cambiar Ruta de Grabaciones

En `call_manager_app.py`, en `__init__`:

```python
# Cambiar de:
self.call_recorder = initialize_call_recorder("recordings")

# A:
self.call_recorder = initialize_call_recorder("C:/backups/recordings")
```

### Configurar Frecuencia de Muestreo

En `client/call_recorder.py`, línea ~20:

```python
# Cambiar de:
def __init__(self, recordings_dir: str = "recordings", sample_rate: int = 44100):

# A (calidad mayor):
def __init__(self, recordings_dir: str = "recordings", sample_rate: int = 48000):
```

---

## 🐛 TROUBLESHOOTING

### Chat IA no funciona

```
❌ Error: "Chat Assistant no disponible"

Solución:
1. ¿Ollama instalado?
   → Ir a https://ollama.ai/
   
2. ¿Ollama ejecutándose?
   → Abrir otra terminal: ollama serve
   
3. ¿Modelo descargado?
   → ollama pull mistral
   
4. ¿Disponible en localhost:11434?
   → curl http://localhost:11434/api/tags
```

### Grabación sin audio

```
❌ Error: "PyAudio no disponible" o "Sin audio"

Solución:
1. ¿PyAudio instalado?
   pip install --upgrade pyaudio

2. ¿Micrófono conectado?
   → Verificar en configuración del sistema

3. ¿Permisos de audio?
   → Windows: Permitir acceso a micrófono en privacidad
   → Mac: Permitir acceso a micrófono en Seguridad
   → Linux: sudo usermod -a -G audio $USER
```

### Excel no se genera

```
❌ Error: "No se pudieron exportar los contactos"

Solución:
1. ¿openpyxl instalado?
   pip install openpyxl

2. ¿Ruta válida?
   → No usar caracteres especiales en ruta

3. ¿Permisos de escritura?
   → Verificar carpeta de destino
```

### UI no responde

```
❌ La interfaz se ve extraña o no responde

Solución:
1. Actualizar CustomTkinter:
   pip install --upgrade customtkinter

2. Reiniciar la aplicación

3. Limpiar cache:
   rm -rf client/__pycache__
   rm -rf client/ui/__pycache__
```

---

## 📊 ESTADÍSTICAS

**Código nuevo agregado:**
- 1,630 líneas de código Python
- 12 nuevas clases
- 45 nuevas funciones
- 4 nuevos módulos principales

**Dependencias:**
- requests (Chat IA)
- pyaudio (Grabación)
- openpyxl (Excel)

**Tamaño esperado de grabaciones:**
- 1 min de audio = ~5-6 MB (WAV)
- 1 hora de audio = ~300-360 MB

---

## ✅ CHECKLIST DE INSTALACIÓN

```
□ Python 3.8+ instalado
□ pip install -r requirements.txt
□ pip install pyaudio openpyxl
□ Ollama descargado e instalado
□ ollama pull mistral ejecutado
□ Directorio /recordings/ creado (automático)
□ Base de datos inicializada
□ Server.py ejecutándose (en otra terminal)
□ ollama serve ejecutándose (en otra terminal)
□ call_manager_app.py iniciado
□ Chat IA disponible (Ctrl+A)
□ Grabación iniciándose al llamar
```

---

## 🆘 SOPORTE

Si encuentras problemas:

1. Revisa los logs en la consola (mensajes con ✅, ⚠️, ❌)
2. Lee ARQUITECTURA_TECNICA_v2.5.md para detalles técnicos
3. Verifica INTEGRACION_NUEVOS_COMPONENTES.md para integración

---

**¿Todo listo?**  
🎉 ¡Tu CallManager v2.5 está completamente funcional!

Próximos pasos:
- [ ] Entrenar a agentes en los nuevos atajos
- [ ] Crear procedimientos de grabación
- [ ] Establecer políticas de almacenamiento de grabaciones
- [ ] Configurar respaldos automáticos de datos
