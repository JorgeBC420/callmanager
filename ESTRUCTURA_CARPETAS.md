# 📁 Estructura de Carpetas - CallManager v2.0

## Descripción General

```
callmanager/
├── 📄 README.md                    ← Portada del proyecto
├── 📄 requirements.txt              ← Dependencias Python
├── 📄 Dockerfile                    ← Imagen Docker
├── 📄 docker-compose.yml            ← Orquestación Docker
├── 📄 .env.example                  ← Variables de entorno (EJEMPLO)
├── 📄 .dockerignore                 ← Archivos a ignorar en Docker
├── 📄 .gitignore                    ← Archivos a ignorar en Git
│
├── 📂 docs/                         ← DOCUMENTACIÓN
│   ├── AUTENTICACION.md
│   ├── DEPLOYMENT_PRODUCCION.md
│   ├── GUIA_CONTINUE_SETUP.md
│   └── ... (otros .md)
│
├── 📂 tests/                        ← TESTS UNITARIOS
│   ├── test_auth_system.py
│   ├── test_roles.py
│   ├── test_phone_generator_window.py
│   └── __init__.py
│
├── 📂 scripts/                      ← HERRAMIENTAS DE MANTENIMIENTO
│   ├── migrate_db.py                ← Migración de base de datos
│   ├── init_users.py                ← Crear usuarios iniciales
│   ├── setup_secure.py              ← Setup de seguridad
│   ├── build_executable.py          ← Compilar exe (Windows)
│   ├── validate_v2.py               ← Validación de v2.0
│   ├── diagnostico_continue.py      ← Diagnóstico Continue
│   ├── demo/                        ← Archivos DEMO
│   │   ├── demo_contacts.csv
│   │   ├── demo_contacts.json
│   │   └── ...
│   └── ...
│
├── 📂 client/                       ← APLICACIÓN CLIENTE (GUI)
│   ├── 📄 call_manager_app.py       ← App principal v2.0
│   ├── 📄 call_manager_app_v1_backup.py
│   ├── 📄 config_loader.py
│   ├── 📄 interphone_controller.py
│   ├── 📄 config_local.example.json
│   │
│   ├── 📂 ui/                       ← COMPONENTES VISUALES
│   │   ├── phone_generator_window.py
│   │   ├── phone_generator.py
│   │   └── __init__.py
│   │
│   └── 📂 __pycache__/
│
├── 📂 src/                          ← (Opcional) CÓDIGO FUENTE SERVIDOR
│   └── server.py → (Actualmente en raíz, puedes mover aquí)
│
├── 📂 backups/                      ← BACKUPS AUTOMÁTICOS BD
│   └── contacts_backup_*.db
│
├── 📂 logs/                         ← LOGS DE EJECUCIÓN
│   └── callmanager.log
│
├── 📂 .continue/                    ← CONFIG CONTINUE (IGNORED)
│   └── config.yaml
│
├── 📂 .vs/                          ← VS CODE SETTINGS (IGNORED)
│
├── 📂 .vscode/                      ← VS CODE WORKSPACE
│   └── settings.json
│
├── 📂 __pycache__/                  ← CACHE PYTHON (IGNORED)
│
└── 📄 server.py                     ← SERVIDOR FLASK (Root por ahora)
```

## 📋 Descripción de cada carpeta

### 📂 **docs/** - Documentación
- Toda la documentación en Markdown
- Incluye guías de configuración, deployment, auditoría, etc.
- **NO incluye** README.md (está en raíz como portada)

**Ejemplos:**
- AUTENTICACION.md - Cómo funciona el sistema de auth
- DEPLOYMENT_PRODUCCION.md - Cómo deployar a producción
- GUIA_CONTINUE_SETUP.md - Configurar Continue + Ollama offline

### 📂 **tests/** - Testing
- Tests unitarios y de integración
- **Convención:** `test_*.py`
- Ejecutar con: `pytest tests/`

**Ejemplos:**
- test_auth_system.py - Tests de autenticación
- test_roles.py - Tests de roles/permisos

### 📂 **scripts/** - Herramientas de Mantenimiento
- Scripts para tareas administrativas
- Setup, migrations, backups, etc.
- **NO son parte de la app principal**

**Ejemplos:**
- migrate_db.py - Migrar base de datos
- init_users.py - Crear usuario admin
- setup_secure.py - Setup de seguridad
- demo/ - Archivos de demostración

### 📂 **client/** - Aplicación Cliente
- Código GUI (CustomTkinter)
- Interface gráfica del usuario
- **client/ui/** - Componentes visuales reutilizables

**Archivos principales:**
- call_manager_app.py - App principal v2.0 (10/10 UX)
- interphone_controller.py - Integración InterPhone
- config_loader.py - Carga de configuración

### 📂 **client/ui/** - Componentes Visuales
- Módulos reutilizables de UI
- phone_generator_window.py - Ventana generador de números
- phone_generator.py - Lógica de generación

### 📂 **backups/** - Backups Automáticos
- Backups automáticos de la base de datos
- Formato: `contacts_backup_YYYYMMDD_HHMMSS.db`
- Se generan en cada inicio del servidor

### 📂 **logs/** - Logs de Ejecución
- Archivos de log (.log)
- callmanager.log - Log principal
- Configurado en logging.py

## 🚀 Cómo ejecutar

### Desarrollo Local
```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Iniciar servidor
python server.py

# 3. En otra terminal, iniciar cliente
python client/call_manager_app.py
```

### Con Docker
```bash
# Construir imagen
docker-compose build

# Iniciar servicios
docker-compose up -d

# Ver logs
docker-compose logs -f callmanager-server

# Detener
docker-compose down
```

### Scripts de Mantenimiento
```bash
# Migrar base de datos
python scripts/migrate_db.py

# Crear usuario admin
python scripts/init_users.py

# Validar v2.0
python scripts/validate_v2.py

# Diagnóstico Continue
python scripts/diagnostico_continue.py
```

### Ejecutar Tests
```bash
# Todos los tests
pytest tests/

# Test específico
pytest tests/test_auth_system.py

# Con cobertura
pytest tests/ --cov=client --cov=tests
```

## 📝 Importancias por Carpeta

| Carpeta | Importancia | Cambios Frecuentes |
|---------|-------------|-------------------|
| `client/` | 🔴 CRÍTICA | ✅ Sí (feature requests) |
| `docs/` | 🟡 MEDIA | ✅ Sí (documentación) |
| `scripts/` | 🟢 BAJA | ❌ No (estables) |
| `tests/` | 🟡 MEDIA | ✅ Sí (nuevos tests) |
| `backups/` | 🔴 CRÍTICA | ✅ Automático |

## 🔐 .gitignore (archivos ignorados)
- `__pycache__/` - Cache Python
- `.env` - Variables de entorno (sensibles)
- `contacts.db` - Base de datos local
- `*.log` - Archivos de log
- `.vscode/`, `.vs/` - Configuración IDE
- `backups/` - Backups locales

## 📦 Docker

**Dockerfile:** Imagen para ejecutar CallManager en contenedor
- Usa Python 3.9 slim
- Instala dependencias automáticamente
- Ejecuta Gunicorn + eventlet en producción

**docker-compose.yml:** Orquestación
- Servicio callmanager-server (puerto 5000)
- Servicio nginx (proxy inverso, puerto 80)
- Volúmenes persistentes
- Health checks

## 🎯 Próximos Pasos

1. **Mover server.py a src/** (opcional)
   - `src/server.py` para mejor organización
   - Actualizar imports

2. **Nginx Configuration**
   - Crear `nginx.conf` para proxy inverso
   - SSL/TLS en producción

3. **CI/CD Pipeline**
   - GitHub Actions para tests automáticos
   - Deploy automático a Docker Hub

4. **Base de Datos Productiva**
   - Cambiar de SQLite a PostgreSQL
   - Implementar connection pooling

## 📞 Soporte

Para preguntas sobre la estructura:
1. Ver README.md en raíz
2. Ver docs/DEPLOYMENT_PRODUCCION.md
3. Ejecutar diagnóstico: `python scripts/diagnostico_continue.py`

---

**Versión:** 2.0  
**Última actualización:** 21 Noviembre 2025  
**Estado:** ✅ Estructura lista para producción
