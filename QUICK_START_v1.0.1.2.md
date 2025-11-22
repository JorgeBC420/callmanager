# 🚀 QUICK START - CallManager v1.0.1.2

**Última revisión:** Noviembre 22, 2025  
**Versión:** 1.0.1.2 (anterior: 1.0.1.1)  
**Tiempo estimado:** 10 minutos

---

## ⚡ En 10 Minutos, Tendrás TODO Funcionando

### Requisito Previo: Python 3.9+
```bash
python --version
```

---

## 📋 Los 5 Pasos

### Paso 1️⃣ | Instalar Dependencias (2 minutos)

```bash
cd c:\Users\bjorg\OneDrive\Desktop\callmanager
pip install -r requirements.txt
```

**Verifica:**
```bash
pip list | grep sounddevice
pip list | grep soundfile
```

**Resultado esperado:** ✅ Ambos instalados

---

### Paso 2️⃣ | Instalar Ollama (3 minutos)

**Windows:**
1. Descargar: https://ollama.ai/
2. Ejecutar instalador (.exe)
3. En PowerShell:
```bash
ollama --version
```

**Mac/Linux:**
```bash
brew install ollama  # macOS
# O visita https://ollama.ai/ para Linux
```

**Resultado esperado:** Versión mostrada (ej: ollama version 0.1.0)

---

### Paso 3️⃣ | Descargar Modelo (2 minutos)

```bash
ollama pull llama3
```

**Verifica:**
```bash
ollama list
```

**Resultado esperado:**
```
NAME            ID              SIZE    MODIFIED
llama3:latest   xxxxxxxxxxxxxx  4.7 GB  2 minutes ago
```

---

### Paso 4️⃣ | Iniciar Servidor Ollama (1 minuto)

**En una terminal NUEVA** (dejarla abierta):

```bash
ollama serve
```

**Resultado esperado:**
```
Pulling layers...
Loaded weights...
Server listening on 127.0.0.1:11434
```

🎉 Ollama está corriendo en `http://localhost:11434`

---

### Paso 5️⃣ | Ver Dashboard (2 minutos)

**En navegador:**
```
http://localhost:5000/mobile
```

**Si no carga:**
```bash
# En otra terminal, iniciar Flask:
python server.py
```

**Resultado esperado:** Dashboard móvil carga con métricas

---

## ✅ Verificación Rápida

### Test 1: ¿Ollama funciona?
```bash
curl http://localhost:11434/api/tags
```
Debería retornar JSON con lista de modelos.

### Test 2: ¿Flask funciona?
```bash
curl http://localhost:5000/health
```
Debería retornar:
```json
{"status": "ok", "components": {...}}
```

### Test 3: ¿Dashboard carga?
Abre navegador: `http://localhost:5000/mobile`

---

## 💬 Chat IA - Test Rápido

**En Python:**
```python
from client.ai_assistant import initialize_ai_copilot
import time

copilot = initialize_ai_copilot()

def show_response(resp):
    print(f"💬 Respuesta: {resp}")

copilot.get_response(
    "Es muy caro",
    context="Internet Fibra 300Mbps",
    callback=show_response
)

time.sleep(3)  # Esperar respuesta
```

**Resultado esperado:** Respuesta en 2-3 segundos

---

## 🎙️ Grabación - Test Rápido

**En Python:**
```python
from client.recording_manager import initialize_audio_recorder
import time

recorder = initialize_audio_recorder()

# Ver dispositivos
print(recorder.list_devices())

# Grabar 5 segundos
rec = recorder.start_recording(
    filename="test",
    contact_name="Cliente Test"
)
time.sleep(5)

metadata = recorder.stop_recording()
print(f"✅ Grabado: {metadata['duration_seconds']}s")
```

**Resultado esperado:** Archivo WAV + JSON en carpeta `recordings/`

---

## 📁 Estructura de Archivos Creados

```
callmanager/
├── client/
│   ├── ai_assistant.py              ✨ Chat IA
│   ├── recording_manager.py         ✨ Grabación
│   └── ... (otros archivos)
│
├── templates/
│   └── dashboard_mobile.html        ✨ Dashboard móvil
│
├── server_integration_v1.0.1.2.py  ✨ Integración
│
├── CALLMANAGER_v1.0.1.2_COMPLETO.md ✨ Docs técnica
├── RESUMEN_EJECUTIVO_v1.0.1.2.md   ✨ Para jefes
├── INDICE_v1.0.1.2.md              ✨ Índice
├── VERIFICACION_FINAL_v1.0.1.2.md  ✨ Verificación
├── QUICK_START_v1.0.1.2.md         ✨ Este archivo
│
└── requirements.txt                 ✨ Actualizado
```

---

## 🔧 Troubleshooting Rápido

| Problema | Solución |
|----------|----------|
| "Ollama no funciona" | Ejecutar `ollama serve` en terminal aparte |
| "Modelo no encontrado" | Ejecutar `ollama pull llama3` |
| "Flask puerto ocupado" | Cambiar puerto en `server.py` línea 500 |
| "Error de audio" | Ejecutar `recorder.list_devices()` para verificar |
| "Archivo grabación grande" | Reducir sample_rate a 16000 en `recording_manager.py` |

---

## 🎯 Próximo Paso (Recomendado)

📖 **Lee:** `RESUMEN_EJECUTIVO_v1.0.1.2.md` (10 minutos)

Luego:

1. **Técnicos:** Lee `CALLMANAGER_v1.0.1.2_COMPLETO.md`
2. **Managers:** Entiende ROI en `RESUMEN_EJECUTIVO_v1.0.1.2.md`
3. **Usuarios:** Aprende shortcuts en dashboard

---

## 💡 Funcionalidades Principales

### 1️⃣ Chat IA (Ollama)
**Acceso:** Botón "💬 Ayuda IA" en aplicación  
**Modelos:** llama3 (default), mistral, neural-chat  
**Velocidad:** 2-3 segundos  
**Privacidad:** Local, sin internet  

### 2️⃣ Grabación Automática
**Acceso:** Automática en cada llamada  
**Formato:** WAV 44.1kHz (CD quality)  
**Metadata:** JSON con participantes y duración  
**Almacenamiento:** Carpeta `recordings/`  

### 3️⃣ Dashboard Móvil
**Acceso:** `http://localhost:5000/mobile`  
**Dispositivos:** Móvil, tablet, desktop  
**Actualización:** Tiempo real (Socket.IO)  
**Datos:** Métricas, gráficos, grabaciones  

---

## 📊 Lo Que Verás

### Dashboard Móvil

```
┌─────────────────────────────────────┐
│ 📞 CallManager v1.0.1.2             │
├─────────────────────────────────────┤
│                                     │
│  📞 Llamadas Hoy: 12                │
│  💰 Ventas: 3                       │
│  📊 Tasa Éxito: 25%                 │
│  ⏱️  Tiempo Total: 2h 5m            │
│                                     │
├─ Pestañas ─────────────────────────│
│  📊 Dashboard  👥 Equipo  🎙️ Grabs  │
│                                     │
│  📈 [Gráfico de estado]             │
│  📊 [Gráfico de tendencia]          │
│                                     │
└─────────────────────────────────────┘
```

---

## ⏱️ Cronograma Detallado

```
Minuto 0-2:   Instalar pip packages
Minuto 2-5:   Instalar Ollama + descargar modelo
Minuto 5-6:   Iniciar Ollama Server
Minuto 6-7:   Verificar Ollama con curl
Minuto 7-10:  Iniciar Flask y ver Dashboard
─────────────────────────────────────
Total:        10 minutos ✅
```

---

## 🎓 Comandos Útiles

### Ver status
```bash
curl http://localhost:5000/health
```

### Ver modelos Ollama
```bash
curl http://localhost:11434/api/tags
```

### Listar grabaciones
```bash
python -c "from client.recording_manager import get_audio_recorder; r = get_audio_recorder(); print(r.list_recordings())"
```

### Limpiar grabaciones antiguas
```bash
python -c "from client.recording_manager import get_audio_recorder; r = get_audio_recorder(); r.get_statistics()"
```

---

## 📱 URLs Importantes

| URL | Propósito |
|-----|----------|
| `http://localhost:5000/mobile` | Dashboard móvil |
| `http://localhost:5000/health` | Status del servidor |
| `http://localhost:11434/api/tags` | Modelos Ollama |
| `http://localhost:5000/api/ai/status` | Status de AICopilot |

---

## 📚 Documentación Rápida

| Documento | Audience | Tiempo |
|-----------|----------|--------|
| Este archivo | Todos | 5 min |
| RESUMEN_EJECUTIVO_v1.0.1.2.md | Ejecutivos | 10 min |
| CALLMANAGER_v1.0.1.2_COMPLETO.md | Técnicos | 30 min |
| INDICE_v1.0.1.2.md | Navegación | 5 min |

---

## ✨ Características Destacadas

- ✅ Chat IA local (sin internet requerido)
- ✅ Grabación automática de llamadas
- ✅ Dashboard responsivo (móvil/tablet/desktop)
- ✅ Tiempo real con Socket.IO
- ✅ Gráficos interactivos
- ✅ Exportación a Excel
- ✅ Auditoría completa

---

## 🎯 Success Criteria

✅ Ollama levantado y funcionando  
✅ Modelos descargados (llama3)  
✅ Flask servidor en puerto 5000  
✅ Dashboard móvil cargando  
✅ Chat IA respondiendo en 2-3s  
✅ Grabación creando archivos WAV  

Si tienes los 6 puntos: **¡Felicidades, todo funciona!** 🎉

---

## 🚀 Ready to Go!

```
┌─────────────────────────────────────┐
│                                     │
│  🎉 CALLMANAGER v1.0.1.2           │
│                                     │
│  ✅ Chat IA (Ollama)                │
│  ✅ Grabación Automática            │
│  ✅ Dashboard Móvil HTML5           │
│                                     │
│  STATUS: LISTO PARA PRODUCCIÓN     │
│                                     │
│  Próximo: Lee documentación técnica │
│                                     │
└─────────────────────────────────────┘
```

---

## 📞 Soporte

**Si algo no funciona:**
1. Verifica `curl http://localhost:11434/api/tags`
2. Verifica `curl http://localhost:5000/health`
3. Lee sección "Troubleshooting" en documento principal
4. Revisa logs en terminal

---

**¡Disfruta CallManager v1.0.1.2! 🚀**

*Próximo paso: RESUMEN_EJECUTIVO_v1.0.1.2.md*

---

**Versión:** 1.0.1.2  
**Fecha:** Noviembre 22, 2025  
**Status:** ✅ LISTO PARA PRODUCCIÓN
