# CallManager - Gestor de Llamadas Multiusuario

##  Descripción

CallManager es una aplicación cliente-servidor construida en Python para gestionar contactos y coordinar llamadas en tiempo real entre múltiples usuarios en una red local.

**Características principales:**
-  Servidor centralizado con Flask + Socket.IO
-  Base de datos SQLite con soporte multiusuario
-  Cliente GUI con CustomTkinter
-  Integración InterPhone para automatización de llamadas
-  Sistema de bloqueo para prevenir ediciones simultáneas
-  Historial de cambios y auditoría
-  Backup automático cada 30 minutos
-  Autenticación con API keys
-  Logging detallado

---

##  Instalación Rápida

### Requisitos
- Python 3.8+
- Windows (para InterPhone)
- InterPhone instalado (opcional)

### Paso 1: Instalar Dependencias
```
pip install -r requirements.txt
```

### Paso 2: Configurar URL del Servidor
Edita client/config_local.json (cópialo de config_local.example.json):
```json
{
  "SERVER_URL": "http://192.168.1.100:5000",
  "API_KEY": "dev-key-change-in-production"
}
```

### Paso 3: Ejecutar Servidor (PC central)
```bash
python server.py
```

**Primer inicio**: Se crea automáticamente el usuario:
- Usuario: `admin`
- Contraseña: `1234`
- ⚠️ Cambiar contraseña inmediatamente en producción

### Paso 4: Ejecutar Cliente (cada PC)
```bash
cd client
python call_manager_app.py
```

---

## 🔐 Autenticación (v3.3.1+)

CallManager ahora incluye un **sistema de autenticación de 2 niveles**:

### 1. **Login de Usuario** (para humanos)
```bash
POST /auth/login
{
  "username": "agente1",
  "password": "contraseña"
}
```

Devuelve JWT token válido por 24 horas.

### 2. **API Keys** (para integraciones)
Se genera automáticamente al crear usuario.
Usar en header: `X-API-Key: tu_api_key`

### Características de Seguridad
- ✅ Contraseñas hasheadas con bcrypt
- ✅ JWT tokens con 24h expiration
- ✅ Rate limiting en endpoints críticos
- ✅ Rate limit: 10 intentos/min en login
- ✅ Role-Based Access Control (RBAC)

### Cambiar Contraseña
```bash
POST /auth/change-password
X-API-Key: tu_api_key

{
  "old_password": "contraseña_actual",
  "new_password": "nueva_contraseña",
  "confirm_password": "nueva_contraseña"
}
```

📖 **Documentación completa**: Ver `AUTENTICACION.md`

---

##  Estructura

```
callmanager/
 server.py                       # Servidor central
 config.py                       # Configuración centralizada
 requirements.txt                # Dependencias
 README.md                       # Este archivo
 DEPLOYMENT.md                   # Guía de deployment
 callmanager.log                 # Logs
 contacts.db                     # Base de datos
 backups/                        # Backups automáticos
 client/
     call_manager_app.py         # Cliente GUI
     config_loader.py            # Cargador de config
     interphone_controller.py    # Control de InterPhone
     config_local.json           # Config local (crear)
     config_local.example.json   # Plantilla
```

---

##  Configuración

### Servidor (config.py)
- **ENABLE_AUTH**: True para requerir API keys
- **SERVER_HOST/PORT**: 0.0.0.0:5000 por defecto
- **BACKUP_INTERVAL_MINUTES**: 30 por defecto
- **AUTH_TOKENS**: Diccionario de llaves permitidas

### Cliente (config_local.json)
```json
{
  "SERVER_URL": "http://192.168.1.100:5000",
  "API_KEY": "tu-clave-aqui"
}
```

O variables de entorno:
```powershell
\ = "http://192.168.1.100:5000"
\ = "tu-clave"
```

---

##  APIs

### GET /contacts
Obtener todos los contactos
```bash
curl -H "X-API-Key: dev-key" http://localhost:5000/contacts
```

### POST /import
Importar contactos en lote
```bash
curl -X POST -H "X-API-Key: dev-key" -d '[{"phone":"555123456","name":"Juan"}]' http://localhost:5000/import
```

---

##  Backups

Backups automáticos en ackups/ cada 30 minutos. Restaurar:
```bash
copy backups\contacts_backup_20250115_100000.db contacts.db
```

---

##  Empaquetado a .exe

```bash
pip install pyinstaller
cd client
pyinstaller --noconfirm --onefile --windowed --name CallManager call_manager_app.py
```

El .exe estará en client/dist/CallManager.exe

---

##  Troubleshooting

**No se conecta:**
- Verificar que servidor está activo: ping 192.168.1.100
- Verificar puerto: 
etstat -ano | findstr :5000

**InterPhone no se detecta:**
- Confirmar que InterPhone está abierto
- Revisar logs: Get-Content callmanager.log -Tail 50

**Puerto 5000 ocupado:**
- Cambiar en config.py: SERVER_PORT = 5001

---

##  Checklist Producción

- [ ] IP estática del servidor
- [ ] Puerto 5000 abierto en Firewall
- [ ] API keys configuradas
- [ ] Backup automático funcionando
- [ ] Testear en 2+ PCs
- [ ] Revisar DEPLOYMENT.md

---

**Última actualización:** 2025-01-15  
**Versión:** 1.0
