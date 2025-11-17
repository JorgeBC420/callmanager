# Sistema de Estados Dinámicos por Visibilidad

## Descripción General

El sistema de **estados dinámicos** actualiza automáticamente el estado de los contactos basándose en cuánto tiempo han estado inactivos (sin visibilidad en la base de datos).

Esto es especialmente útil para identificar números que:
- **No existen** (hace 3 meses sin actualización)
- **No tienen red** (hace 6 meses sin actualización)
- **No quieren contacto** (hace 8 meses sin actualización)

## Estados Dinámicos

| Estado | Inactividad | Descripción | Ícono |
|--------|-----------|-------------|-------|
| `NO_EXISTE` | 3 meses | Número no existe o no responde desde hace 3 meses | ⏰ |
| `SIN_RED` | 6 meses | Número sin red/servicio desde hace 6 meses | ⚠️ |
| `NO_CONTACTO` | 8 meses | No quieren contacto - sin respuesta desde 8 meses | ❌ |

## Prioridades de Ordenamiento

Al cargar contactos en el cliente, se ordenan automáticamente por prioridad. **Números menores = Mayor visibilidad**:

| Prioridad | Estado | Descripción |
|-----------|--------|-------------|
| 1 | `NC` | **No Contesta** - MÁXIMA PRIORIDAD |
| 2 | `CUELGA` | **Cuelgan** - ALTA PRIORIDAD (depende del vendedor) |
| 3 | `SIN_GESTIONAR` | Sin gestionar - NORMAL |
| 4 | `INTERESADO` | Interesado en servicio - MEDIA |
| 10 | `SERVICIOS_ACTIVOS` | Con servicios - BAJA PRIORIDAD |
| 20 | `NO_EXISTE` | No existe - MUY BAJA |
| 21 | `SIN_RED` | Sin red - MUY BAJA |
| 22 | `NO_CONTACTO` | No quieren contacto - MÍNIMA |

## Cómo Funciona

### 1. Inicialización de Visibilidad

Cuando se importan contactos, cada uno recibe un timestamp `last_visibility_time`:

```
POST /import
├─ Contacto nuevo → last_visibility_time = ahora
└─ Contacto existente → last_visibility_time = ahora (actualizado)
```

### 2. Cálculo de Estados Dinámicos

Cada vez que se cargan contactos (GET /contacts), el servidor:

1. **Calcula** cuántos meses han pasado desde `last_visibility_time`
2. **Compara** contra los umbrales configurados:
   - Si ≥ 8 meses → Estado = `NO_CONTACTO`
   - Si ≥ 6 meses → Estado = `SIN_RED`
   - Si ≥ 3 meses → Estado = `NO_EXISTE`
3. **Actualiza** el estado en la base de datos si procede
4. **Ordena** contactos por prioridad antes de enviar al cliente

### 3. Display en Cliente

La UI muestra información de visibilidad:

```
📱 Juan Pérez
☎️ +506-5123-4567 (51234567)
Status: NC [No hay visibilidad en 0 meses]
```

Con indicadores visuales:
- `[⏰ 3 meses no existe]` - 3+ meses sin ver
- `[⚠️ 6 meses sin red]` - 6+ meses sin ver
- `[❌ 8 meses sin contacto]` - 8+ meses sin ver

## Configuración

Editar en `config.py`:

```python
# ========== ESTADOS DINÁMICOS POR VISIBILIDAD ==========
STATUS_AUTO_RULES = {
    'NO_EXISTE': (3, 'Número no existe - 3 meses sin visibilidad'),
    'SIN_RED': (6, 'Sin red - 6 meses sin visibilidad'),
    'NO_CONTACTO': (8, 'No quieren contacto - 8 meses sin visibilidad'),
}

# ========== PRIORIDADES DE ORDENAMIENTO ==========
STATUS_PRIORITY = {
    'NC': 1,                    # No Contesta
    'CUELGA': 2,               # Cuelgan
    'SIN_GESTIONAR': 3,        # Sin gestionar
    'INTERESADO': 4,           # Interesado
    'SERVICIOS_ACTIVOS': 10,   # Servicios activos
    'NO_EXISTE': 20,           # No existe
    'SIN_RED': 21,             # Sin red
    'NO_CONTACTO': 22,         # No quieren contacto
}
```

### Cambiar Umbrales

Ejemplo: Cambiar `NO_EXISTE` de 3 a 2 meses:

```python
STATUS_AUTO_RULES = {
    'NO_EXISTE': (2, 'Número no existe - 2 meses sin visibilidad'),  # ← 2 meses
    'SIN_RED': (6, 'Sin red - 6 meses sin visibilidad'),
    'NO_CONTACTO': (8, 'No quieren contacto - 8 meses sin visibilidad'),
}
```

### Agregar Nuevos Estados

Ejemplo: Agregar estado `INACTIVO` a los 1 mes:

```python
STATUS_AUTO_RULES = {
    'INACTIVO': (1, 'Inactivo - 1 mes sin visibilidad'),             # ← NUEVO
    'NO_EXISTE': (3, 'Número no existe - 3 meses sin visibilidad'),
    'SIN_RED': (6, 'Sin red - 6 meses sin visibilidad'),
    'NO_CONTACTO': (8, 'No quieren contacto - 8 meses sin visibilidad'),
}

STATUS_PRIORITY = {
    'NC': 1,
    'CUELGA': 2,
    'SIN_GESTIONAR': 3,
    'INTERESADO': 4,
    'SERVICIOS_ACTIVOS': 10,
    'INACTIVO': 15,            # ← NUEVO: Entre servicios activos y no existe
    'NO_EXISTE': 20,
    'SIN_RED': 21,
    'NO_CONTACTO': 22,
}
```

## Resetear Visibilidad

Cuando importas contactos (Excel), automáticamente se resetea `last_visibility_time` a la hora actual para:
- Contactos nuevos
- Contactos actualizados (misma base importada múltiples veces)

**Resultado:** El contador de inactividad vuelve a 0.

## Casos de Uso

### Caso 1: Re-importar Excel Mensualmente
1. Exportas contactos desde tu CRM
2. Importas en CallManager (POST /import)
3. Contactos actualizados → last_visibility_time = ahora
4. Contador vuelve a 0

### Caso 2: Identificar Números Muertos
1. Dejas sin tocar la base 6 meses
2. Cargas contactos (GET /contacts)
3. El servidor detecta automáticamente:
   - `NO_EXISTE`: +506 números sin actividad 3+ meses → BAJA PRIORIDAD
   - `SIN_RED`: +506 números sin actividad 6+ meses → MUY BAJA
   - `NO_CONTACTO`: +506 números sin actividad 8+ meses → MÍNIMA
4. UI muestra solo NC y CUELGA al principio (máxima visibilidad)

### Caso 3: Patrón por Vendedor
Si un vendedor gestiona números y no los llama en 3 meses:
```
Juan García
Status: NC [⏰ 3 meses no existe]
```

El gestor/líder ve que no está siendo atendido → Action requerida.

## API

### GET /contacts

**Respuesta incluye:**

```json
{
  "id": "51234567",
  "phone": "+506-5123-4567",
  "name": "Juan Pérez",
  "status": "NC",
  "last_visibility_time": "2025-11-15T10:30:00",
  "visibility_months_ago": 0,
  "last_called_time": "2025-11-15T09:00:00",
  "locked_by": null,
  ...
}
```

**Campos nuevos:**
- `last_visibility_time`: ISO timestamp de última actualización
- `visibility_months_ago`: Número de meses sin visibilidad (calculado por cliente)

### POST /import

Al importar, automáticamente:
1. Si contacto existe → actualizar + resetear `last_visibility_time`
2. Si contacto es nuevo → crear + asignar `last_visibility_time = ahora`

**Respuesta:**
```json
{
  "inserted": 50,
  "updated": 120,
  "duplicates_merged": 45,
  "total": 170
}
```

## Logs

Verificar en `callmanager.log`:

```
2025-11-15 10:30:12 - CallManager - INFO - Auto-status for 51234567: NO_EXISTE (Número no existe - 3 meses sin visibilidad)
2025-11-15 10:30:12 - CallManager - INFO - Contacts sorted by priority. Order: ['NC', 'NC', 'CUELGA', 'SIN_GESTIONAR', ...]
2025-11-15 10:30:12 - CallManager - INFO - Retrieved 1250 contacts (sorted by priority)
```

## Troubleshooting

### P: ¿Por qué un contacto sigue siendo NC después de 3 meses?
**R:** Los estados dinámicos solo se asignan si el contacto:
- NO tiene estado manual (como INTERESADO, SERVICIOS_ACTIVOS)
- Cumple con el umbral de inactividad
- Si necesitas forzar, cambia el status manualmente en la UI

### P: ¿Cómo reseteo el contador sin reimportar?
**R:** Actualmente se resetea solo con:
- `POST /import` (importar archivo Excel)
- Actualizar el contacto vía Socket.IO

Próximamente: endpoint manual para resetear visibilidad por contacto.

### P: ¿Se pierden los datos de contacto?
**R:** **NO**. El sistema solo actualiza el `status` automáticamente. Todos los datos (nombre, teléfono, notas, historial) se mantienen intactos.

## Próximas Mejoras

- [ ] Dashboard de estadísticas (% NC vs SIN_RED vs NO_CONTACTO)
- [ ] Filtro por estado en UI
- [ ] Endpoint para resetear visibilidad individual
- [ ] Alertas cuando contacto entra en estado crítico (8 meses)
- [ ] Exportar reporte de números muertos
- [ ] Webhook para notificar cambios de estado

---

**Versión:** 2.0  
**Última actualización:** Noviembre 15, 2025  
**Estado:** Producción - Listo para Lunes
