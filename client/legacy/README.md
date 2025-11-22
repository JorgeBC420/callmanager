# Legacy - Versiones Anteriores de CallManager

Esta carpeta contiene versiones anteriores de CallManager que han sido consolidadas en la versión actual.

## Archivos Archivados

### call_manager_app_v1_backup.py
- **Versión:** 1.0 (Original)
- **Estado:** 🔴 Deprecated
- **Descripción:** Primera versión de CallManager, sin Material Design, sin muchas funcionalidades
- **Razón de archivo:** Reemplazada por v2.0 completa

### call_manager_app_original_v2.py
- **Versión:** 2.0 (Original/Referencia)
- **Estado:** 🟡 Referencia
- **Descripción:** Versión original v2.0 con todas las funcionalidades básicas
- **Características:**
  - Socket.IO básico
  - Tarjetas de contacto
  - Búsqueda
  - Edición no implementada ("Funcionalidad en desarrollo")
  - Importar/Exportar simulado
- **Razón de archivo:** Mejorada en versión actual con edición completa

### call_manager_app_v2.py
- **Versión:** 2.0 (Copia de referencia)
- **Estado:** 🔴 Deprecated
- **Descripción:** Copia de call_manager_app_original_v2.py
- **Razón de archivo:** Duplicado, mantenido como backup

### call_manager_app_fixed.py
- **Versión:** 2.0 (Simplificada/Reparada)
- **Estado:** 🟡 Intermedia
- **Descripción:** Versión simplificada creada para reparar problemas de UI
- **Cambios:**
  - Removido Socket.IO (causaba bloqueos)
  - UI más simple y rápida
  - Fallback a JSON local
- **Razón de archivo:** Características reintegradas en versión completa

## Versión Actual Activa

### ../call_manager_app.py
- **Versión:** 2.0 (Completa y Mejorada)
- **Estado:** 🟢 **PRODUCCIÓN**
- **Líneas:** 1066
- **Características:**
  - ✅ Socket.IO completo (actualización en tiempo real)
  - ✅ Edición de contactos con diálogo modal
  - ✅ Importar/Exportar real (Excel, CSV, JSON)
  - ✅ Llamadas con InterPhone
  - ✅ Estados de contactos visuales
  - ✅ LoadingSpinner animado
  - ✅ StatusBar mejorada
  - ✅ Show Status detallado
  - ✅ Material Design Dark theme
  - ✅ Búsqueda en tiempo real
  - ✅ Threading optimizado
  - ✅ Error handling robusto

## Comparación de Características

| Función | v1 | v2 Original | Fixed | **v2 Actual** |
|---------|----|----|-------|-------|
| Material Design | ❌ | ✅ | ✅ | ✅ |
| Socket.IO | ❌ | ✅ | ❌ | ✅ |
| Búsqueda | ✅ | ✅ | ✅ | ✅ |
| Editar contacto | ❌ | ❌ | ❌ | ✅ |
| Borrar contacto | ✅ | ✅ | ✅ | ✅ |
| Llamadas | ✅ | ✅ | ✅ | ✅ |
| Importar/Exportar | ❌ | 🟡 | 🟡 | ✅ |
| LoadingSpinner | ❌ | ✅ | ✅ | ✅ |
| StatusBar avanzada | ❌ | ✅ | ✅ | ✅ |
| InterPhone | ✅ | ✅ | ✅ | ✅ |
| API Backend | ✅ | ✅ | ✅ | ✅ |
| Threading | ❌ | ✅ | ✅ | ✅ |

## Cómo Recuperar una Versión Antigua

Si necesitas revertir a una versión anterior:

```bash
# Copiar versión anterior
cp legacy/call_manager_app_original_v2.py ../call_manager_app.py

# O restaurar desde git
git log --oneline
git checkout <commit-hash> client/call_manager_app.py
```

## Estructura Actual del Proyecto

```
client/
├── call_manager_app.py        (ACTUAL - VERSIÓN ACTIVA)
├── config_loader.py
├── interphone_controller.py
├── config_local.example.json
├── ui/
│   ├── phone_generator_window.py
│   └── phone_generator.py
└── legacy/                     (ARCHIVOS ANTIGUOS)
    ├── call_manager_app_v1_backup.py
    ├── call_manager_app_original_v2.py
    ├── call_manager_app_v2.py
    └── call_manager_app_fixed.py
```

## Notas

- **Versión recomendada:** v2.0 Actual (call_manager_app.py)
- **Estado:** Producción lista
- **Soporte:** Socket.IO, API Backend, Material Design
- **Compatibilidad:** Python 3.9+, customtkinter, requests, socketio, pandas

## Historial de Cambios

1. **v1.0** - Versión inicial (básica)
2. **v2.0 Original** - Material Design + Socket.IO
3. **v2.0 Fixed** - Versión simplificada (reparación de bloqueos)
4. **v2.0 Actual** - Consolidación de todas las características en una sola versión completa y estable

---

**Última actualización:** 21 de Noviembre, 2025
**Versión consolidada:** 1066 líneas, totalmente funcional
