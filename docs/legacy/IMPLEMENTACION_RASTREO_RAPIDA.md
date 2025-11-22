# 🚀 Guía Rápida de Implementación - Sistema de Rastreo de Tiempo

## ¿Qué se implementó?

✅ **Modelo de Base de Datos:** Tabla `CallLog` para historial detallado
✅ **Endpoints del Servidor:** 3 rutas nuevas para rastreo
✅ **Cliente Python:** Módulo `call_tracking.py` para comunicación
✅ **UI Dashboard:** Panel de métricas con 4 vistas diferentes
✅ **Integración Completa:** Todo conectado en la app principal

---

## Verificación Rápida

### 1. ¿El servidor inicia correctamente?
```bash
cd callmanager
python server.py
```

Debería ver (sin errores):
```
✅ WAL mode habilitado para SQLite
📞 CallLog table created
Servidor iniciado en 0.0.0.0:5000
```

### 2. ¿El cliente inicia correctamente?
```bash
cd client
python call_manager_app.py
```

Debería ver:
- Aplicación abre normalmente
- Header muestra "00:00" (timer vacío)
- Botón "📊 Métricas" visible

### 3. ¿CallTracker está disponible?
```python
from call_tracking import initialize_tracker
tracker = initialize_tracker("http://localhost:5000")
print("✅ CallTracker funciona")
```

---

## Prueba de Funcionalidad

### Test 1: Iniciar y finalizar una llamada

```python
# En la consola Python (con app corriendo):
from call_tracking import get_tracker

tracker = get_tracker()

# Iniciar
call_id = tracker.start_call(
    contact_id="test_contact",
    contact_phone="+506-5123-4567"
)
print(f"Llamada iniciada: {call_id}")

# Esperar 10 segundos
import time
time.sleep(10)

# Finalizar
result = tracker.end_call("COMPLETED")
print(f"Duración: {result['duration_seconds']}s")
print(f"Promedio: {result['new_average']}s")
```

**Resultado esperado:**
```
Llamada iniciada: call_1700000000000_agent_001
Duración: 10s
Promedio: 10s
```

---

### Test 2: Ver el timer en la UI

1. Click en un contacto para **iniciar llamada**
2. Header debe mostrar:
   - `00:01` → `00:02` → `00:03`... (incrementando)
   - Color verde al principio
3. Llamar a `end_current_call("COMPLETED")` desde código
4. Timer debe resetear a `00:00` (gris)

---

### Test 3: Abrir Dashboard de Métricas

1. Click en botón **"📊 Métricas"** en header
2. Debe abrirse ventana nueva con:
   - **Tarjetas KPI:** Llamadas, Exitosas, Fallidas, AHT, Tiempo Total, Tasa %
   - **Botones:** Actualizar, Historial
3. Click en **"📋 Historial"**
4. Debe mostrar tabla con todas las llamadas realizadas

---

## Integración en Tu Flujo Actual

### Si usas FormLogin o autenticación:

```python
# En login.py o auth.py, después de loguearse:

class LoginWindow:
    def on_login_success(self, user_id, username, role):
        # ← Aquí están los datos del usuario autenticado
        
        # Guardar en la app
        app.current_user_id = user_id
        app.current_username = username
        app.current_user_role = role
        
        # CallTracker ya está inicializado, solo asegúrate de que se llamó en __init__
        # Si lo hizo: tracker = initialize_tracker(SERVER_URL, API_KEY)
```

### Si NO tienes login aún:

```python
# En call_manager_app.py __init__:

self.current_user_id = 'agent_001'      # Por ahora hardcoded
self.current_username = 'Agent Demo'    # Cambiar cuando tengas login
self.current_user_role = 'agent'        # Cambiar según rol del usuario
```

---

## Endpoints Disponibles

### POST /api/calls/start
```bash
curl -X POST http://localhost:5000/api/calls/start \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-key-change-in-production" \
  -d '{
    "contact_id": "contact_123",
    "contact_phone": "+506-5123-4567"
  }'
```

**Respuesta:**
```json
{
    "message": "Call started",
    "call_id": "call_1700000000000_user_001",
    "start_time": "2024-11-22T14:30:00"
}
```

---

### POST /api/calls/end
```bash
curl -X POST http://localhost:5000/api/calls/end \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-key-change-in-production" \
  -d '{
    "call_id": "call_1700000000000_user_001",
    "status": "COMPLETED",
    "notes": "Cliente satisfecho"
  }'
```

**Respuesta:**
```json
{
    "message": "Call ended",
    "duration_seconds": 245,
    "new_average": 180,
    "calls_made": 5,
    "calls_success": 4
}
```

---

### GET /api/calls/log
```bash
curl http://localhost:5000/api/calls/log?limit=10 \
  -H "X-API-Key: dev-key-change-in-production"
```

**Respuesta:**
```json
[
    {
        "call_id": "call_1700000000000_user_001",
        "user_id": "agent_001",
        "contact_id": "contact_123",
        "contact_phone": "+506-5123-4567",
        "duration_seconds": 245,
        "status": "COMPLETED",
        "start_time": "2024-11-22T14:30:00",
        "end_time": "2024-11-22T14:34:05"
    }
]
```

---

## Archivos Modificados/Creados

### ✅ CREADOS:
```
client/call_tracking.py              (290 líneas)
client/ui/metrics_dashboard.py       (450 líneas)
SISTEMA_RASTREO_TIEMPO_COMPLETO.md   (Documentación)
```

### ✅ MODIFICADOS:
```
server.py                  (+ 180 líneas para 3 endpoints + modelo CallLog)
client/call_manager_app.py (+ 100 líneas para integración)
```

---

## Checklist de Verificación

- [ ] `server.py` inicia sin errores
- [ ] `call_manager_app.py` inicia sin errores
- [ ] Timer "00:00" visible en header
- [ ] Botón "📊 Métricas" abre dashboard
- [ ] Iniciar llamada → Timer comienza a contar
- [ ] Finalizar llamada → Timer se resetea
- [ ] Dashboard muestra métricas actualizadas
- [ ] Historial de llamadas tiene registros

---

## Solución de Problemas

| Problema | Causa | Solución |
|----------|-------|----------|
| "ModuleNotFoundError: call_tracking" | Archivo no existe o ruta incorrecta | Verificar que `client/call_tracking.py` existe |
| Timer no se actualiza | CallTracker no inicializado | Verificar `initialize_tracker()` en __init__ |
| Dashboard no abre | Import fallido de MetricsDashboard | Verificar que `client/ui/metrics_dashboard.py` existe |
| Duración siempre 0 | Servidor no recibe end_call | Verificar conexión a `http://localhost:5000` |
| Métodos no encontrados en CallTracker | Versión desactualizada | Reinstalar desde `client/call_tracking.py` |

---

## Próximos Pasos (Opcionales)

### 1. **Agregar Persistencia Local**
```python
# Guardar sesiones locales si servidor falla
call_tracker.session_history  # Ya mantiene lista de CallSession
```

### 2. **Reportes por Email**
```python
# Enviar reporte diario de métricas
import smtplib
# ... código para enviar email con totales del día
```

### 3. **Alertas en Tiempo Real**
```python
# Si una llamada dura > 30 minutos, alerta
if duration > 1800:
    send_notification("⚠️ Llamada larga detectada")
```

### 4. **Integración con Google Sheets**
```python
# Exportar CallLog a sheet automáticamente
from gsheets import authorize
# ... código para escribir en sheet
```

---

## Recursos Útiles

**Documentación completa:**
- `SISTEMA_RASTREO_TIEMPO_COMPLETO.md` - Arquitectura detallada
- `SISTEMA_PROVEEDORES_LLAMADAS.md` - Sistema de múltiples proveedores

**Código relevante:**
- `server.py` líneas 169-209 (Modelo CallLog)
- `server.py` líneas 1329-1500 (Endpoints rastreo)
- `client/call_tracking.py` (Cliente rastreo)
- `client/ui/metrics_dashboard.py` (Dashboard UI)

---

## Resumen

**En 15 minutos, el sistema está listo para:**

1. ⏱️ Rastrear automáticamente cada llamada
2. 📊 Mostrar métricas en tiempo real
3. 📈 Mantener historial completo
4. 💾 Almacenar en base de datos segura

**Sin cambios complicados en tu código existente.**

¡Listo para usar! 🎉
