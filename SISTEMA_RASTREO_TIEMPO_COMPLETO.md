# 🕐 Sistema Completo de Rastreo de Tiempo en Llamadas

## Descripción General

Se ha implementado un **sistema end-to-end de rastreo de tiempo de llamadas** que registra automáticamente:
- Inicio y fin de cada llamada
- Duración en segundos
- Estado (COMPLETADA, FALLIDA, SIN_RESPUESTA)
- Métricas agregadas (promedio, total, etc.)

El sistema es **automático, escalable y está integrado en toda la aplicación**.

---

## Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                    USUARIO HACE LLAMADA                    │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│          call_manager_app.py: call_contact()              │
│  - Inicia CallTracker.start_call()                         │
│  - Ejecuta llamada (InterPhone/Skype/etc)                  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│         call_tracking.py: CallTracker.start_call()         │
│  - Envía POST /api/calls/start al servidor                 │
│  - Recibe call_id único                                     │
│  - Inicia TimerThread para actualizar UI cada segundo      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│       server.py: POST /api/calls/start                     │
│  - Crea registro CallLog                                    │
│  - Estado: IN_PROGRESS                                      │
│  - Retorna call_id                                          │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┴────────────────┐
        │                                 │
    [LLAMADA ACTIVA]                      │
    [TIMER CORRIENDO]                     │
        │                                 │
        └────────────────┬────────────────┘
                         │
                         ▼ (Usuario cuelga o timeout)
┌─────────────────────────────────────────────────────────────┐
│   call_manager_app.py: end_current_call(status)            │
│  - Llama CallTracker.end_call(status)                       │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│       call_tracking.py: CallTracker.end_call()             │
│  - Envía POST /api/calls/end al servidor                   │
│  - Detiene TimerThread                                      │
│  - Resetea UI timer a 00:00                                 │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│        server.py: POST /api/calls/end                      │
│  - Calcula duration = end_time - start_time                │
│  - Actualiza CallLog (duration_seconds, status)            │
│  - Actualiza UserMetrics:                                  │
│    * calls_made += 1                                        │
│    * calls_success += 1 (si status == COMPLETED)           │
│    * calls_failed += 1 (si no)                             │
│    * total_talk_time += duration_seconds                   │
│    * avg_call_duration = total_talk_time / calls_made      │
│  - Emite evento SocketIO para actualizar dashboards        │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│    metrics_dashboard.py: Recibe datos actualizados          │
│  - Actualiza tarjetas KPI en tiempo real                    │
│  - Muestra: Llamadas, AHT, Tasa de éxito, etc              │
└─────────────────────────────────────────────────────────────┘
```

---

## Componentes Implementados

### 1. **Base de Datos (server.py)**

#### Modelo: `CallLog`
```python
class CallLog(Base):
    id: String              # ID único
    user_id: String         # Usuario que hizo la llamada
    contact_id: String      # Contacto llamado
    contact_phone: String   # Número de teléfono
    start_time: DateTime    # Cuándo empezó
    end_time: DateTime      # Cuándo terminó
    duration_seconds: Int   # Duración calculada
    status: String          # COMPLETED, DROPPED, NO_ANSWER, FAILED
    notes: Text             # Notas adicionales
    created_at: DateTime    # Registro creado
```

#### Actualización: `UserMetrics`
```python
class UserMetrics(Base):
    # ... campos existentes ...
    total_talk_time: Int      # Total en segundos hablando (NUEVO)
    avg_call_duration: Int    # Promedio en segundos (ACTUALIZADO)
```

---

### 2. **Endpoints del Servidor (server.py)**

#### `POST /api/calls/start`
**Registra el inicio de una llamada**

Solicitud:
```json
{
    "contact_id": "contact_123",
    "contact_phone": "+506-5123-4567"
}
```

Respuesta (201 Created):
```json
{
    "message": "Call started",
    "call_id": "call_1700000000000_user_001",
    "start_time": "2024-11-22T14:30:00"
}
```

---

#### `POST /api/calls/end`
**Registra el fin de una llamada y actualiza métricas**

Solicitud:
```json
{
    "call_id": "call_1700000000000_user_001",
    "status": "COMPLETED",
    "notes": "Venta exitosa"
}
```

Respuesta (200 OK):
```json
{
    "message": "Call ended",
    "call_id": "call_1700000000000_user_001",
    "duration_seconds": 245,
    "new_average": 180,
    "calls_made": 5,
    "calls_success": 4,
    "total_talk_time": 900
}
```

**Efectos secundarios:**
- Actualiza `CallLog` con duración y estado
- Incrementa `UserMetrics.calls_made`
- Incrementa `UserMetrics.calls_success` o `calls_failed` según status
- Suma duración a `UserMetrics.total_talk_time`
- Recalcula `UserMetrics.avg_call_duration`
- Emite evento SocketIO para actualizar dashboards en vivo

---

#### `GET /api/calls/log`
**Obtiene historial de llamadas (con filtros)**

Parámetros opcionales:
```
?user_id=agent_001
&start_date=2024-11-20
&end_date=2024-11-22
&status=COMPLETED
&limit=50
```

Respuesta (200 OK):
```json
[
    {
        "call_id": "call_1700000000000_user_001",
        "user_id": "agent_001",
        "contact_id": "contact_123",
        "contact_phone": "+506-5123-4567",
        "start_time": "2024-11-22T14:30:00",
        "end_time": "2024-11-22T14:34:05",
        "duration_seconds": 245,
        "status": "COMPLETED",
        "notes": ""
    },
    ...
]
```

---

### 3. **Cliente Python (client/call_tracking.py)**

#### Clase: `CallSession`
Representa una sesión de llamada individual.

```python
session = CallSession(
    call_id="call_123",
    contact_id="contact_456",
    contact_phone="+506-5123-4567"
)

# Cuando la llamada termina:
duration = session.end_call(status="COMPLETED")
# duration = 245 (segundos)
```

**Métodos:**
- `end_call(status)` → Finaliza y retorna duración
- `get_duration()` → Obtiene duración actual (en vivo)
- `to_dict()` → Convierte a diccionario para serializar

---

#### Clase: `CallTracker`
Gestor completo del rastreo de llamadas.

```python
# Inicializar
tracker = CallTracker(
    base_url="http://localhost:5000",
    api_key="dev-key-change-in-production"
)

# Establecer callback para actualizar UI cada segundo
tracker.set_timer_callback(lambda duration, formatted: print(f"{formatted}"))

# Iniciar llamada
call_id = tracker.start_call(
    contact_id="contact_123",
    contact_phone="+506-5123-4567"
)

# [Usuario está en llamada, timer corriendo en background]

# Finalizar llamada
metrics = tracker.end_call(
    status="COMPLETED",
    notes="Cliente satisfecho"
)

# Acceder a métricas
print(f"Duración: {metrics['duration_seconds']}s")
print(f"Nuevo promedio: {metrics['new_average']}s")
```

**Métodos principales:**
- `start_call(contact_id, contact_phone)` → Inicia rastreo, retorna call_id
- `end_call(status, notes)` → Finaliza rastreo, retorna métricas
- `get_current_duration()` → Duración actual (mientras está activa)
- `format_duration(seconds)` → Formatea como MM:SS o HH:MM:SS
- `set_timer_callback(callback)` → Registra callback para actualizaciones UI
- `get_metrics()` → Obtiene métricas de sesiones locales

---

### 4. **UI - Timer (client/call_manager_app.py)**

#### En el header:
```python
self.lbl_timer = ctk.CTkLabel(
    header,
    text="00:00",
    font=("Consolas", 16, "bold"),
    text_color="#888888"
)
```

#### Callback de actualización:
```python
def _on_timer_update(self, duration_seconds: int, formatted_time: str):
    """Se ejecuta cada segundo durante una llamada"""
    if duration_seconds > 300:  # > 5 minutos
        color = "#e74c3c"  # ROJO
    elif duration_seconds > 120:  # > 2 minutos
        color = "#f39c12"  # AMARILLO
    else:
        color = "#2ecc71"  # VERDE
    
    self.lbl_timer.configure(text=formatted_time, text_color=color)
```

El timer:
- Comienza en verde (00:00)
- Pasa a amarillo en 2 minutos
- Pasa a rojo en 5 minutos
- Se resetea a gris cuando termina la llamada

---

### 5. **Dashboard de Métricas (client/ui/metrics_dashboard.py)**

#### Clase: `MetricsDashboard`
Panel visual con tarjetas KPI y tablas de equipo.

**Tarjetas KPI:**
- 📊 Llamadas Realizadas
- ✅ Llamadas Exitosas
- ❌ Llamadas Fallidas
- ⏱️ AHT (Average Handle Time)
- ⏲️ Tiempo Total
- 📈 Tasa de Éxito (%)

**Vistas por rol:**
- **Agent:** Solo sus propias métricas
- **Supervisor/TeamLead:** Sus métricas + tabla de equipo
- **Admin/TI:** Toda la organización

**Características:**
- Actualización en tiempo real (botón Actualizar)
- Historial de llamadas (ventana modal)
- Filtros por fecha, usuario, estado
- Colores intuitivos (rojo/verde/amarillo)

---

## Flujo de Uso Práctico

### 1. **Inicio de Sesión**
```
App carga
↓
Establece: current_user_id, current_username, current_user_role
↓
CallTracker se inicializa automáticamente
```

### 2. **Realizar Llamada**
```
Usuario hace click en contacto
↓
call_contact(contact) se ejecuta
↓
CallTracker.start_call() envía al servidor
↓
Timer comienza a correr en header (00:00, 00:01, 00:02...)
↓
Llamada activa (InterPhone/Skype/etc)
```

### 3. **Terminar Llamada**
```
Usuario cuelga o hace click en botón "Finalizar"
↓
end_current_call("COMPLETED") se ejecuta
↓
CallTracker.end_call() envía duración al servidor
↓
Servidor actualiza CallLog y UserMetrics
↓
Dashboard se actualiza automáticamente
↓
Timer se resetea a 00:00 (gris)
```

### 4. **Ver Métricas**
```
Usuario hace click en botón "📊 Métricas"
↓
MetricsDashboard se abre
↓
Solicita datos a /metrics/personal y /metrics/team
↓
Muestra tarjetas KPI y tabla de equipo
↓
Botón "🔄 Actualizar" recarga datos
↓
Botón "📋 Historial" abre tabla completa de llamadas
```

---

## Ejemplos de Código

### Ejemplo 1: Usar CallTracker directamente

```python
from call_tracking import initialize_tracker

# Inicializar
tracker = initialize_tracker("http://localhost:5000", "api-key-123")

# Hacer llamada
call_id = tracker.start_call(
    contact_id="customer_123",
    contact_phone="+506-8765-4321"
)

# ... [usuario está hablando] ...

# Finalizar
metrics = tracker.end_call("COMPLETED", "Venta completada")

print(f"Duración: {metrics['duration_seconds']}s")
print(f"Promedio: {metrics['new_average']}s")
print(f"Total: {metrics['total_talk_time']}s")
```

### Ejemplo 2: Registrar callback para UI

```python
tracker = initialize_tracker("http://localhost:5000")

def update_ui_timer(duration, formatted):
    """Esto se ejecuta cada 1 segundo"""
    print(f"Tiempo en llamada: {formatted}")
    label.configure(text=formatted)

tracker.set_timer_callback(update_ui_timer)

# Ahora cada segundo se actualiza automáticamente
tracker.start_call("contact_id", "5123456789")
```

### Ejemplo 3: Obtener historial de llamadas

```python
import requests

headers = {'X-API-Key': 'your-api-key'}

# Historial de hoy
response = requests.get(
    'http://localhost:5000/api/calls/log',
    params={
        'start_date': '2024-11-22',
        'end_date': '2024-11-22',
        'limit': 50
    },
    headers=headers
)

calls = response.json()
for call in calls:
    print(f"{call['start_time']} - {call['duration_seconds']}s - {call['status']}")
```

---

## Almacenamiento de Datos

### Base de Datos SQLite (contacts.db)

**Tabla: `call_logs`**
- Registra cada llamada con precisión de segundos
- Indexada por: `user_id`, `start_time`, `status`
- Permite filtrado y reporting rápido

**Tabla: `user_metrics`**
- Una fila por usuario
- Se actualiza con cada llamada
- Mantiene totales acumulados

### Características:
- ✅ WAL Mode habilitado (mejor concurrencia)
- ✅ Índices en campos frecuentemente consultados
- ✅ Integridad referencial
- ✅ Backups automáticos

---

## Cálculos Automáticos

### Average Handle Time (AHT)
```
AHT = total_talk_time / calls_made
Ejemplo: 2400s / 10 llamadas = 240s = 4 minutos
```

### Tasa de Éxito
```
Success Rate = (calls_success / calls_made) * 100
Ejemplo: 9 / 10 = 90%
```

### Tiempo Total
```
Total = total_talk_time en segundos
Ejemplo: 2400s = 40 minutos
```

---

## Seguridad y Validaciones

✅ **API Key Required** - Todas las rutas requieren X-API-Key
✅ **Rate Limiting** - 1000 requests/hora por defecto
✅ **SQL Injection Prevention** - ORM SQLAlchemy
✅ **Input Validation** - Valores numéricos y tipos chequeados
✅ **Error Handling** - Excepciones capturadas con logging
✅ **Thread Safety** - Lock en CallTracker para acceso concurrente

---

## Troubleshooting

### "Call ID not found"
**Causa:** Servidor reiniciado o sesión expirada
**Solución:** Iniciar nueva llamada con `start_call()`

### "Timer no se actualiza"
**Causa:** Callback no registrado
**Solución:** Verificar que `set_timer_callback()` se llamó

### "Métricas no se actualizan"
**Causa:** SocketIO no conectado
**Solución:** Verificar conexión al servidor

### "Duración = 0 segundos"
**Causa:** Llamada muy rápida o error al guardar
**Solución:** Verificar logs del servidor

---

## Próximas Mejoras

- [ ] Pausa/reanudación de llamadas
- [ ] Grabación de duración local (offline)
- [ ] Sincronización al reconectar
- [ ] Reportes PDF automáticos
- [ ] Integraciones con Slack/Teams para notificaciones
- [ ] Machine Learning para predicción de duración
- [ ] Análisis de patrones de llamadas

---

## Conclusión

El sistema de rastreo de tiempo es:
- ✅ **Automático:** Se inicia y termina sin intervención manual
- ✅ **Preciso:** Registra duración hasta el segundo
- ✅ **Escalable:** Soporta miles de llamadas por día
- ✅ **Integrado:** Funciona con todos los proveedores de llamadas
- ✅ **Visual:** Muestra métricas en tiempo real
- ✅ **Auditable:** Historial completo de cada llamada

Tu aplicación ahora tiene **visibilidad total sobre los tiempos de llamadas**.
