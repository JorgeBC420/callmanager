# 👥 Sistema de Roles y Autorización - CallManager

**Versión:** 3.3  
**Fecha:** Noviembre 18, 2025  
**Estado:** Implementado

---

## 📋 Descripción General

CallManager implementa un sistema de roles y permisos basado en API Keys con 4 niveles de acceso:

1. **Agent** - Agentes de llamadas
2. **TeamLead** - Líderes de equipo
3. **ProjectManager** - Jefes de proyecto
4. **TI** - Administradores técnicos

---

## 🔐 Roles y Permisos

### Agent
**Descripción:** Agentes de call center que hacen llamadas y gestionan contactos

**Permisos:**
```
✅ GET /metrics/personal          - Ver métricas personales
✅ GET /contacts                  - Ver contactos asignados
✅ POST /import                   - Importar contactos
✅ Socket.IO: update_contact      - Actualizar contactos
✅ Socket.IO: lock_contact        - Bloquear contactos
✅ Socket.IO: unlock_contact      - Desbloquear contactos
❌ GET /metrics/team              - NO puede ver equipo
❌ GET /metrics/all               - NO puede ver todas las métricas
❌ GET /config                    - NO puede accesar configuración
```

---

### TeamLead
**Descripción:** Líderes de equipos que supervisan equipos específicos

**Permisos:**
```
✅ GET /metrics/personal          - Ver métricas personales
✅ GET /metrics/team              - Ver métricas DE SU EQUIPO
✅ GET /metrics/team              - + totales de otros equipos
✅ GET /contacts                  - Ver contactos de su equipo
✅ POST /import                   - Importar contactos
✅ Socket.IO: update_contact      - Actualizar contactos
❌ GET /metrics/all               - NO puede ver detalles individuales de otros
❌ GET /config                    - NO puede accesar configuración
```

**Comportamiento especial:**
- `/metrics/team` devuelve solo usuarios del mismo `team_id`
- Puede ver agregados de otros equipos (totales) pero no detalles individuales

---

### ProjectManager
**Descripción:** Jefes de proyecto con visibilidad total

**Permisos:**
```
✅ GET /metrics/personal          - Ver métricas personales
✅ GET /metrics/team              - Ver TODOS los usuarios
✅ GET /metrics/all               - Ver métricas consolidadas
✅ GET /config                    - Accesar configuración (lectura)
✅ GET /contacts                  - Ver todos los contactos
✅ POST /import                   - Importar contactos
✅ Socket.IO: update_contact      - Actualizar contactos
❌ POST /config                   - NO puede modificar configuración
```

**Casos de uso:**
- Ver dashboard ejecutivo con todas las métricas
- Monitorear performance de todos los equipos
- Generar reportes consolidados
- Ver histórico de cambios

---

### TI
**Descripción:** Administradores técnicos con acceso total

**Permisos:**
```
✅ GET /metrics/personal          - Ver métricas personales
✅ GET /metrics/team              - Ver TODOS los usuarios
✅ GET /metrics/all               - Ver métricas consolidadas
✅ GET /config                    - Accesar configuración (lectura)
✅ POST /config                   - MODIFICAR configuración (escritura)
✅ POST /create_user              - Crear nuevos usuarios
✅ POST /delete_user              - Eliminar usuarios
✅ GET /logs                      - Ver logs del sistema
✅ POST /backup                   - Crear backups manuales
✅ GET /health                    - Health check avanzado
```

**Casos de uso:**
- Gestionar usuarios del sistema
- Modificar configuraciones
- Realizar backups manuales
- Monitorear salud del sistema
- Cambiar niveles de log

---

## 📊 Tabla de Comparación

| Endpoint | Agent | TeamLead | ProjectManager | TI |
|----------|-------|----------|---------------|----|
| `/metrics/personal` | ✅ | ✅ | ✅ | ✅ |
| `/metrics/team` | ❌ | ✅ | ✅ | ✅ |
| `/metrics/all` | ❌ | ❌ | ✅ | ✅ |
| `/config` (GET) | ❌ | ❌ | ✅ | ✅ |
| `/config` (POST) | ❌ | ❌ | ❌ | ✅ |
| `/contacts` | ✅ | ✅ | ✅ | ✅ |
| `/import` (POST) | ✅ | ✅ | ✅ | ✅ |
| Socket.IO events | ✅ | ✅ | ✅ | ✅ |
| `/logs` | ❌ | ❌ | ❌ | ✅ |
| `/backup` (POST) | ❌ | ❌ | ❌ | ✅ |
| `/users` (CRUD) | ❌ | ❌ | ❌ | ✅ |

---

## 🔑 Autenticación

### Headers Requeridos

Todos los endpoints requieren:
```
X-API-Key: <api_key_del_usuario>
```

### Ejemplo con cURL

```bash
# Obtener métricas personales
curl -H "X-API-Key: agent1-key-abc123" \
  http://127.0.0.1:5000/metrics/personal

# Obtener métricas de equipo (TeamLead)
curl -H "X-API-Key: teamlead-sales-def456" \
  http://127.0.0.1:5000/metrics/team

# Obtener configuración (TI)
curl -H "X-API-Key: ti-key-ghi789" \
  http://127.0.0.1:5000/config

# Modificar configuración (TI - Solo TI)
curl -X POST -H "X-API-Key: ti-key-ghi789" \
  -H "Content-Type: application/json" \
  -d '{"log_level": "DEBUG"}' \
  http://127.0.0.1:5000/config
```

### Ejemplo con Python

```python
import requests

headers = {"X-API-Key": "mi-api-key-123"}

# GET
response = requests.get("http://127.0.0.1:5000/metrics/personal", headers=headers)
print(response.json())

# POST
response = requests.post(
    "http://127.0.0.1:5000/config",
    headers=headers,
    json={"log_level": "DEBUG"}
)
```

---

## 🗂️ Estructura de Datos

### Modelo User

```python
class User:
    id: str              # ID único (ej: "u_agent1")
    api_key: str         # Clave de API única
    username: str        # Nombre de usuario
    role: str            # Agent, TeamLead, ProjectManager, TI
    team_id: str         # ID del equipo (ej: "team-sales")
    team_name: str       # Nombre del equipo (ej: "Equipo Ventas")
    email: str           # Email del usuario
    is_active: int       # 1 = activo, 0 = inactivo
    last_login: DateTime # Último acceso
    created_at: DateTime # Fecha de creación
```

### Modelo UserMetrics

```python
class UserMetrics:
    id: str              # ID único
    user_id: str         # Referencia a User
    calls_made: int      # Total de llamadas
    calls_success: int   # Llamadas exitosas
    calls_failed: int    # Llamadas fallidas
    contacts_managed: int # Contactos gestionados
    avg_call_duration: int # Duración promedio (segundos)
    last_updated: DateTime # Última actualización
```

---

## 🚀 Implementación

### 1. Decorador @require_role

```python
@require_role('ProjectManager', 'TI')
def get_all_metrics(current_user):
    """
    Solo ProjectManager y TI pueden acceder
    current_user se inyecta automáticamente
    """
    return jsonify({
        'total_calls': ...,
        'total_users': ...
    })
```

### 2. Obtener Usuario Actual

```python
from server import require_role, get_user_from_api_key

api_key = request.headers.get('X-API-Key')
user = get_user_from_api_key(api_key)

if user.role == 'TeamLead':
    # Lógica específica para TeamLead
    pass
```

---

## 🧪 Testing

### Inicializar Usuarios de Prueba

```bash
python init_users.py
```

Esto crea 7 usuarios:
- 3 Agents (Ventas, Ventas, Soporte)
- 2 TeamLeads (Ventas, Soporte)
- 1 ProjectManager
- 1 TI

### Ejecutar Pruebas de Autorización

```bash
python test_roles.py
```

Output esperado:
```
✅ [200] GET  /metrics/personal          → Agent
❌ [403] GET  /metrics/team              → Agent (forbidden)
✅ [200] GET  /metrics/team              → TeamLead
✅ [200] GET  /metrics/all               → ProjectManager
✅ [200] GET  /config                    → TI
❌ [403] POST /config                    → ProjectManager (forbidden)
```

---

## 💾 Base de Datos

### Tablas

```sql
CREATE TABLE users (
    id TEXT PRIMARY KEY,
    api_key TEXT UNIQUE,
    username TEXT UNIQUE,
    role TEXT,        -- Agent, TeamLead, ProjectManager, TI
    team_id TEXT,
    team_name TEXT,
    email TEXT,
    is_active INTEGER,
    last_login DATETIME,
    created_at DATETIME,
    updated_at DATETIME
);

CREATE TABLE user_metrics (
    id TEXT PRIMARY KEY,
    user_id TEXT,
    calls_made INTEGER,
    calls_success INTEGER,
    calls_failed INTEGER,
    contacts_managed INTEGER,
    avg_call_duration INTEGER,
    last_updated DATETIME
);
```

### Índices

```sql
CREATE INDEX idx_users_api_key ON users(api_key);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_team ON users(team_id);
CREATE INDEX idx_users_active ON users(is_active);
CREATE INDEX idx_metrics_user ON user_metrics(user_id);
```

---

## 🔒 Seguridad

### Prácticas Implementadas

1. **API Keys Únicas:** Cada usuario tiene una API key única
2. **Validación de Rol:** Cada endpoint valida el rol del usuario
3. **Logging de Acceso:** Se registran todos los intentos de acceso
4. **Inactive Check:** Solo usuarios con `is_active=1` pueden acceder
5. **Rate Limiting:** Protección contra brute force (Flask-Limiter)

### Generación Segura de API Keys

```python
import secrets

# Generar API key segura
api_key = secrets.token_urlsafe(32)
print(api_key)  # Ej: "K8x_Q9mP2L5vN7rT1sH3dF6gJ4bC8zW0yX"
```

---

## 📈 Casos de Uso

### Agent - Inicio de Sesión
```bash
# Agent se loguea y ve sus métricas personales
curl -H "X-API-Key: agent1-key-abc123" \
  http://127.0.0.1:5000/metrics/personal

# Respuesta:
{
  "user_id": "u_agent1",
  "username": "agent1",
  "role": "Agent",
  "calls_made": 15,
  "calls_success": 12,
  "success_rate": 80.0
}
```

### TeamLead - Supervisa Su Equipo
```bash
# TeamLead ve métricas de su equipo (Ventas)
curl -H "X-API-Key: teamlead-sales-def456" \
  http://127.0.0.1:5000/metrics/team

# Respuesta: Array con todos los agentes de Ventas
[
  {"username": "agent1", "calls_made": 15, "success_rate": 80},
  {"username": "agent2", "calls_made": 20, "success_rate": 85}
]
```

### ProjectManager - Dashboard Ejecutivo
```bash
# PM ve todas las métricas consolidadas
curl -H "X-API-Key: pm-key-ghi789" \
  http://127.0.0.1:5000/metrics/all

# Respuesta:
{
  "total_calls": 450,
  "total_success": 380,
  "total_users": 10,
  "overall_success_rate": 84.4,
  "by_team": {
    "Equipo Ventas": {"calls_made": 280, "agents": 5},
    "Equipo Soporte": {"calls_made": 170, "agents": 3}
  }
}
```

### TI - Acceso Administrativo
```bash
# TI accede y modifica configuración
curl -X POST -H "X-API-Key: ti-key-xyz123" \
  -H "Content-Type: application/json" \
  -d '{"log_level": "DEBUG", "rate_limit": 2000}' \
  http://127.0.0.1:5000/config
```

---

## 🔄 Flujo de Autenticación

```
1. Cliente envía request con header X-API-Key
                    ↓
2. @require_role valida que API key existe
                    ↓
3. Se busca User en BD con api_key
                    ↓
4. Verificar que is_active = 1
                    ↓
5. Validar que user.role está en allowed_roles
                    ↓
6. Inyectar current_user a la función
                    ↓
7. Ejecutar función con permisos validados
                    ↓
8. Loguear acceso (éxito o fallo)
```

---

## ⚡ Próximos Pasos

### Phase 3.4 - Interface Gráfica con Roles

Actualizar `call_manager_app.py` para mostrar diferentes menús según el rol:

```python
# En call_manager_app.py
if user.role == 'Agent':
    # Mostrar solo: Llamar, Importar, Contactos personales
    
elif user.role == 'TeamLead':
    # Mostrar: Dashboard del equipo, Métricas, Contactos
    
elif user.role == 'ProjectManager':
    # Mostrar: Dashboard ejecutivo, Todas las métricas
    
elif user.role == 'TI':
    # Mostrar: Configuración, Usuarios, Logs, Backups
```

### Phase 3.5 - Logging Auditado

Implementar audit trail completo:
```python
# Loguear TODOS los cambios de datos sensibles
# - Quién cambió qué y cuándo
# - Intentos fallidos de acceso
# - Cambios de configuración
```

---

## 📞 Soporte

Para agregar nuevos usuarios:
```python
from server import Session, User
import secrets

db = Session()
new_user = User(
    id=f"u_newuser",
    api_key=secrets.token_urlsafe(32),
    username="newuser",
    role="Agent",
    team_id="team-sales",
    team_name="Equipo Ventas",
    email="user@example.com"
)
db.add(new_user)
db.commit()
```

---

**Versión:** 3.3  
**Última actualización:** Noviembre 18, 2025  
**Status:** ✅ Producción Ready
