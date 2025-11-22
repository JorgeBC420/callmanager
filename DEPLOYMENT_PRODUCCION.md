# 🚀 DEPLOYMENT CallManager v3.3.1

**Guía Completa para Desplegar en Producción**

---

## 📋 Checklist Pre-Deployment

### Seguridad
- [ ] Cambiar SECRET_KEY en .env
- [ ] Cambiar API_KEY en .env
- [ ] FLASK_ENV = production
- [ ] Verificar .env NO está en git
- [ ] Certificado SSL/TLS listo

### Código
- [ ] Todos los tests pasan
- [ ] No hay credenciales en código
- [ ] requirements.txt actualizado
- [ ] CORS configurado correctamente

### Infraestructura
- [ ] Servidor/VPS disponible
- [ ] Python 3.7+ instalado
- [ ] Puertos 80/443 abiertos
- [ ] Firewall configurado

### Database
- [ ] Backup actual realizado
- [ ] SQLite con WAL mode habilitado
- [ ] Permisos de archivo correctos

---

## 🔧 Opción 1: Desplegar en Windows (Más Común)

### Paso 1: Preparar el Servidor

```bash
# 1. Crear carpeta del proyecto
mkdir C:\CallManager
cd C:\CallManager

# 2. Descargar código
git clone https://github.com/JorgeBC420/callmanager.git .
# O descargar ZIP y extraer

# 3. Crear venv
python -m venv venv
venv\Scripts\activate

# 4. Instalar dependencias
pip install -r requirements.txt

# 5. Setup seguro
python setup_secure.py
# Esto genera:
# - .env con claves seguras
# - Valida código
# - Crea build_info.json
```

### Paso 2: Configurar .env

Editar `C:\CallManager\.env`:

```dotenv
# CAMBIAR ESTOS VALORES
FLASK_ENV=production
CALLMANAGER_SECRET_KEY=<generar-con-secrets>
CALLMANAGER_API_KEY=<generar-con-uuid>

# Otros valores
CALLMANAGER_HOST=0.0.0.0
CALLMANAGER_PORT=5000
DATABASE_PATH=./contacts.db
BACKUP_DIR=./backups
```

### Paso 3: Generar Claves Seguras

```python
# En PowerShell o Python console
import secrets
print(secrets.token_urlsafe(32))  # Para SECRET_KEY
print(secrets.token_urlsafe(32))  # Para API_KEY

# O usar UUID
import uuid
print(uuid.uuid4())
```

### Paso 4: Crear Servicio Windows (Opcional)

Crear archivo `install_service.bat`:

```batch
@echo off
REM Instalar CallManager como servicio Windows

REM Cambiar a directorio
cd /d "C:\CallManager"

REM Instalar servicio
nssm install CallManager "C:\CallManager\venv\Scripts\python.exe" "C:\CallManager\run_service.py"

REM Iniciar servicio
nssm start CallManager

echo Servicio instalado. Ver con: nssm status CallManager
pause
```

Crear `run_service.py`:

```python
#!/usr/bin/env python3
import os
os.chdir(r'C:\CallManager')

from server import app, socketio

if __name__ == '__main__':
    socketio.run(
        app,
        host='0.0.0.0',
        port=5000,
        debug=False,
        use_reloader=False
    )
```

### Paso 5: Ejecutable Actualizable

```bash
# Generar EXE
python build_executable.py

# Distribuir contenido de dist/CallManager/
# Los usuarios ejecutan install.bat
# Luego corren CallManager.exe
```

### Paso 6: Crear Tarea Programada (Backups)

En Task Scheduler de Windows:

```
Trigger: Diario a las 23:00
Action: python backup.py
Folder: C:\CallManager
```

Script `backup.py`:

```python
#!/usr/bin/env python3
import shutil
from datetime import datetime
from pathlib import Path

backup_dir = Path('backups')
backup_dir.mkdir(exist_ok=True)

timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
backup_file = backup_dir / f'contacts_{timestamp}.db'

shutil.copy('contacts.db', backup_file)
print(f"Backup created: {backup_file}")

# Limpiar backups viejos (>7 días)
import os
from datetime import timedelta
cutoff = datetime.now() - timedelta(days=7)
for file in backup_dir.glob('contacts_*.db'):
    if datetime.fromtimestamp(file.stat().st_mtime) < cutoff:
        file.unlink()
        print(f"Deleted old backup: {file}")
```

---

## 🐧 Opción 2: Desplegar en Linux (VPS/Servidor)

### Paso 1: Preparar Servidor Linux

```bash
# 1. SSH al servidor
ssh user@your-server.com

# 2. Actualizar sistema
sudo apt update && sudo apt upgrade -y

# 3. Instalar Python
sudo apt install python3.9 python3-venv python3-pip -y

# 4. Instalar dependencias del sistema
sudo apt install sqlite3 supervisor nginx -y

# 5. Crear usuario para la app
sudo useradd -m callmanager
sudo su - callmanager
```

### Paso 2: Clonar y Configurar

```bash
# Como usuario callmanager
cd ~
git clone https://github.com/JorgeBC420/callmanager.git
cd callmanager

# Crear venv
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Setup seguro
python setup_secure.py
```

### Paso 3: Editar .env

```bash
# Editar con nano o vi
nano .env
```

```dotenv
FLASK_ENV=production
CALLMANAGER_SECRET_KEY=<generar>
CALLMANAGER_API_KEY=<generar>
CALLMANAGER_HOST=127.0.0.1  # Escuchar en localhost
CALLMANAGER_PORT=5000
```

### Paso 4: Crear Servicio Systemd

```bash
# Como root
sudo tee /etc/systemd/system/callmanager.service << EOF
[Unit]
Description=CallManager Service
After=network.target

[Service]
Type=simple
User=callmanager
WorkingDirectory=/home/callmanager/callmanager
Environment="PATH=/home/callmanager/callmanager/venv/bin"
ExecStart=/home/callmanager/callmanager/venv/bin/python run_demo.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable callmanager
sudo systemctl start callmanager
```

### Paso 5: Configurar Nginx (Reverse Proxy)

```bash
# Como root
sudo tee /etc/nginx/sites-available/callmanager << 'EOF'
server {
    listen 80;
    server_name your-domain.com;

    # Redirigir a HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # Certificados SSL (Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # Configuración SSL
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Headers de seguridad
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-XSS-Protection "1; mode=block" always;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /socket.io {
        proxy_pass http://127.0.0.1:5000/socket.io;
        proxy_http_version 1.1;
        proxy_buffering off;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
EOF

# Habilitar sitio
sudo ln -s /etc/nginx/sites-available/callmanager /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default 2>/dev/null

# Recargar nginx
sudo systemctl reload nginx
```

### Paso 6: SSL con Let's Encrypt

```bash
# Instalar certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtener certificado (automatiza todo)
sudo certbot --nginx -d your-domain.com

# Auto-renovación
sudo systemctl enable certbot.timer
```

### Paso 7: Monitorar con Supervisor

```bash
# Como root
sudo tee /etc/supervisor/conf.d/callmanager.conf << EOF
[program:callmanager]
command=/home/callmanager/callmanager/venv/bin/python run_demo.py
directory=/home/callmanager/callmanager
user=callmanager
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/callmanager.log
EOF

sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl status
```

---

## 🐳 Opción 3: Docker (Recomendado para equipos grandes)

### Crear `Dockerfile`

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Instalar dependencias de sistema
RUN apt-get update && apt-get install -y \
    sqlite3 \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivos
COPY requirements.txt .
COPY . .

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Setup seguro
RUN python setup_secure.py

# Exponer puerto
EXPOSE 5000

# Comando de inicio
CMD ["python", "run_demo.py"]
```

### Crear `docker-compose.yml`

```yaml
version: '3.8'

services:
  callmanager:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./contacts.db:/app/contacts.db
      - ./backups:/app/backups
      - ./.env:/app/.env:ro
    environment:
      - FLASK_ENV=production
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### Desplegar con Docker

```bash
# Build
docker-compose build

# Run
docker-compose up -d

# Ver logs
docker-compose logs -f callmanager

# Parar
docker-compose down
```

---

## 📊 Monitoreo Post-Deployment

### Ver Estado del Servicio

**Windows (PowerShell)**:
```powershell
# Si es servicio Windows
Get-Service CallManager

# Si es proceso Python
Get-Process python | Where-Object {$_.CommandLine -like '*server*'}
```

**Linux**:
```bash
# Si es systemd
systemctl status callmanager

# Si es supervisor
supervisorctl status callmanager

# Ver logs
journalctl -u callmanager -f
tail -f /var/log/callmanager.log
```

### Verificar Conectividad

```bash
# Test del servidor
curl -X GET http://localhost:5000/health \
  -H "X-API-Key: your-api-key"

# Si da 200, está funcionando
```

### Monitorizar Recursos

```bash
# Linux: monitorear CPU, RAM
top

# Windows: Task Manager o PowerShell
Get-Process python | Select-Object CPU, Memory
```

---

## 🔄 Actualizar en Producción

### Método 1: Git Pull + Restart

```bash
# SSH al servidor
ssh user@server

# Cambiar a directorio
cd /home/callmanager/callmanager

# Parar servicio
sudo systemctl stop callmanager

# Pull cambios
git pull origin main

# Instalar nuevas dependencias (si hay)
source venv/bin/activate
pip install -r requirements.txt

# Iniciar servicio
sudo systemctl start callmanager
```

### Método 2: Auto-Update (Recomendado)

El EXE construido con `build_executable.py` puede auto-actualizar:

```python
# En el updater.py incluido en el EXE
def update_from_git():
    subprocess.run(['git', 'pull', 'origin', 'main'], check=True)
    subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], check=True)
    # Restart automático
```

---

## 🆘 Troubleshooting

### Error: "SECRET_KEY no configurada"

```
Solución: Editar .env y cambiar CALLMANAGER_SECRET_KEY
python setup_secure.py para generar nueva
```

### Error: "Port 5000 already in use"

```bash
# Linux: matar proceso
sudo lsof -i :5000
sudo kill -9 <PID>

# Windows PowerShell:
Get-Process -Id (Get-NetTCPConnection -LocalPort 5000).OwningProcess | Stop-Process -Force
```

### Base de datos corrupta

```bash
# Restaurar desde backup
cp backups/contacts_YYYYMMDD_HHMMSS.db contacts.db

# O crear nueva
rm contacts.db
python run_demo.py  # Recrea automáticamente
```

### Servicio no inicia

```bash
# Ver error detallado
python run_demo.py  # Ejecutar manualmente para ver error

# Verificar logs
journalctl -u callmanager -n 50  # Últimas 50 líneas
```

---

## 📈 Performance Tuning

### Gunicorn (Producción Linux)

```bash
# En lugar de: python run_demo.py
# Usar: gunicorn con múltiples workers

gunicorn --workers 4 \
         --worker-class eventlet \
         --bind 0.0.0.0:5000 \
         --access-logfile - \
         --error-logfile - \
         server:app
```

### Configuración para Alta Carga

```python
# En config.py
SQLALCHEMY_POOL_SIZE = 20        # Conexiones a DB
SQLALCHEMY_POOL_RECYCLE = 3600   # Reciclar cada hora
SQLALCHEMY_ECHO = False          # No loguear SQL
```

---

## 🔒 Seguridad en Producción

### Firewall

```bash
# Abrir solo puertos necesarios
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable
```

### Backup Automático

```bash
# Cron Linux: Backup diario a las 2 AM
0 2 * * * /home/callmanager/callmanager/venv/bin/python /home/callmanager/callmanager/backup.py

# O Windows Task Scheduler: Mismo backup.py cada día
```

### Monitoreo de Logs

```bash
# Buscar intentos fallidos
grep "Unauthorized\|WARNING" callmanager.log

# Alerts (si WARN = intento fallido)
grep "WARNING" callmanager.log | mail -s "CallManager Alert" admin@company.com
```

---

## 📝 Checklist de Post-Deployment

- [ ] Servicio iniciado correctamente
- [ ] Se puede acceder a la app
- [ ] Autenticación funciona (API Key)
- [ ] Importar/Exportar Excel funciona
- [ ] Generador de contactos funciona
- [ ] Backups se crean automáticamente
- [ ] Logs se escriben correctamente
- [ ] HTTPS funciona (si Linux)
- [ ] Rate limiting activo
- [ ] Roles y permisos funcionales

---

**Versión**: CallManager v3.3.1  
**Última actualización**: Noviembre 2024  
**Soporte**: Envía issues a GitHub o contacta al equipo
