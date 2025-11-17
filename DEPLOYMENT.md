# 📋 Guía de Deployment - CallManager

## 1. Configuración del Servidor (PC Central)

### 1.1 Asignar IP Estática
- Abre **Windows Settings** → **Network & Internet** → **WiFi (o Ethernet)**
- Click en la conexión activa
- Scroll a **IP settings** → **Edit**
- Cambia a **Manual** y activa **IPv4**
- Asigna una IP fija (ej: `192.168.1.100`)
- Guarda los cambios

### 1.2 Abrir Puerto 5000 en Firewall
**Opción A: GUI (Windows Defender Firewall)**
- Abre **Windows Defender Firewall** → **Advanced Settings**
- Click **Inbound Rules** → **New Rule**
- Selecciona **Port** → **TCP** → **Specific local ports: 5000**
- Acción: **Allow**
- Profile: marcar todas las casillas
- Nombre: `CallManager Server`

**Opción B: PowerShell (como Admin)**
```powershell
netsh advfirewall firewall add rule name="CallManager Server" dir=in action=allow protocol=tcp localport=5000
```

### 1.3 Verificar Conexión
Desde otra PC:
```powershell
ping 192.168.1.100
```
Si funciona, el servidor está accesible.

### 1.4 Instalar Dependencias y Ejecutar Servidor
```powershell
cd C:\Users\<tu_usuario>\OneDrive\Desktop\callmanager
python -m pip install -r requirements.txt
python server.py
```

El servidor debe mostrar:
```
============================================================
Starting CallManager Server
Host: 0.0.0.0:5000
Database: contacts.db
Backups: backups
Auth enabled: True
============================================================
```

---

## 2. Configuración del Cliente (.exe)

### 2.1 Cambiar URL del Servidor
**Opción A: Variable de Entorno**
```powershell
# En la PC cliente, antes de ejecutar:
$env:CALLMANAGER_SERVER_URL = "http://192.168.1.100:5000"
cd C:\path\to\client
python call_manager_app.py
```

**Opción B: Archivo de Configuración**
- Crea `config_local.json` en la carpeta `client/`:
```json
{
  "SERVER_URL": "http://192.168.1.100:5000",
  "API_KEY": "dev-key-change-in-production"
}
```

### 2.2 Testear Cliente
```powershell
cd client
python call_manager_app.py
```

Verifica que:
- [ ] Se conecte al servidor sin errores
- [ ] Se carguen los contactos
- [ ] El botón "Refrescar" funcione

---

## 3. Integración InterPhone

### 3.1 Verificar Instalación de InterPhone
- InterPhone debe estar instalado en `%LOCALAPPDATA%\InterPhone\`
- Confirma el título exacto de la ventana: **"InterPhone - XXX"**

### 3.2 Testear Integración
1. Abre InterPhone
2. En el cliente CallManager, haz click en **"Llamar"** para un contacto
3. Verifica que el número se ingrese automáticamente

### 3.3 Troubleshooting
Si falla:
- [ ] Confirma que InterPhone está abierto
- [ ] Verifica el título de la ventana con `Get-Process` en PowerShell
- [ ] Revisa los logs en `callmanager.log`

---

## 4. Backup Automático

El servidor crea backups automáticos en la carpeta `backups/`:
- Cada 30 minutos (configurable en `config.py`)
- Mantiene los últimos 7 días (configurable)
- Nombre: `contacts_backup_YYYYMMDD_HHMMSS.db`

**Restaurar desde backup:**
```powershell
# Detener servidor
# Copiar backup a contacts.db
Copy-Item 'backups\contacts_backup_20250115_120000.db' 'contacts.db'
# Reiniciar servidor
```

---

## 5. Autenticación

### 5.1 Habilitar/Deshabilitar
En `config.py`:
```python
ENABLE_AUTH = True  # o False para deshabilitar
```

### 5.2 Agregar API Keys
En `config.py`:
```python
AUTH_TOKENS = {
    'dev-key-change-in-production': 'Desarrollador',
    'tu-nueva-key-1': 'Usuario 1',
    'tu-nueva-key-2': 'Usuario 2',
}
```

### 5.3 Usar API Key en Cliente
```python
headers = {'X-API-Key': 'tu-nueva-key-1'}
requests.get('http://192.168.1.100:5000/contacts', headers=headers)
```

---

## 6. Empaquetado a .exe

### 6.1 Instalar PyInstaller
```powershell
pip install pyinstaller
```

### 6.2 Crear Ejecutable
```powershell
cd client
pyinstaller --noconfirm --onefile --windowed `
  --name CallManager `
  --icon=icon.ico `
  call_manager_app.py
```

El .exe estará en `client\dist\CallManager.exe`

### 6.3 Distribuir
- Copia `CallManager.exe` a otra PC
- Copia `config_local.json` (si usas configuración local)
- El usuario solo necesita ejecutar `CallManager.exe`

---

## 7. 🚨 Checklist Crítico Antes de Producción

### Servidor
- [ ] IP estática asignada (ej: 192.168.1.100)
- [ ] Puerto 5000 abierto en Firewall
- [ ] Testear acceso desde otra PC (`ping` y navegador)
- [ ] Crear backup inicial (automático)
- [ ] Revisar logs en `callmanager.log`
- [ ] Base de datos `contacts.db` creada
- [ ] Variables de entorno configuradas (si aplica)

### Cliente
- [ ] SERVER_URL actualizada a IP del servidor
- [ ] InterPhone abierto durante pruebas
- [ ] Botón "Llamada" funciona correctamente
- [ ] Import de Excel probado con datos reales
- [ ] Comunicación Socket.IO funciona (sin errores en consola)

### Integración
- [ ] Título de ventana de InterPhone confirmado
- [ ] pywinauto instalado y funcionando
- [ ] Manejo de errores si InterPhone se cierra
- [ ] Probado en al menos 2 PCs diferentes

---

## 8. Riesgos Identificados y Mitigación

| Riesgo | Impacto | Mitigación |
|--------|--------|-----------|
| SQLite no soporta escrituras concurrentes extremas | Si >60 usuarios activos simultáneamente | Migrar a PostgreSQL |
| pywinauto sensible a cambios de UI | InterPhone actualiza interfaz | Implementar reintentos y fallback manual |
| Sin autenticación | Acceso no autorizado desde red | Habilitar AUTH_TOKENS en config.py |
| Port forwarding accidental | Exposición a internet | Usar VPN o firewall perimetral |
| Backup incompleto | Pérdida de datos | Probar restauración regularmente |

---

## 9. Troubleshooting

### El cliente no se conecta
```bash
# Verificar conectividad
ping 192.168.1.100
curl http://192.168.1.100:5000/contacts -H "X-API-Key: dev-key-change-in-production"
```

### Puerto 5000 ya está en uso
```powershell
Get-Process -Id (Get-NetTCPConnection -LocalPort 5000).OwningProcess
```
Cambia el puerto en `config.py`:
```python
SERVER_PORT = 5001
```

### Logs no se crean
```powershell
# Verificar permisos en carpeta
icacls C:\Users\bjorg\OneDrive\Desktop\callmanager
# Asegúrate de tener permisos de escritura
```

---

## 10. Monitoreo y Mantenimiento

### Revisar logs regularmente
```powershell
Get-Content callmanager.log -Tail 100
```

### Verificar tamaño de base de datos
```powershell
(Get-Item contacts.db).Length / 1MB
```

### Monitoreo de CPU/Memoria
```powershell
Get-Process python | Select-Object Name, CPU, Memory
```

---

**Última actualización**: 2025-11-15  
**Versión**: 1.0
