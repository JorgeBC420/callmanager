# 📊 Sistema de Métricas - CallManager v2.0

## Descripción General

El nuevo sistema de métricas proporciona dashboards interactivos según el rol del usuario, permitiendo visualizar:

- **Métricas Personales** (Agente): Llamadas, ventas, instalaciones, tasa de éxito
- **Métricas de Equipo** (Supervisor/TeamLead): Desempeño del equipo + comparativa con otros equipos
- **Dashboard Ejecutivo** (Jefe de Proyecto): Vista consolidada de todas las operaciones

---

## Estructura de Módulos

### 1. `metrics_dashboard.py`
Componentes visuales reutilizables:
- `SimpleChart` - Gráficos de barras
- `MetricCard` - Tarjetas de métricas
- `AgentMetricsDashboard` - Dashboard para agentes
- `SupervisorMetricsDashboard` - Dashboard para supervisores
- `ProjectManagerDashboard` - Dashboard para jefes de proyecto
- `get_dashboard_for_role()` - Factory function

### 2. `auth_context.py`
Gestión de información del usuario actual:
- `CurrentUser` - Clase para representar el usuario
- `current_user` - Variable global del usuario actual
- `set_current_user()` - Función para actualizar el usuario tras autenticación

### 3. `call_manager_app.py`
Integración en la aplicación principal:
- Botón "📊 Métricas" en el header
- Método `show_metrics()` que abre el dashboard

---

## Cómo Usar

### Mostrar el Dashboard

```python
# Se muestra automáticamente al hacer click en el botón "📊 Métricas"
# del header de la aplicación principal
```

### Actualizar el Rol del Usuario

```python
from auth_context import set_current_user

# Después de una autenticación exitosa
set_current_user(
    username="juan_perez",
    role="supervisor",  # agent, supervisor, teamlead, projectmanager, ti
    team_id="team_1",
    team_name="Equipo Ventas"
)
```

### Verificar Permisos

```python
from auth_context import current_user

if current_user.can_view_all_metrics():
    # Mostrar dashboard completo
    pass

if current_user.is_supervisor():
    # Mostrar opciones de supervisor
    pass
```

---

## Roles y Acceso

| Rol | Dashboard | Acceso |
|-----|-----------|--------|
| **Agent** | Personales | Solo sus métricas |
| **Supervisor** | Equipo | Su equipo + totales de otros |
| **TeamLead** | Ejecutivo | Todos los equipos |
| **ProjectManager** | Ejecutivo | Todos los equipos |
| **TI** | Ejecutivo | Todos los equipos + configuración |

---

## API Endpoints Utilizados

### `/metrics/personal`
Retorna métricas personales del usuario:
```json
{
  "username": "juan",
  "calls_made": 150,
  "calls_success": 130,
  "calls_failed": 20,
  "success_rate": 86.67,
  "contacts_managed": 45
}
```

### `/metrics/team`
Retorna métricas del equipo (acceso según rol):
```json
[
  {
    "username": "agente1",
    "calls_made": 100,
    "calls_success": 90,
    "success_rate": 90.0
  },
  ...
]
```

### `/metrics/all`
Retorna métricas consolidadas de la organización (solo PM/TI):
```json
{
  "total_calls": 5000,
  "total_success": 4200,
  "total_contacts": 1500,
  "by_team": {
    "Equipo 1": {
      "calls_made": 2800,
      "calls_success": 2400,
      "agents": 5
    }
  }
}
```

---

## Features Implementados

✅ **Dashboard de Agente**
- Métricas personales (4x2 tarjetas)
- Gráfico de estado de llamadas
- Gráfico de llamadas por día
- Botón para actualizar

✅ **Dashboard de Supervisor**
- Métricas consolidadas del equipo
- Tabla de desempeño de agentes
- Pestaña para ver totales del otro equipo
- Botón para actualizar

✅ **Dashboard de Jefe de Proyecto**
- Métricas consolidadas de toda la organización
- Comparativa de equipos
- Gráficos de ventas por equipo
- Resumen general

✅ **Actualizaciones en Tiempo Real**
- Cada dashboard incluye botón "🔄 Actualizar"
- Carga datos desde el servidor en background (threading)
- No bloquea la interfaz de usuario

---

## Futuras Mejoras

- [ ] Sincronización automática cada 30 segundos
- [ ] Exportar reportes en PDF
- [ ] Histórico de métricas (últimos 30 días)
- [ ] Alertas de bajo desempeño
- [ ] Filtros por rango de fechas
- [ ] Integración con estadísticas de llamadas
- [ ] Metas y objetivos
- [ ] Comparativa de desempeño individual vs equipo

---

## Troubleshooting

**Problema: Las métricas no cargan**
1. Verificar que el servidor está corriendo (`python server.py`)
2. Verificar que la API Key es correcta
3. Verificar que el endpoint está disponible (`/metrics/personal`)

**Problema: El dashboard se ve en blanco**
1. Verificar conexión a internet/servidor local
2. Revisar logs del servidor para errores
3. Probar con datos de ejemplo (modo demo)

**Problema: Rol incorrecta en el dashboard**
1. Actualizar el rol con `set_current_user()` tras autenticación
2. Verificar que el usuario tiene los permisos necesarios en el servidor
