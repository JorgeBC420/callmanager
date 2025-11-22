# 🚀 GUÍA RÁPIDA DE INICIO - CallManager v3.3.1
**Estado Actual:** ✅ TOTALMENTE FUNCIONAL Y AUDITADO

---

## 📋 Checklist Rápido

- ✅ Seguridad: Sistema de roles + autenticación implementado
- ✅ CRUD: Funcionalidad completa (C, R, U, D)
- ✅ Bugs: Todos los errores críticos corregidos
- ✅ Demos: Scripts listos para ejecutar
- ✅ Tests: Suite de pruebas de roles disponible

---

## 🎯 INICIANDO EN 3 PASOS

### Paso 1: Inicializar Servidor + Datos Demo

```powershell
# Terminal 1 - En la carpeta callmanager
cd c:/Users/bjorg/OneDrive/Desktop/callmanager

# Opción A: Ejecutar demo simple (recomendado)
python run_demo.py

# Opción B: Ejecutar servidor sin demo
python start_server.py
```

**Esperado:** Verás `Socket.IO: EventletAsync` y `Running on http://0.0.0.0:5000`

---

### Paso 2: Iniciar Cliente GUI (en otra Terminal)

```powershell
# Terminal 2
cd c:/Users/bjorg/OneDrive/Desktop/callmanager/client
python call_manager_app.py
```

**Esperado:** 
- Abre ventana GUI CustomTkinter
- Muestra "Cargando contactos..."
- Se conecta al servidor automáticamente

---

### Paso 3: Importar Contactos de Prueba

1. Haz clic en **📥 Importar Excel**
2. Selecciona: `../demo_contacts.csv`
3. Se importan 15 contactos de prueba
4. Verifica en la lista que aparecen todos

---

## 🧪 TESTING CON ROLES

### Crear Usuarios de Prueba

```powershell
# Terminal 3
cd c:/Users/bjorg/OneDrive/Desktop/callmanager
python init_users.py
```

**Output esperado:**
```
✅ Agent: agent1-key-XXXXXXXX
✅ TeamLead: teamlead-sales-XXXXXXXX
✅ ProjectManager: pm-key-XXXXXXXX
✅ TI: ti-key-XXXXXXXX
```

### Ejecutar Tests de Autorización

```powershell
# Terminal 4 (con servidor activo)
python test_roles.py
```

**Verifica:**
- ✅ Agents ven métricas personales
- ❌ Agents NO ven métricas de equipo
- ✅ TeamLeads ven su equipo
- ✅ ProjectManager ve todo
- ✅ TI tiene acceso total

---

## 🔐 CREDENCIALES DEFAULT

### Para Testing Rápido:
```
API Key (Demo): dev-key-change-in-production
URL: http://127.0.0.1:5000
```

### Para Testing con Roles:
Usar las keys generadas por `init_users.py`

---

## 📊 FEATURES PROBADOS

### Agent (Agente/Asesor)
- ✅ VER contactos
- ✅ ACTUALIZAR contactos
- ✅ BLOQUEAR contactos
- ✅ Ver métricas personales
- ✅ Importar contactos

### TeamLead (Supervisor)
- ✅ Todo lo del Agent
- ✅ Ver métricas de su equipo
- ✅ Ver métricas consolidadas

### ProjectManager (Jefe Proyecto)
- ✅ Ver todas las métricas
- ✅ Ver toda la configuración
- ✅ Gestionar todos los contactos
- ❌ Modificar configuración (solo TI)

### TI (Jefe TI)
- ✅ Acceso TOTAL
- ✅ Crear/eliminar usuarios
- ✅ Modificar configuración
- ✅ Ver logs
- ✅ Hacer backups

---

## 🐛 PROBLEMAS CONOCIDOS Y SOLUCIONES

### Problema: "No se pudo conectar al servidor"
**Solución:**
- Asegúrate de que `python run_demo.py` está corriendo en Terminal 1
- Verifica que el puerto 5000 NO está bloqueado por firewall

### Problema: "pywinauto not available"
**Solución:**
- `pip install pywinauto`
- Necesario solo para integración InterPhone

### Problema: "CustomTkinter import error"
**Solución:**
- `pip install customtkinter`
- Instalar todas las dependencias: `pip install -r requirements.txt`

### Problema: "API key inválida"
**Solución:**
- Asegúrate de ejecutar `init_users.py` primero
- Reemplaza las API keys de prueba en `test_roles.py` con las nuevas

---

## 🔄 FLUJO COMPLETO RECOMENDADO

```
1. [Terminal 1] python run_demo.py
   ↓
2. [Terminal 2] cd client && python call_manager_app.py
   ↓
3. [GUI] Haz clic en "📥 Importar Excel" → demo_contacts.csv
   ↓
4. [GUI] Verifica que hay 15 contactos en la lista
   ↓
5. [GUI] Haz clic en "🔄 Refrescar" → debería recargar sin errores
   ↓
6. [GUI] Haz clic en "📞 Llamar" en un contacto
   ↓
7. [GUI] Verifica que muestra error de InterPhone si no está instalado
   ↓
8. [GUI] Haz clic en "🔒 Bloquear" → debe cambiar a "🔓 Desbloquear"
   ↓
9. [Terminal 3] python init_users.py
   ↓
10. [Terminal 4] python test_roles.py
    ↓
11. Verifica output de tests (deberías ver ✅ y ❌ apropiados)
```

---

## 🛠️ MANTENIMIENTO

### Limpiar Todo y Reiniciar

```powershell
# Borrar base de datos
Remove-Item contacts.db -ErrorAction SilentlyContinue
Remove-Item callmanager.log -ErrorAction SilentlyContinue

# Reiniciar
python run_demo.py
```

### Ver Logs del Servidor

```powershell
# En tiempo real
Get-Content callmanager.log -Tail 50 -Wait
```

### Hacer Backup Manual

```powershell
# Usar endpoint de TI
curl -X POST http://127.0.0.1:5000/backup `
  -H "X-API-Key: ti-key-XXXXXXXX"
```

---

## 📞 INTEGRACIÓN INTERPHONE (Opcional)

Si tienes InterPhone instalado:

1. Abre InterPhone
2. En la GUI de CallManager, haz clic en **📞 Llamar**
3. Debería marcar automáticamente el número

---

## 🚀 DESPLEGAR A PRODUCCIÓN

### 1. Cambiar Credenciales
```python
# config.py
SECRET_KEY = "tu-secret-key-aleatorio-muy-largo-aqui"
CALLMANAGER_API_KEY = "production-api-key-secreto"
```

### 2. Usar Gunicorn + HTTPS
```powershell
pip install gunicorn
gunicorn --certfile=cert.pem --keyfile=key.pem \
  --bind 0.0.0.0:443 server:app
```

### 3. Configurar CORS
```python
# server.py
SOCKETIO_CORS_ORIGINS = "https://tudominio.com"
```

### 4. Activar WAL Mode para SQLite (ya está por defecto)
```python
# server.py ya tiene:
# PRAGMA journal_mode=WAL
# PRAGMA synchronous=NORMAL
```

---

## 📈 ARQUITECTURA

```
┌─────────────────────────────────────────────────────────┐
│                    CLIENT (CustomTkinter)               │
│                   call_manager_app.py                   │
│  ┌──────────────────────────────────────────────────┐   │
│  │ • Ver contactos                                  │   │
│  │ • Importar Excel/CSV                             │   │
│  │ • Bloquear/Desbloquear contactos                 │   │
│  │ • Integración InterPhone                         │   │
│  │ • Real-time via Socket.IO                        │   │
│  └──────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────┘
                         │ Socket.IO + REST
                         ▼
┌─────────────────────────────────────────────────────────┐
│                     SERVER (Flask)                      │
│                      server.py                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │ REST Endpoints:                                  │   │
│  │ • GET  /contacts          - Leer todos          │   │
│  │ • POST /import            - Importar lote       │   │
│  │ • DEL  /contacts/{id}     - Eliminar (PM/TI)    │   │
│  │ • GET  /metrics/*         - Métricas por rol    │   │
│  │ • GET  /config            - Configuración       │   │
│  │                                                  │   │
│  │ Socket.IO Events:                                │   │
│  │ • update_contact          - Actualizar          │   │
│  │ • lock_contact            - Bloquear            │   │
│  │ • unlock_contact          - Desbloquear         │   │
│  │ • contact_locked (emit)   - Notificar bloqueo   │   │
│  │ • contact_unlocked (emit) - Notificar desbloqueo│   │
│  │ • contact_updated (emit)  - Notificar cambios   │   │
│  │ • contact_deleted (emit)  - Notificar eliminación
│  │                                                  │   │
│  │ Autenticación:                                   │   │
│  │ • Decorador @require_auth - Validar API key     │   │
│  │ • Decorador @require_role - Validar rol         │   │
│  │ • Tabla users + UserMetrics                     │   │
│  └──────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────┘
                         │ SQL queries
                         ▼
┌─────────────────────────────────────────────────────────┐
│                   DATABASE (SQLite)                     │
│                    contacts.db                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │ Tables:                                          │   │
│  │ • contact         - Contactos                    │   │
│  │ • users           - Usuarios (roles)             │   │
│  │ • user_metrics    - Métricas por usuario         │   │
│  │                                                  │   │
│  │ Features:                                        │   │
│  │ • WAL Mode (lectura concurrente)                 │   │
│  │ • Índices en campos clave (api_key, role, etc)  │   │
│  │ • Backups automáticos cada 30 min                │   │
│  │ • Limpieza de locks vencidos cada 5 min          │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

---

## 📞 SOPORTE Y DEBUGGING

### Logs más detallados
```python
# config.py
LOG_LEVEL = 'DEBUG'  # cambiar a DEBUG
```

### Ver estado del servidor
```powershell
curl http://127.0.0.1:5000/health
```

### Ver configuración
```powershell
curl -H "X-API-Key: dev-key-change-in-production" \
  http://127.0.0.1:5000/config
```

---

**Versión:** 3.3.1  
**Última Actualización:** 21 de Noviembre, 2025  
**Estado:** ✅ PRODUCCIÓN READY (con mejoras de seguridad)
