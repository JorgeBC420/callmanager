# CallManager - Call Center Management System

**MVP Version 2.1** - Sistema de gestión de llamadas para call centers con soporte para Costa Rica

🔗 **GitHub**: https://github.com/JorgeBC420/callmanager

---

## 📋 Resumen Ejecutivo

CallManager es un **sistema completo cliente-servidor** para gestión de contactos y automatización de llamadas en call centers. Diseñado específicamente para enfrentar desafíos de gestión de bases de datos telefónicas en Costa Rica.

**Estado**: ✅ Listo para producción el lunes  
**Última actualización**: Noviembre 17, 2025

---

## 🎯 Características Principales

### ✅ Fase 1: Base Sólida
- **Servidor Flask + Socket.IO**: Backend escalable con comunicación en tiempo real
- **Cliente CustomTkinter**: UI moderna y profesional para Windows
- **Base de datos SQLite**: Con respaldo automático cada 30 minutos
- **Autenticación básica**: Sistema de API keys configurable
- **Validaciones robustas**: Teléfono, nombre, notas
- **Historial y auditoría**: Registro completo de cambios

### ✅ Fase 2: Mejoras Críticas (Costa Rica)
- **Detección automática de duplicados**: Si número existe → actualiza en lugar de insertar
- **Limpieza de prefijo +506**: Normaliza números para InterPhone sin errores
- **UI mejorada**: Muestra ambos formatos (original + normalizado)

### ✅ Fase 2.1: Estados Dinámicos
- **3 estados automáticos por inactividad**:
  - `NO_EXISTE` (3 meses sin ver)
  - `SIN_RED` (6 meses sin ver)
  - `NO_CONTACTO` (8 meses sin ver)
- **Ordenamiento inteligente por prioridad**:
  - NC (No Contesta) → MÁXIMA visibilidad
  - CUELGA → ALTA visibilidad
  - SERVICIOS_ACTIVOS → BAJA visibilidad
  - NO_CONTACTO → MÍNIMA visibilidad
- **Tracking automático**: Calcula meses de inactividad sin intervención manual

---

## 🚀 Quick Start

### Requisitos
- Python 3.8+
- Windows (para InterPhone)
- Red local con conexión TCP/IP

### Instalación

```bash
# Clonar repositorio
git clone https://github.com/JorgeBC420/callmanager.git
cd callmanager

# Instalar dependencias
pip install -r requirements.txt
```

### Configuración

#### Servidor (PC central)
```bash
# No requiere configuración adicional
python server.py
# El servidor escucha en 0.0.0.0:5000
```

#### Clientes (PCs de trabajadores)
```bash
cd client

# Copiar plantilla de configuración
copy config_local.example.json config_local.json

# Editar con IP del servidor
# En config_local.json cambiar:
# "SERVER_URL": "http://192.168.1.X:5000"

# Ejecutar cliente
python call_manager_app.py
```

---

## 📁 Estructura del Proyecto

```
callmanager/
├── server.py                      # Servidor Flask + Socket.IO
├── config.py                      # Configuración centralizada
├── requirements.txt               # Dependencias Python
│
├── client/
│   ├── call_manager_app.py       # GUI principal (CustomTkinter)
│   ├── config_loader.py          # Cargador de configuración
│   ├── interphone_controller.py  # Automatización de InterPhone
│   └── config_local.example.json # Plantilla de configuración
│
├── README.md                      # Este archivo
├── DEPLOYMENT.md                  # Guía de deployment completa
├── ESTADOS_DINAMICOS.md           # Documentación de estados automáticos
├── GUIA_RAPIDA_LUNES.md          # Procedimientos para lunes
├── GUIA_VISUAL_LUNES.md          # Guía visual paso a paso
├── MEJORAS_FASE2_COSTA_RICA.md   # Cambios de fase 2
├── MEJORAS_IMPLEMENTADAS.md      # Resumen de cambios fase 1
└── .gitignore                     # Archivos a excluir de Git
```

---

## 🔧 Arquitectura

### Modelo Cliente-Servidor

```
┌─────────────────┐        TCP/IP (puerto 5000)        ┌──────────────────┐
│  PC Central     │◄─────────WebSocket─────────────────►│  PC Worker 1     │
│  (Servidor)     │         Socket.IO                   │  (Cliente)       │
│  - Flask        │                                     │  - CustomTkinter │
│  - SQLite       │        TCP/IP (puerto 5000)        │  - InterPhone    │
│  - Backup       │◄─────────WebSocket─────────────────►│  Integration     │
└─────────────────┘         Socket.IO                   └──────────────────┘
                                                        
                                                         ┌──────────────────┐
                                                         │  PC Worker N     │
                                                         │  (Cliente)       │
                                                         └──────────────────┘
```

### Componentes Clave

| Componente | Responsabilidad |
|-----------|-----------------|
| **server.py** | REST API, WebSocket, Gestión de base datos, Backup automático |
| **call_manager_app.py** | UI, Manejo de eventos, Sincronización en tiempo real |
| **interphone_controller.py** | Automatización de ventanas, Marcar números |
| **config.py** | Configuración centralizada, Estados dinámicos |

---

## 📊 Base de Datos

### Modelo Contact

| Campo | Tipo | Índice | Descripción |
|-------|------|--------|------------|
| id | String | ✅ | ID único (normalizado) |
| phone | String | ✅ | Número telefónico |
| name | String | | Nombre del contacto |
| status | String | ✅ | Estado (NC, CUELGA, etc.) |
| note | Text | | Notas |
| coords | JSON | | Coordenadas |
| last_called_by | String | | Último que marcó |
| last_called_time | DateTime | | Hora última llamada |
| last_visibility_time | DateTime | ✅ | Última actualización |
| editors_history | JSON | | Historial de cambios |
| locked_by | String | ✅ | Bloqueado por usuario |
| locked_until | DateTime | ✅ | Hasta cuándo bloqueado |
| created_at | DateTime | ✅ | Fecha creación |
| updated_at | DateTime | ✅ | Última actualización |

---

## 🔒 Seguridad

### Autenticación
- Sistema de API keys configurable
- Header: `X-API-Key: <token>`
- Tokens definidos en `config.py`

### Validaciones
- Regex para teléfono: `^\+?[\d\s\-\(\)]{7,}$`
- Limites de caracteres (nombre 1-200, nota max 2000)
- Sanitización de entrada

### Base de Datos
- Prepared statements (SQLAlchemy ORM)
- Transacciones ACID
- Rollback automático en errores

### Backup
- Automático cada 30 minutos
- Retención de 7 días
- Ubicación: `/backups/contacts_backup_YYYYMMDD_HHMMSS.db`

---

## 🌍 Características Costa Rica

### Manejo de Prefijo +506
```python
# Entrada: +506-5123-4567
# Para BD: 51234567 (ID único)
# Para InterPhone: 51234567 (sin +506)
# En UI: +506-5123-4567 (51234567) - ambos formatos
```

### Detección Automática de Duplicados
```
POST /import
├─ Número nuevo → INSERT
└─ Número existe → UPDATE (merge)
   └─ Resetea last_visibility_time
```

---

## 📈 Estados y Prioridades

### Estados Automáticos
```
Estado           | Inactividad | Prioridad
─────────────────┼─────────────┼──────────
NC              | -           | 1 (MÁXIMA)
CUELGA          | -           | 2 (ALTA)
SIN_GESTIONAR   | -           | 3 (NORMAL)
INTERESADO      | -           | 4 (MEDIA)
SERVICIOS_ACTI. | -           | 10 (BAJA)
NO_EXISTE       | 3+ meses    | 20 (MUY BAJA)
SIN_RED         | 6+ meses    | 21 (MUY BAJA)
NO_CONTACTO     | 8+ meses    | 22 (MÍNIMA)
```

### Configuración
Editable en `config.py`:
```python
STATUS_AUTO_RULES = {
    'NO_EXISTE': (3, '3 meses...'),
    'SIN_RED': (6, '6 meses...'),
    'NO_CONTACTO': (8, '8 meses...'),
}

STATUS_PRIORITY = {
    'NC': 1,
    'SERVICIOS_ACTIVOS': 10,
    'NO_CONTACTO': 22,
}
```

---

## 🛠️ Desarrollo

### Instalación para Desarrollo
```bash
# Con venv
python -m venv venv
venv\Scripts\activate

# Instalar con extras
pip install -r requirements.txt
pip install pytest pylint
```

### Verificar Sintaxis
```bash
python -m py_compile server.py
python -m py_compile client/call_manager_app.py
```

### Logs
- Servidor: `callmanager.log`
- Archivo + consola
- Nivel configurable: INFO, DEBUG, WARNING, ERROR

---

## 📚 Documentación Completa

| Documento | Contenido |
|-----------|----------|
| **DEPLOYMENT.md** | 10 secciones, checklist, troubleshooting |
| **ESTADOS_DINAMICOS.md** | Sistema automático, API reference, casos de uso |
| **GUIA_RAPIDA_LUNES.md** | Paso a paso para lunes (mañana y tarde) |
| **GUIA_VISUAL_LUNES.md** | Versión visual con screenshots |
| **MEJORAS_FASE2_COSTA_RICA.md** | Cambios específicos, testing procedures |
| **MEJORAS_IMPLEMENTADAS.md** | Resumen de fase 1 |

---

## 🚀 Deployment Lunes

### Timeline
- **08:00-10:00**: Preparación (servidor, firewall, instalación)
- **09:00**: Configurar clientes (config_local.json)
- **14:00-16:00**: Testing (4 pruebas clave)
- **16:00**: Resultado final

### Checklist
- [ ] IP estática en PC servidor
- [ ] Puerto 5000 abierto en Firewall
- [ ] requirements.txt instalado
- [ ] `python server.py` ejecutándose
- [ ] Clientes con config_local.json correcto
- [ ] Test 1: Conexión - Socket.IO conectado
- [ ] Test 2: Duplicados - Excel re-importado sin errores
- [ ] Test 3: +506 - Marcar número con prefijo funciona
- [ ] Test 4: Bloqueos - Funciona entre clientes

---

## 🐛 Troubleshooting

### Servidor no inicia
```bash
# Verificar puerto 5000
netstat -ano | findstr :5000

# Si está en uso, cambiar en config.py SERVER_PORT
```

### Cliente no conecta
```bash
# Verificar config_local.json
# Asegurarse que SERVER_URL sea correcto: http://IP_SERVIDOR:5000

# Verificar firewall en servidor
# Puerto 5000 debe estar ABIERTO
```

### InterPhone no recibe números
```bash
# Verificar que InterPhone está abierto
# Verificar que pywinauto está instalado
# Revisar logs: callmanager.log
```

Ver **DEPLOYMENT.md** para troubleshooting completo.

---

## 📞 Soporte

- **Issues**: https://github.com/JorgeBC420/callmanager/issues
- **Email**: Contact author
- **Documentation**: Revisar carpeta `/docs` o archivos `.md`

---

## 📄 Licencia

Este proyecto es de uso privado para el call center.

---

## ✅ Checklist Final

- ✅ Sintaxis válida en todos los archivos
- ✅ Imports correctamente configurados
- ✅ Funciones críticas presentes
- ✅ Endpoints/callbacks funcionales
- ✅ Seguridad implementada
- ✅ Documentación completa
- ✅ Dependencias declaradas
- ✅ .gitignore configurado
- ✅ Subido a GitHub
- ✅ Listo para producción

---

**Versión**: 2.1 MVP  
**Estado**: Production Ready  
**Fecha**: Noviembre 17, 2025  
**Autor**: Jorge BC

🚀 **Listo para revolucionar tu call center**
