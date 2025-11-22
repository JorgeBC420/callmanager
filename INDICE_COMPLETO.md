# 📚 Índice de Documentación - CallManager v2.0

## 🎯 Empezar Aquí

**¿Primera vez?** → Leer en este orden:
1. **README.md** - Qué es CallManager
2. **ESTRUCTURA_CARPETAS.md** - Cómo está organizado
3. **CAMBIOS_REORGANIZACION_v2.md** - Qué cambió en v2.0

---

## 📂 Documentación por Categoría

### 🚀 Deployment & Producción
- **docs/DEPLOYMENT_PRODUCCION.md** ← LEER PRIMERO
- **docs/DEPLOYMENT.md**
- **Dockerfile** - Imagen Docker
- **docker-compose.yml** - Orquestación

### 🔐 Autenticación & Seguridad
- **docs/AUTENTICACION.md** - Cómo funciona auth
- **docs/AUTENTICACION_IMPLEMENTADA.md** - Implementación
- **docs/ROLES_Y_AUTORIZACION.md** - Permisos por rol
- **docs/SEGURIDAD.md** - Mejores prácticas

### 💻 Desarrollo Local
- **docs/INICIO_RAPIDO.md** - Setup rápido
- **docs/GUIA_RAPIDA_LUNES.md** - Checklist semanal
- **docs/DEMO.md** - Cómo usar demo

### 🎨 Interfaz Gráfica
- **docs/CALL_MANAGER_v2_TRANSFORMACION.md** - Rediseño UI v2.0
- **docs/RESUMEN_PRUEBA_VISUAL.md** - Pruebas visuales
- **docs/COMPARATIVO_VISUAL_GENERADOR.md** - Componentes visuales

### 📱 Generador de Teléfonos
- **docs/GUIA_USUARIO_GENERADOR.md** - Manual de usuario
- **docs/QUICK_START_PHONE_GENERATOR.md** - Setup rápido
- **docs/INTEGRACION_GENERADOR_CONTACTOS.md** - Cómo integrar
- **docs/CHECKLIST_PHONE_GENERATOR.md** - Verificación

### 🤖 Continue + Ollama (IA Offline)
- **docs/GUIA_CONTINUE_SETUP.md** - Configuración de Continue
- **scripts/diagnostico_continue.py** - Diagnóstico

### 🧪 Testing
- **tests/test_auth_system.py** - Tests de autenticación
- **tests/test_roles.py** - Tests de roles
- **tests/test_phone_generator_window.py** - Tests de UI
- **docs/CHECKLIST_VERIFICACION.md** - Checklist QA

### 🛠️ Scripts de Admin
```bash
python scripts/migrate_db.py              # Migrar BD
python scripts/init_users.py              # Crear usuarios
python scripts/setup_secure.py            # Setup seguridad
python scripts/build_executable.py        # Compilar exe
python scripts/validate_v2.py             # Validar v2.0
python scripts/diagnostico_continue.py    # Diagnóstico
python scripts/run_demo.py                # Ejecutar demo
```

### 📊 Cambios & Mejoras
- **CAMBIOS_REORGANIZACION_v2.md** - v2.0 reorganización
- **RESUMEN_REORGANIZACION_FINAL.md** - Resumen final
- **docs/MEJORAS_IMPLEMENTADAS.md** - Todas las mejoras
- **docs/MEJORAS_FASE2_COSTA_RICA.md** - Fase 2
- **docs/MEJORAS_FASE3.md** - Fase 3

### 📈 Auditoría & Análisis
- **docs/AUDITORIA_FINAL.md** - Auditoria completa
- **docs/AUDITORIA_CALLMANAGER_COMPLETA.md** - Detallada
- **docs/RESUMEN_AUDITORIA_FINAL.md** - Resumen
- **docs/DASHBOARD_ESTADO.md** - Estado actual

### 🏗️ Arquitectura
- **docs/ARQUITECTURA_FASE3.md** - Arquitectura actual
- **docs/PROPUESTA_REFACTORIZACION.md** - Mejoras propuestas
- **docs/ESTADOS_DINAMICOS.md** - Gestión de estados
- **docs/FASE3_CAMBIOS_IMPLEMENTADOS_P1.md** - Cambios fase 3

### 🧩 Análisis Técnico
- **docs/ANALISIS_GENERADOR_MEJORADO.md** - Análisis del generador
- **docs/IMPLEMENTACION_GENERADOR_MEJORADO.md** - Implementación
- **docs/INDICE_DOCUMENTACION.md** - Índice anterior

### ✅ Listas de Verificación
- **docs/CHECKLIST_PHONE_GENERATOR.md** - Generator checklist
- **docs/CHECKLIST_QUE_ESPERAR.md** - Qué esperar
- **docs/CHECKLIST_VERIFICACION.md** - Verificación completa

### 📝 Resúmenes & Reportes
- **docs/RESUMEN_EJECUTIVO_AUDITORIA.md** - Ejecutivo
- **docs/RESUMEN_FINAL_AUTENTICACION.md** - Auth resumen
- **docs/RESUMEN_CAMBIOS_SESSION.md** - Cambios de sesión
- **docs/SESION_COMPLETADA_RESUMEN.md** - Sesión completada
- **docs/REPORTE_PRUEBA_COMPLETO.md** - Reporte de pruebas
- **docs/RESUMEN_EJECUTIVO_V3.3.md** - v3.3 resumen
- **docs/RESUMEN_PRUEBA_VISUAL.md** - Prueba visual
- **docs/RESUMEN_VISUAL_INTEGRACION.md** - Integración visual
- **docs/RESUMEN_DE_CAMBIOS.md** - Todos los cambios
- **docs/ERRORES_ENCONTRADOS_Y_CORREGIDOS.md** - Errores & fixes

### 📺 Guías Visuales
- **docs/GUIA_VISUAL_LUNES.md** - Guía con imágenes
- **docs/GUIA_RAPIDA_AUTENTICACION.md** - Auth rápido
- **docs/QUICK_START_GUIA_RAPIDA.md** - Quick start

### 🌐 Información de Producción
- **docs/README_PRODUCCION.md** - README para prod

---

## 🗂️ Estructura de Carpetas

```
callmanager/
├── 📂 docs/                          ← DOCUMENTACIÓN (estás aquí)
│   ├── AUTENTICACION.md
│   ├── DEPLOYMENT_PRODUCCION.md      ← LEER PRIMERO
│   ├── GUIA_CONTINUE_SETUP.md
│   └── ... (50+ archivos)
│
├── 📂 tests/                         ← TESTS
│   ├── test_auth_system.py
│   ├── test_roles.py
│   └── test_phone_generator_window.py
│
├── 📂 scripts/                       ← SCRIPTS ADMIN
│   ├── migrate_db.py
│   ├── init_users.py
│   ├── setup_secure.py
│   ├── validate_v2.py
│   ├── diagnostico_continue.py
│   └── demo/
│       ├── demo_contacts.csv
│       └── demo_contacts.json
│
├── 📂 client/                        ← APP GUI
│   ├── call_manager_app.py           ← Principal
│   ├── config_loader.py
│   ├── interphone_controller.py
│   └── 📂 ui/                        ← Componentes
│       ├── phone_generator_window.py
│       └── phone_generator.py
│
├── 📄 Dockerfile                     ← Docker image
├── 📄 docker-compose.yml             ← Orquestación
├── 📄 .dockerignore
├── 📄 server.py                      ← Servidor Flask
├── 📄 requirements.txt
│
└── 📚 DOCUMENTACIÓN EN RAÍZ
    ├── README.md                     ← Portada
    ├── ESTRUCTURA_CARPETAS.md        ← Este archivo
    ├── CAMBIOS_REORGANIZACION_v2.md
    ├── RESUMEN_REORGANIZACION_FINAL.md
    └── ...
```

---

## 🔍 Buscar por Tema

### ¿Quiero...?

**...deployar a producción**
→ docs/DEPLOYMENT_PRODUCCION.md
→ Dockerfile
→ docker-compose.yml

**...configurar autenticación**
→ docs/AUTENTICACION.md
→ docs/ROLES_Y_AUTORIZACION.md

**...usar Continue + Ollama offline**
→ docs/GUIA_CONTINUE_SETUP.md
→ scripts/diagnostico_continue.py

**...entender la arquitectura**
→ docs/ARQUITECTURA_FASE3.md
→ docs/PROPUESTA_REFACTORIZACION.md

**...crear usuarios**
→ python scripts/init_users.py
→ docs/AUTENTICACION.md

**...migrar la base de datos**
→ python scripts/migrate_db.py
→ docs/DEPLOYMENT_PRODUCCION.md

**...ejecutar tests**
→ pytest tests/
→ docs/CHECKLIST_VERIFICACION.md

**...usar el generador de teléfonos**
→ docs/GUIA_USUARIO_GENERADOR.md
→ docs/QUICK_START_PHONE_GENERATOR.md

**...entender los cambios de v2.0**
→ CAMBIOS_REORGANIZACION_v2.md
→ RESUMEN_REORGANIZACION_FINAL.md

**...troubleshooting**
→ scripts/diagnostico_continue.py
→ docs/ERRORES_ENCONTRADOS_Y_CORREGIDOS.md

---

## 📱 Quick Links

| Tarea | Comando | Documentación |
|-------|---------|---------------|
| Dev local | `python server.py` | docs/INICIO_RAPIDO.md |
| Run cliente | `python client/call_manager_app.py` | - |
| Docker | `docker-compose up -d` | docker-compose.yml |
| Tests | `pytest tests/` | - |
| Crear usuario | `python scripts/init_users.py` | docs/AUTENTICACION.md |
| Migrar BD | `python scripts/migrate_db.py` | - |
| Diagnóstico | `python scripts/diagnostico_continue.py` | docs/GUIA_CONTINUE_SETUP.md |
| Demo | `python scripts/run_demo.py` | docs/DEMO.md |

---

## 📞 Soporte

### Si tienes problema con...

**InterPhone:**
- Ver: docs/ERRORES_ENCONTRADOS_Y_CORREGIDOS.md
- Script: client/interphone_controller.py

**Autenticación:**
- Ver: docs/AUTENTICACION.md
- Ejecutar: python scripts/init_users.py

**Continue/Ollama:**
- Ver: docs/GUIA_CONTINUE_SETUP.md
- Ejecutar: python scripts/diagnostico_continue.py

**Docker:**
- Ver: docker-compose.yml
- Ver: Dockerfile

**Tests:**
- Ver: tests/
- Ejecutar: pytest tests/ -v

---

## 📚 Referencias Externas

- **Flask:** https://flask.palletsprojects.com/
- **Socket.IO:** https://python-socketio.readthedocs.io/
- **CustomTkinter:** https://github.com/TomSchimansky/CustomTkinter
- **Docker:** https://docs.docker.com/
- **Ollama:** https://ollama.ai/

---

**Última actualización:** 21 Noviembre 2025  
**Versión:** 2.0  
**Total de documentos:** 60+  
**Estado:** ✅ Completamente indexado
