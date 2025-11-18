# 📊 Arquitectura de CallManager - Fase 3.3 Final

**Estado:** Implementado y en GitHub  
**Versión:** 3.3 Complete  
**Último Commit:** `358017a`

---

## 🏗️ Arquitectura General

```
┌─────────────────────────────────────────────────────────────────┐
│                     CallManager v3.3                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────┐         ┌──────────────────────────────┐  │
│  │   Clientes       │         │   Servidor Flask + SocketIO  │  │
│  ├──────────────────┤         ├──────────────────────────────┤  │
│  │ call_manager_app │◄───────►│ HTTP: :5000                  │  │
│  │ (CustomTkinter)  │ Socket  │ CORS: * (Configurable)       │  │
│  └──────────────────┘ .IO     └──────────────────────────────┘  │
│                                            │                    │
│  ┌──────────────────┐                      ▼                    │
│  │ InterPhone Auto  │                  ┌─────────────────────┐  │
│  │ (pywinauto)      │                  │  Autenticación      │  │
│  └──────────────────┘                  ├─────────────────────┤  │
│         │                              │ API Key en Header   │  │
│         │                              │ Flask-Limiter       │  │
│         ▼                              │ @require_role       │  │
│  ┌──────────────────┐                  └─────────────────────┘  │
│  │ InterPhone       │                                            │
│  │ (External)       │                  ┌─────────────────────┐  │
│  └──────────────────┘                  │  Roles              │  │
│                                        ├─────────────────────┤  │
│                                        │ • Agent             │  │
│                                        │ • TeamLead          │  │
│                                        │ • ProjectManager    │  │
│                                        │ • TI                │  │
│                                        └─────────────────────┘  │
│                                                 │                │
│                                                 ▼                │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Endpoints Segregados por Rol                          │    │
│  ├─────────────────────────────────────────────────────────┤    │
│  │ /metrics/personal  (todos)                              │    │
│  │ /metrics/team      (TeamLead+)                          │    │
│  │ /metrics/all       (PM/TI)                              │    │
│  │ /config            (PM/TI, POST solo TI)               │    │
│  │ /contacts          (todos)                              │    │
│  │ /import            (POST, todos)                        │    │
│  │ Socket.IO events   (todos)                              │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                 │                │
│                                                 ▼                │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  SQLite + SQLAlchemy ORM (WAL Mode)                    │    │
│  ├─────────────────────────────────────────────────────────┤    │
│  │ • contacts (15+ campos + version para optimistic lock) │    │
│  │ • users (rol, team, api_key)                           │    │
│  │ • user_metrics (llamadas, contactos gestionados)       │    │
│  │ • Backups automáticos cada 30 min                      │    │
│  │ • Índices para búsquedas rápidas                       │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔐 Flujo de Autorización

```
┌─────────────────────┐
│ Cliente envia       │
│ X-API-Key: xyz     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ @require_role()     │
│ Valida decorador    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────────────┐
│ User existe en BD?              │
│ is_active = 1?                  │
│ api_key válida?                 │
└──────────┬──────────────────────┘
           │
      No   │   Sí
      ▼    └──────────┐
    401               ▼
  Forbidden    ┌──────────────────┐
              │ User.role en      │
              │ allowed_roles?    │
              └──────────┬───────┘
                     No   │   Sí
                    ▼     └──────────┐
                  403               ▼
                Forbidden    ┌──────────────┐
                            │ Inyectar     │
                            │ current_user │
                            └──────┬───────┘
                                  ▼
                            ┌──────────────┐
                            │ Ejecutar     │
                            │ endpoint     │
                            └──────┬───────┘
                                  ▼
                            ┌──────────────┐
                            │ Loguear      │
                            │ acceso (éxito│
                            └──────────────┘
```

---

## 👥 Matriz de Permisos Detallada

### Endpoints por Rol

```
┌────────────────────────┬──────┬─────────┬────┬────┐
│ ENDPOINT               │Agent │TeamLead │ PM │ TI │
├────────────────────────┼──────┼─────────┼────┼────┤
│ GET /metrics/personal  │  ✅  │   ✅    │ ✅ │ ✅ │
│ GET /metrics/team      │  ❌  │   ✅    │ ✅ │ ✅ │
│ GET /metrics/all       │  ❌  │   ❌    │ ✅ │ ✅ │
│ GET /config            │  ❌  │   ❌    │ ✅ │ ✅ │
│ POST /config           │  ❌  │   ❌    │ ❌ │ ✅ │
│ GET /contacts          │  ✅  │   ✅    │ ✅ │ ✅ │
│ POST /import           │  ✅  │   ✅    │ ✅ │ ✅ │
│ Socket.IO events       │  ✅  │   ✅    │ ✅ │ ✅ │
│ GET /logs              │  ❌  │   ❌    │ ❌ │ ✅ │
│ POST /backup           │  ❌  │   ❌    │ ❌ │ ✅ │
│ POST /users (CRUD)     │  ❌  │   ❌    │ ❌ │ ✅ │
└────────────────────────┴──────┴─────────┴────┴────┘
```

---

## 📊 Modelos de BD

### Tabla: users

```
┌──────────────────────┬─────────────┬──────────────┐
│ Columna              │ Tipo        │ Restricción  │
├──────────────────────┼─────────────┼──────────────┤
│ id (PK)              │ String      │ Unique       │
│ api_key              │ String      │ Unique Index │
│ username             │ String      │ Unique Index │
│ role                 │ String      │ Index        │
│ team_id              │ String      │ Index        │
│ team_name            │ String      │              │
│ email                │ String      │              │
│ is_active            │ Integer     │ Index        │
│ last_login           │ DateTime    │              │
│ created_at           │ DateTime    │ Index        │
│ updated_at           │ DateTime    │              │
└──────────────────────┴─────────────┴──────────────┘
```

### Tabla: user_metrics

```
┌──────────────────────┬─────────────┬──────────────┐
│ Columna              │ Tipo        │ Restricción  │
├──────────────────────┼─────────────┼──────────────┤
│ id (PK)              │ String      │ Unique       │
│ user_id              │ String      │ Index (FK)   │
│ calls_made           │ Integer     │ Default 0    │
│ calls_success        │ Integer     │ Default 0    │
│ calls_failed         │ Integer     │ Default 0    │
│ contacts_managed     │ Integer     │ Default 0    │
│ avg_call_duration    │ Integer     │ Default 0    │
│ last_updated         │ DateTime    │ Auto-update  │
└──────────────────────┴─────────────┴──────────────┘
```

### Tabla: contacts (extensiones)

```
Nuevas columnas agregadas:
├── assigned_to_user_id (String, Index)
├── assigned_to_team_id (String, Index)
└── assigned_to_team_name (String)
```

---

## 🧪 Testing

### 1. Inicializar Usuarios
```bash
$ python init_users.py

╔════════════════════════════════════════════════════════╗
║              INICIALIZANDO USUARIOS DE PRUEBA         ║
╠════════════════════════════════════════════════════════╣
║ Agent      | agent1                | agent1-key-abc1  ║
║ Agent      | agent2                | agent2-key-def2  ║
║ Agent      | agent3                | agent3-key-ghi3  ║
║ TeamLead   | teamlead_sales        | teamlead-sl-jk4  ║
║ TeamLead   | teamlead_support      | teamlead-sp-lm5  ║
║ PM         | project_manager       | pm-key-no-pq6    ║
║ TI         | ti_admin              | ti-key-rs-tu7    ║
╚════════════════════════════════════════════════════════╝
```

### 2. Ejecutar Pruebas
```bash
$ python test_roles.py

✅ [200] GET /metrics/personal          (Agent)
❌ [403] GET /metrics/team              (Agent - forbidden)
✅ [200] GET /metrics/team              (TeamLead)
✅ [200] GET /metrics/all               (ProjectManager)
✅ [200] GET /config                    (TI)
❌ [403] POST /config                   (ProjectManager - forbidden)
```

---

## 📈 Casos de Uso Reales

### Caso 1: Agent - Inicia Sesión
```
1. Agent se loguea con API key
2. Accede a /metrics/personal
3. Ve solo sus métricas: 15 llamadas, 80% éxito
4. Puede hacer llamadas y gestionar contactos
5. ❌ No puede ver métricas de otros
```

### Caso 2: TeamLead - Supervisa Equipo
```
1. TeamLead accede con su API key
2. Accede a /metrics/team (filtra por team_id)
3. Ve:
   - Sus propias métricas
   - Métricas de agentes en su equipo
   - Totales de otros equipos (sin detalles)
4. Puede ver contactos asignados a su equipo
5. ❌ No puede modificar config
```

### Caso 3: ProjectManager - Dashboard Ejecutivo
```
1. PM accede con su API key
2. Accede a /metrics/all
3. Ve:
   - Total de llamadas de toda la org: 450
   - Tasa de éxito: 84.4%
   - Desglose por equipo
4. Puede accesar /config (solo lectura)
5. Genera reportes para ejecutivos
```

### Caso 4: TI - Administrador del Sistema
```
1. TI accede con su API key
2. Puede:
   - Ver /metrics/all
   - Accesar /config (lectura)
   - Modificar /config (POST)
   - Crear/eliminar usuarios
   - Ver logs del sistema
   - Realizar backups manuales
3. Monitorea salud del sistema
```

---

## 🚀 Próximas Mejoras Sugeridas

### Phase 3.4 - UI con Roles
Actualizar `call_manager_app.py` para mostrar menúes diferenciados por rol

### Phase 3.5 - Audit Trail
Implementar registro completo de cambios:
- Quién cambió qué
- Cuándo
- Valor anterior vs nuevo

### Phase 3.6 - Reportería
Crear endpoints de reportes:
- `/reports/daily` - Reporte diario
- `/reports/weekly` - Reporte semanal
- `/reports/team-performance` - Performance de equipo

### Phase 3.7 - Notificaciones
Alertas por Socket.IO:
- Cuando un agent no responde (NC)
- Cuando se alcanza límite de rate limit
- Cuando hay cambios en config

---

## 📦 Archivos Modificados/Creados

### Modificados:
- ✏️ `server.py` - +250 líneas (modelos User/UserMetrics, decoradores, endpoints)
- ✏️ `config.py` - Mejoras con python-dotenv
- ✏️ `requirements.txt` - Nuevas dependencias

### Creados:
- ✨ `init_users.py` - Script para crear usuarios de prueba
- ✨ `test_roles.py` - Suite de pruebas de autorización
- ✨ `ROLES_Y_AUTORIZACION.md` - Documentación completa

---

## 📊 Estadísticas de Código

```
Total líneas agregadas: ~500
Total líneas modificadas: ~200
Nuevos endpoints: 6
Nuevos decoradores: 2
Nuevos modelos: 2 (User, UserMetrics)
Scripts de testing: 2
Documentación: 1 archivo (150+ líneas)
```

---

## ✅ Checklist de Completitud

- [x] Modelos User y UserMetrics implementados
- [x] Decorador @require_role implementado
- [x] Endpoints de métricas segregados por rol
- [x] Endpoint /config con POST restringido a TI
- [x] Validación de is_active en login
- [x] Logging de accesos
- [x] Scripts de inicialización de usuarios
- [x] Suite de pruebas de roles
- [x] Documentación completa
- [x] Commit a GitHub
- [x] Validación de sintaxis
- [x] Rate limiting funcional

---

## 📞 Soporte Rápido

### Crear nuevo usuario programáticamente
```python
from server import Session, User, UserMetrics
import secrets

db = Session()
user = User(
    id=f"u_nuevo",
    api_key=secrets.token_urlsafe(32),
    username="nuevo",
    role="Agent",
    team_id="team-sales",
    team_name="Equipo Ventas"
)
db.add(user)

metrics = UserMetrics(id=f"m_u_nuevo", user_id=user.id)
db.add(metrics)
db.commit()
```

### Cambiar rol de usuario
```python
user = db.query(User).filter_by(username="agent1").first()
user.role = "TeamLead"
db.commit()
```

### Desactivar usuario
```python
user = db.query(User).filter_by(username="agent1").first()
user.is_active = 0
db.commit()
```

---

**Versión:** 3.3 Complete  
**Estatus:** ✅ Ready for Production  
**Última actualización:** Noviembre 18, 2025  
**Commit:** `358017a`
