# Guía Visual - Qué Verás el Lunes

## Escenario: Importas 1000 contactos el lunes por la mañana

### ANTES (Fase 1 - Sin estados dinámicos)
```
Contacto             Status              Prioridad  Visible
─────────────────────────────────────────────────────────────
Rosa González        SERVICIOS_ACTIVOS   Mismo      Igual
Juan García          NC                  Mismo      Igual
María López          CUELGA              Mismo      Igual
Carlos Ruiz          NO_EXISTE           Manual     Mismo
(1000 contactos más en orden aleatorio)
```

### AHORA (Fase 2.1 - Con estados dinámicos)
```
Contacto             Status              Prioridad  Visible
─────────────────────────────────────────────────────────────
Juan García          NC                  1          ✅ PRIMERO
María López          CUELGA              2          ✅ SEGUNDO
Carlos Ruiz          SIN_GESTIONAR       3          ✅ TERCERO
Ana Martínez         INTERESADO          4          ✅ CUARTO
Rosa González        SERVICIOS_ACTIVOS   10         ⬇️ ABAJO (como pediste)
Luis Torres          NO_EXISTE           20         📌 MUY ABAJO
Diego Soto           SIN_RED             21         📌 MUY ABAJO
Pedro Flores         NO_CONTACTO         22         📌 MÍNIMA (casi no lo ves)
```

---

## Interfaz del Cliente - Lo que ves en pantalla

### LUNES (Día 1 - Recién importado)

```
┌─────────────────────────────────────────────────────────────────┐
│  📥 Importar Excel   🔄 Refrescar   ℹ️ Estado                  │
│  Servidor: http://192.168.1.100:5000                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ 📱 Juan García                                    🔒 Bloquear │ │
│ │ ☎️ +506-5123-4567 (51234567)        📞 Llamar               │ │
│ │ Status: NC [⏰ 0 meses]                                    │ │
│ │ Nota: Llamó ayer, sin contestar                            │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                  │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ 📱 María López                                  🔒 Bloquear │ │
│ │ ☎️ +506-8234-5678 (82345678)        📞 Llamar               │ │
│ │ Status: CUELGA [⏰ 0 meses]                                │ │
│ │ Nota: Cuelga siempre después de 2 segundos                 │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                  │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ 📱 Carlos Ruiz                                  🔒 Bloquear │ │
│ │ ☎️ +506-9345-6789 (93456789)        📞 Llamar               │ │
│ │ Status: SIN_GESTIONAR [⏰ 0 meses]                         │ │
│ │ Nota: Aún no gestionado, nuevo en la cartera              │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                  │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ 📱 Rosa González                                🔒 Bloquear │ │
│ │ ☎️ +506-1111-2222 (11112222)        📞 Llamar               │ │
│ │ Status: SERVICIOS_ACTIVOS [⏰ 0 meses]                    │ │
│ │ Nota: Cliente activo, servicio hasta diciembre            │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                  │
│ [Scroll para ver más...] (996 contactos más)                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### MES 3 (Sin reimportar - 3 meses después)

```
┌─────────────────────────────────────────────────────────────────┐
│  📥 Importar Excel   🔄 Refrescar   ℹ️ Estado                  │
│  Servidor: http://192.168.1.100:5000                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ 📱 Juan García                                  🔒 Bloquear │ │
│ │ ☎️ +506-5123-4567 (51234567)        📞 Llamar               │ │
│ │ Status: NC [⏰ 3 meses]                                    │ │
│ │ Nota: Llamó ayer, sin contestar                            │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                  │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ 📱 María López                                  🔒 Bloquear │ │
│ │ ☎️ +506-8234-5678 (82345678)        📞 Llamar               │ │
│ │ Status: CUELGA [⏰ 3 meses]                                │ │
│ │ Nota: Cuelga siempre después de 2 segundos                 │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                  │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ 📱 Rosa González                                🔒 Bloquear │ │
│ │ ☎️ +506-1111-2222 (11112222)        📞 Llamar               │ │
│ │ Status: SERVICIOS_ACTIVOS [⏰ 0 meses]                    │ │
│ │ Nota: Cliente activo, servicio hasta diciembre            │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                  │
│ ⚠️ ABAJO (scrollear):                                           │
│                                                                  │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ 📱 Carlos Ruiz                                  🔒 Bloquear │ │
│ │ ☎️ +506-9345-6789 (93456789)        📞 Llamar               │ │
│ │ Status: NO_EXISTE [⏰ 3 meses no existe]                   │ │
│ │ Nota: Aún no gestionado, nuevo en la cartera              │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                  │
│ [Scroll para ver más...] (996 contactos más)                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**KEY CHANGE:** Carlos Ruiz se movió ABAJO porque:
- Status automáticamente cambió de "SIN_GESTIONAR" a "NO_EXISTE"
- Prioridad cambió de 3 → 20
- Ahora está debajo de Rosa González (SERVICIOS_ACTIVOS)

### MES 6 (Sin reimportar)

Carlos Ruiz ahora:
```
Status: SIN_RED [⏰ 6 meses sin red]
```
- Prioridad: 21 (aún más abajo)

### MES 8 (Sin reimportar)

Carlos Ruiz ahora:
```
Status: NO_CONTACTO [❌ 8 meses sin contacto]
```
- Prioridad: 22 (casi invisible)
- Tienes que scrollear MUCHO para verlo

### MES 3 - REIMPORTANDO EXCEL ACTUALIZADO

```
Paso 1: Cargas "contactos_mes3.xlsx" (1000 números, algunos actualizados)
Paso 2: Click en "📥 Importar Excel"
Paso 3: El servidor detecta:
        ├─ Carlos Ruiz: Ya existe
        ├─ Acción: Actualizar datos
        └─ Acción: last_visibility_time = AHORA ← RESET

Resultado Inmediato:
        ├─ Carlos vuelve a aparecer en su posición original
        ├─ Status vuelve a: SIN_GESTIONAR (o lo que sea en la importación)
        ├─ Prioridad vuelve a: 3
        ├─ [⏰ 0 meses] (contador vuelve a cero)
```

Pantalla después de reimportar:

```
┌─────────────────────────────────────────────────────────────────┐
│  Importación completada:                                         │
│  - Insertados: 50 nuevos contactos                              │
│  - Actualizados: 900 contactos existentes                       │
│  - Duplicados fusionados: 50                                    │
│  ✅ ACEPTAR                                                      │
└─────────────────────────────────────────────────────────────────┘

PANTALLA DESPUÉS:

┌─────────────────────────────────────────────────────────────────┐
│ 📱 Juan García           NC                [⏰ 0 meses]  ✅      │
│ 📱 María López           CUELGA            [⏰ 0 meses]  ✅      │
│ 📱 Carlos Ruiz           SIN_GESTIONAR     [⏰ 0 meses]  ✅      │
│ 📱 Ana Martínez          INTERESADO        [⏰ 0 meses]  ✅      │
│ 📱 Rosa González         SERVICIOS_ACTIVOS [⏰ 0 meses]  ⬇️      │
│ ... (más contactos en orden de prioridad)                       │
└─────────────────────────────────────────────────────────────────┘
```

---

## Logs que Verás

Cuando carga contactos, en `callmanager.log` verás:

**Primero (Lunes):**
```
2025-11-15 10:30:00 - CallManager - INFO - Import complete: 950 inserted, 50 updated (merged 50 duplicates)
2025-11-15 10:30:05 - CallManager - INFO - Contacts sorted by priority. Order: ['NC', 'CUELGA', 'SIN_GESTIONAR', 'INTERESADO', 'SERVICIOS_ACTIVOS', ...]
2025-11-15 10:30:05 - CallManager - INFO - Retrieved 1000 contacts (sorted by priority)
```

**Mes 3:**
```
2025-02-15 10:30:05 - CallManager - INFO - Auto-status for 51234567: NO_EXISTE (Número no existe - 3 meses sin visibilidad)
2025-02-15 10:30:05 - CallManager - INFO - Auto-status for 82345678: NO_EXISTE (Número no existe - 3 meses sin visibilidad)
2025-02-15 10:30:05 - CallManager - INFO - Auto-status for 93456789: NO_EXISTE (Número no existe - 3 meses sin visibilidad)
2025-02-15 10:30:05 - CallManager - INFO - Contacts sorted by priority. Order: ['NC', 'CUELGA', 'SIN_GESTIONAR', 'INTERESADO', 'SERVICIOS_ACTIVOS', 'NO_EXISTE', 'NO_EXISTE', 'NO_EXISTE', ...]
```

**Mes 3 - Reimportando:**
```
2025-02-15 10:30:00 - CallManager - INFO - Updated existing contact: 51234567 (Carlos Ruiz → Carlos Ruiz [actualizado])
2025-02-15 10:30:00 - CallManager - INFO - Import complete: 50 inserted, 900 updated (merged 50 duplicates)
2025-02-15 10:30:05 - CallManager - INFO - Contacts sorted by priority. Order: ['NC', 'CUELGA', 'SIN_GESTIONAR', 'INTERESADO', 'SERVICIOS_ACTIVOS', 'NO_EXISTE', ...]
```

---

## Tabla Comparativa: Antes vs Después

| Aspecto | ANTES (Fase 2) | AHORA (Fase 2.1) |
|---------|------|------|
| **Estados disponibles** | 5 estados | 8 estados (5 + 3 dinámicos) |
| **Orden al cargar** | Aleatorio | Por prioridad automática |
| **Visibilidad de NC** | En el medio | PRIMERO (prioridad 1) |
| **Visibilidad de SERVICIOS_ACTIVOS** | En el medio | ABAJO (prioridad 10) |
| **Contactos viejos (3+ meses)** | No definido | NO_EXISTE (prioridad 20) |
| **Contactos muy viejos (8+ meses)** | No definido | NO_CONTACTO (prioridad 22) |
| **Cómo se detectan viejos** | Manual | Automático por inactividad |
| **Reset de contador** | No aplica | Al reimportar Excel |
| **Información de meses inactivo** | No mostrada | Mostrada en UI: [⏰ X meses] |
| **Cambiar prioridades** | Modifica código | Edita config.py (1 línea) |

---

## Casos de Uso Reales - Lunes

### Escenario 1: Vendedor Juan García
```
Lunes: Importas su cartera
├─ Status: NC (No Contesta)
├─ Prioridad: 1 (MÁXIMA) ✅
├─ Visible: SÍ (primero en la lista)

Mes 3 (sin contacto):
├─ Status: Sigue siendo NC (estado manual)
├─ Prioridad: Sigue siendo 1 (estados manuales no cambian)
├─ Visible: SÍ (NC nunca baja)
└─ [⏰ 3 meses] (pero aún NC = sigue prioritario)
```

### Escenario 2: Vendedor Carlos Ruiz (sin gestionar)
```
Lunes: Importas su cartera
├─ Status: SIN_GESTIONAR
├─ Prioridad: 3 (NORMAL)
├─ Visible: SÍ (tercero en la lista)

Mes 3 (sin contacto):
├─ Status: Cambió a NO_EXISTE (automático)
├─ Prioridad: Cambió a 20 (MUY BAJA)
├─ Visible: NO (tienes que scrollear)
└─ [⏰ 3 meses no existe] (automáticamente)

Mes 3 + Reimportar:
├─ Status: Vuelve a SIN_GESTIONAR (importación actualiza)
├─ Prioridad: Vuelve a 3
├─ Visible: SÍ (vuelve a tercero)
└─ [⏰ 0 meses] (contador reseteado)
```

### Escenario 3: Cliente Rosa González (SERVICIOS_ACTIVOS)
```
Lunes: Importas su contacto
├─ Status: SERVICIOS_ACTIVOS
├─ Prioridad: 10 (BAJA - como pediste)
├─ Visible: SÍ pero ABAJO (después de NC, CUELGA, SIN_GESTIONAR, INTERESADO)

Mes 3:
├─ Status: Sigue siendo SERVICIOS_ACTIVOS (estado manual = no cambia)
├─ Prioridad: Sigue siendo 10
├─ Visible: SÍ pero ABAJO (no asciende a NO_EXISTE porque es manual)
└─ [⏰ 3 meses] (pero no se convierte en NO_EXISTE)
```

---

## Conclusión

**Lo más importante:** El lunes verás:

1. **NC y CUELGA PRIMERO** (máxima visibilidad)
2. **SERVICIOS_ACTIVOS ABAJO** (baja visibilidad, como pediste)
3. **Números viejos (3+ meses) CASI INVISIBLE** (al final)
4. **Indicadores visuales** de cuánto tiempo sin gestionar
5. **TODO ORDENADO AUTOMÁTICAMENTE** (no haces nada, se ordena solo)

**El beneficio:** Trabajadores ven primero lo que importa (NC, CUELGA) y casi no ven números muertos (NO_CONTACTO). ¡Visibilidad inteligente!

---

**Versión:** Guía Visual 1.0  
**Estado:** Listo para Lunes  
**Última actualización:** 15 de noviembre de 2025
