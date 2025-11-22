# 📞 CallManager v3.3.1

**Sistema de Gestión de Contactos para Call Centers**  
**Auditado para Seguridad Empresarial** ✅

---

## ✨ Características

- 📱 Gestión de contactos con teléfonos Costa Rica
- 🎲 Generador de números realistas automático
- 📊 Importar/Exportar a Excel
- 🔐 Autenticación por API Key
- 👥 Control de acceso por roles (4 roles)
- 🔄 Sincronización real-time con Socket.IO
- 💾 Base de datos SQLite con backups automáticos
- 📞 Integración con InterPhone
- 🖥️ GUI moderna con CustomTkinter
- 🔒 Seguridad empresarial completa

---

## 🚀 Inicio Rápido

### 1. Setup Seguro (PRIMERO)

```bash
# Generar .env con claves seguras
python setup_secure.py
```

### 2. Instalar Dependencias

```bash
# Crear entorno virtual
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Instalar requirements
pip install -r requirements.txt
```

### 3. Ejecutar

```bash
# Servidor + Cliente
python run_demo.py

# O solo servidor
python server.py

# O solo cliente
python client/call_manager_app.py
```

---

## 📁 Estructura del Proyecto

```
callmanager/
├── server.py                           # Servidor Flask (1272 líneas)
├── config.py                           # Configuración centralizada
├── phone_generator.py                  # Generador de números CR
│
├── client/
│   ├── call_manager_app.py             # GUI (CustomTkinter)
│   ├── interphone_controller.py        # Integración InterPhone
│   ├── config_loader.py                # Cargador de config
│   └── __pycache__/
│
├── setup_secure.py                     # Setup seguro (claves)
├── build_executable.py                 # Constructor de EXE
├── requirements.txt                    # Dependencias
├── .env.example                        # Template de config (SIN claves)
├── .env                                # Config real (EN .gitignore)
│
├── SEGURIDAD.md                        # Auditoría de seguridad ✅
├── DEPLOYMENT_PRODUCCION.md            # Cómo desplegar
├── README.md                           # Este archivo
│
├── backups/                            # Backups automáticos
├── contacts.db                         # Base de datos
└── callmanager.log                     # Logs

```

---

## 🔐 Seguridad (IMPORTANTE)

### ✅ Lo que está bien

- **Sin credenciales en código**: Todo viene del `.env`
- **API Key segura**: Generada criptográficamente
- **Control de acceso**: Roles (Agent, TeamLead, ProjectManager, TI)
- **Validación de entrada**: Todo se valida antes de usar
- **SQLAlchemy ORM**: Previene SQL injection
- **Logging**: Registra todos los intentos de acceso
- **Rate limiting**: Protección contra ataques
- **Backups automáticos**: Recuperación en caso de error

### 🚨 Lo que NUNCA hacer

```python
# ❌ INCORRECTO
SECRET_KEY = 'my-secret'
API_KEY = 'sk-123456'

# ✅ CORRECTO
SECRET_KEY = os.getenv('CALLMANAGER_SECRET_KEY')
API_KEY = os.getenv('CALLMANAGER_API_KEY')
```

### 📋 Para IT: Auditoría Pre-Deploy

```bash
# 1. Verificar que .env NO está en git
git ls-files | grep -E "\.env$"  # Debe estar vacío

# 2. Verificar credenciales NO en código
python setup_secure.py  # Valida automáticamente

# 3. Instalar dependencias limpias
pip install -r requirements.txt

# 4. Ver documentación de seguridad
cat SEGURIDAD.md
```

---

## 📱 Funcionalidades Principales

### 1. Gestión de Contactos

**Importar**:
- Botón: `📥 Importar Excel`
- Carga archivos .xlsx, .xls, .csv
- Detecta automáticamente columnas
- No crea duplicados

**Exportar**:
- Botón: `📤 Exportar Excel`
- Descarga todos los contactos
- Incluye estado, notas, timestamps

**Generar**:
- Botón: `🎲 Generar`
- 3 métodos: stratified (recomendado), simple, random
- Operadores CR: Kölbi (40%), Telefónica (35%), Claro (25%)
- Cantidad: 1-1000 números

### 2. Control de Acceso por Roles

| Rol | Lectura | Actualizar | Generar | Borrar |
|-----|---------|-----------|---------|--------|
| Agent | ✅ | ✅ | ❌ | ❌ |
| TeamLead | ✅ | ✅ | ❌ | ❌ |
| ProjectManager | ✅ | ✅ | ✅ | ✅ |
| TI | ✅ | ✅ | ✅ | ✅ |

### 3. Real-Time Sync

- Socket.IO para sincronización instantánea
- Múltiples clientes conectados
- Bloqueos inteligentes de contactos
- Historial de ediciones

---

## 🛠️ Deployment

### Opción 1: Windows (Más común)

```bash
# 1. Setup seguro
python setup_secure.py

# 2. Crear EXE actualizable
python build_executable.py

# 3. Distribuir dist/CallManager/
# Los usuarios ejecutan: install.bat
```

### Opción 2: Linux/VPS

```bash
# Ver DEPLOYMENT_PRODUCCION.md
# Incluye: Nginx, SSL, Systemd, Supervisor
```

### Opción 3: Docker

```bash
# Ver docker-compose.yml (si existe)
docker-compose up -d
```

---

## 📊 API Endpoints

### Contactos

```
GET    /contacts              # Listar todos
POST   /contacts              # Crear nuevo
PUT    /contacts/<id>         # Actualizar
DELETE /contacts/<id>         # Eliminar (solo ProjectManager/TI)
GET    /export                # Descargar Excel
POST   /import                # Importar desde Excel
POST   /api/generate_contacts # Generar números CR
```

### Info

```
GET    /health                # Estado del servidor
GET    /metrics               # Estadísticas
GET    /config                # Configuración
```

**Header requerido**: `X-API-Key: your-api-key`

---

## 🔧 Configuración

### Variables de Entorno (.env)

```dotenv
# Seguridad
FLASK_ENV=production
CALLMANAGER_SECRET_KEY=<cambiar-antes-producción>
CALLMANAGER_API_KEY=<cambiar-antes-producción>

# Base de datos
DATABASE_PATH=./contacts.db
BACKUP_DIR=./backups
BACKUP_INTERVAL_MINUTES=30
BACKUP_KEEP_DAYS=7

# Servidor
CALLMANAGER_HOST=0.0.0.0
CALLMANAGER_PORT=5000

# Logging
LOG_LEVEL=INFO
LOG_FILE=./callmanager.log

# Autenticación
ENABLE_AUTH=true
DEFAULT_LOCK_DURATION_MINUTES=10
```

---

## 📞 Soporte & Documentación

### Documentos Incluidos

| Documento | Propósito |
|-----------|-----------|
| `SEGURIDAD.md` | Auditoría completa de seguridad |
| `DEPLOYMENT_PRODUCCION.md` | Guía de despliegue en producción |
| `INTEGRACION_GENERADOR_CONTACTOS.md` | Detalles del generador de números |
| `RESUMEN_VISUAL_INTEGRACION.md` | Arquitectura y flujos |
| `CHECKLIST_PHONE_GENERATOR.md` | Verificaciones completas |

### Requisitos del Sistema

- **Python**: 3.7 o superior
- **RAM**: Mínimo 512 MB
- **Disco**: 100 MB + espacio para BD
- **OS**: Windows, Linux, macOS

### Dependencias Principales

```
flask>=2.0              # Framework web
sqlalchemy              # ORM para BD
customtkinter           # GUI
python-socketio         # Real-time
pandas, openpyxl        # Excel support
gunicorn                # Production server
python-dotenv           # .env loader
```

---

## 🔄 Actualizar a Nueva Versión

### Con Git

```bash
git pull origin main
pip install -r requirements.txt --upgrade
python setup_secure.py  # Verificar seguridad
```

### Con EXE

```
El EXE incluido auto-actualiza desde Git
No requiere intervención manual
```

---

## 🐛 Reportar Problemas

### Para Desarrolladores

```bash
# Crear issue en GitHub
# Incluir:
# - Versión de Python
# - OS
# - Error completo del log
# - Pasos para reproducir
```

### Para Usuarios Finales

```
Contactar a: IT/Soporte técnico
No cambiar archivos del programa
Ejecutar: python setup_secure.py si hay problemas
```

---

## 📈 Versión & Changelog

**Versión Actual**: 3.3.1  
**Última Actualización**: Noviembre 2024

### v3.3.1 - Auditoría & Seguridad
- ✅ Auditoría completa de seguridad
- ✅ Documentación de deployment
- ✅ Setup seguro y validación
- ✅ Constructor de EXE con auto-update

### v3.3.0 - Phone Generator & Export
- ✅ Generador de números Costa Rica
- ✅ Endpoint de exportación Excel
- ✅ Botones en GUI

### v3.2.0 - RBAC y DELETE
- ✅ Control de acceso por roles
- ✅ Endpoint DELETE /contacts/<id>
- ✅ Corrección de errores previos

---

## 📄 Licencia

Copyright © 2024 CallManager Team

---

## ✅ Checklist para IT (Auditoría)

Antes de aprobar en tu empresa:

- [ ] Revisó `SEGURIDAD.md` completo
- [ ] Verificó que `.env` NO está en git
- [ ] Corrió `python setup_secure.py` exitosamente
- [ ] Revisó `requirements.txt` (sin librerías extrañas)
- [ ] Probó importar/exportar Excel
- [ ] Verificó roles de acceso funcionan
- [ ] Testeó autenticación
- [ ] Revisó logging
- [ ] Verificó backups automáticos
- [ ] Leyó `DEPLOYMENT_PRODUCCION.md`
- [ ] ✅ APROBADO para producción

---

**¿Preguntas?** Revisa los archivos `.md` incluidos  
**¿Bugs?** Reporta en GitHub o contacta al equipo  
**¿Mejorias?** Pull requests bienvenidas

🚀 **Listo para producción**
