# 🚀 Guía de Prueba - Sistema de Métricas

## Requisitos Previos

```bash
# 1. Asegurate de que el servidor está corriendo
python server.py

# 2. En otra terminal, ejecuta la aplicación cliente
python client/call_manager_app.py
```

---

## Paso 1: Verificar que el Servidor Tiene Datos de Prueba

El servidor debe tener usuarios con métricas. Si no tienes datos, ejecuta:

```bash
python init_users.py
python demo_roles.py
```

Esto creará usuarios de ejemplo con roles y métricas:
- `agent1` (Agent)
- `supervisor1` (TeamLead)
- `pm1` (ProjectManager)

---

## Paso 2: Abrir la Aplicación CallManager

```bash
python client/call_manager_app.py
```

Verás la ventana principal con varios botones en el header.

---

## Paso 3: Hacer Click en "📊 Métricas"

En la barra de herramientas superior, busca el botón **"📊 Métricas"** (de color verde).

Al hacer click, se abrirá una nueva ventana con el dashboard según el rol actual (por defecto: Agent).

---

## Paso 4: Explorar los Dashboards

### Dashboard de Agente (Rol: agent)
**Muestra:**
- Total de llamadas realizadas
- Llamadas exitosas/fallidas
- Tasa de éxito en %
- Gráfico de estado de llamadas (pie chart)
- Gráfico de llamadas por día (últimos 7 días)

**Botones:**
- 🔄 Actualizar - Recarga datos del servidor

---

### Dashboard de Supervisor (Rol: supervisor)
**Pestaña "Mi Equipo":**
- Métricas consolidadas del equipo
- Tabla con desempeño de cada agente
  - Nombre
  - Total de llamadas
  - Llamadas exitosas
  - Tasa de éxito

**Pestaña "Otro Equipo":**
- Resumen de totales del otro equipo

---

### Dashboard de Jefe de Proyecto (Rol: projectmanager)
**Pestaña "Resumen General":**
- Métricas consolidadas de toda la organización
- Gráfico comparativo de equipos (llamadas)
- Gráfico de ventas por equipo

**Información:**
- Total de llamadas globales
- Total de ventas
- Total de instalaciones
- Cantidad de equipos activos

---

## Paso 5: Cambiar de Rol (Opcional)

Para probar los diferentes dashboards, edita `client/call_manager_app.py`:

```python
def show_metrics(self):
    # Cambiar esta línea:
    role = "agent"  # Puede ser: agent, supervisor, projectmanager, teamlead
```

Opciones disponibles:
- `"agent"` - Métricas personales
- `"supervisor"` - Métricas de equipo
- `"projectmanager"` - Dashboard ejecutivo
- `"teamlead"` - Dashboard ejecutivo (igual a projectmanager)

---

## Paso 6: Actualizar Datos

Cada dashboard tiene un botón **"🔄 Actualizar"** que recarga los datos del servidor sin cerrar la ventana.

Si los datos cambian en otra ventana/usuario, haz click en este botón para refrescar.

---

## Datos de Ejemplo

Si ejecutaste `demo_roles.py`, tienes estos usuarios:

### Agent1
```
Llamadas: 150
Exitosas: 130
Tasa de éxito: 86.7%
```

### Agent2
```
Llamadas: 120
Exitosas: 110
Tasa de éxito: 91.7%
```

### Supervisor (ve todos los agentes)
```
Total del equipo: 270 llamadas
Promedio por agente: 135 llamadas
```

---

## Troubleshooting

### Dashboard vacío / Sin datos
**Causas:**
- [ ] Servidor no está corriendo (`python server.py`)
- [ ] No hay datos en la base de datos
- [ ] API Key incorrecta

**Solución:**
```bash
# Resetear base de datos y crear datos de ejemplo
python init_users.py
python demo_roles.py
```

### Error de conexión
**Causas:**
- [ ] Servidor no está en `http://localhost:5000`
- [ ] Puerto 5000 ocupado por otra aplicación
- [ ] Firewall bloqueando conexión

**Solución:**
```bash
# Verifica que el servidor está corriendo
python server.py

# Si falla, usa otro puerto
export FLASK_PORT=5001
python server.py
```

### Los botones no responden
**Solución:**
- Espera a que carguen los datos (ver en terminal los logs)
- Haz click en "🔄 Actualizar"
- Cierra y reabre la ventana de métricas

---

## Métricas Esperadas por Rol

| Rol | Ve | No Ve |
|-----|----|----|
| **Agent** | Sus propias métricas | Otros agentes |
| **Supervisor** | Su equipo + totales otros | Detalles otros equipos |
| **ProjectManager** | Todo | Configuración del sistema |
| **TI** | Todo incluyendo logs | - |

---

## Siguientes Pasos

Una vez que verifiques que el sistema funciona:

1. **Integrar Autenticación Real**
   - Conectar con login del usuario
   - Actualizar rol después de autenticación

2. **Agregar Más Métricas**
   - Tiempo en llamadas
   - Instalaciones completadas
   - Metas vs realidad

3. **Histórico**
   - Guardar métricas diarias
   - Mostrar tendencias (últimas 30 días)

4. **Alertas**
   - Notificar si tasa de éxito baja de 80%
   - Alertar si no hay llamadas en 1 hora

---

## Contacto

Si tienes problemas, revisa:
- Logs del servidor: `server.py` output
- Logs de la aplicación: Console output de `call_manager_app.py`
- Documentación: `docs/METRICAS_Y_DASHBOARDS.md`
