# 🚀 GUÍA RÁPIDA - Sistema de Autenticación CallManager v3.3.1

## ⚡ Inicio en 30 segundos

### 1️⃣ Instalar (una sola vez)
```bash
pip install -r requirements.txt
```

### 2️⃣ Iniciar Servidor
```bash
python server.py
```

**Resultado esperado:**
```
✅ CallManager Server Starting
✅ Host: 127.0.0.1:5000
✅ Database: ./contacts.db
✅ Usuario por defecto creado: admin / 1234
```

### 3️⃣ Login Inicial (en otra ventana)
```bash
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"1234"}'
```

**Respuesta:**
```json
{
  "success": true,
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "user_admin_default",
    "username": "admin",
    "role": "TI"
  }
}
```

### 4️⃣ Cambiar Contraseña (CRÍTICO)
```bash
# Primero, obtén tu API Key del servidor
# Se muestra cuando creas el usuario o en la consola del servidor

curl -X POST http://localhost:5000/auth/change-password \
  -H "X-API-Key: tu_api_key_aqui" \
  -H "Content-Type: application/json" \
  -d '{
    "old_password": "1234",
    "new_password": "MiContraseña_Segura_2024!",
    "confirm_password": "MiContraseña_Segura_2024!"
  }'
```

---

## 🔑 Usando JWT Token

### Método 1: Con Token JWT (para usuarios)
```bash
# 1. Login
TOKEN=$(curl -s -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"1234"}' | jq -r '.token')

# 2. Usar token
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/contacts
```

### Método 2: Con API Key (para integraciones)
```bash
curl -H "X-API-Key: tu_api_key" \
  http://localhost:5000/contacts
```

---

## 👤 Crear Nuevos Usuarios

### Registrar Usuario
```bash
curl -X POST http://localhost:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "agente1",
    "password": "ClaveSegura123",
    "role": "Agent",
    "team_name": "Equipo Ventas"
  }'
```

**Respuesta:**
```json
{
  "success": true,
  "user_id": "user_agente1_1234567890",
  "username": "agente1",
  "role": "Agent",
  "api_key": "abcd1234efgh5678ijkl9012mnop3456",
  "message": "Usuario creado exitosamente"
}
```

**Guardar la API Key** en lugar seguro (no se muestra de nuevo).

---

## 📋 Roles Disponibles

```
Agent         → Ver/editar solo sus contactos
TeamLead      → Gestionar equipo
ProjectManager→ CRUD completo + borrar
TI            → Admin total (crear/borrar usuarios)
```

---

## 🔒 Checklist de Seguridad

### Antes de usar en Producción

- [ ] Cambiar contraseña de admin (de "1234")
- [ ] Crear usuarios en roles necesarios
- [ ] Guardar API Keys en lugar seguro (NOT en código)
- [ ] JWT_SECRET única en .env
- [ ] Habilitar HTTPS/SSL
- [ ] Firewall solo puerto 443
- [ ] Cambiar permisos de BD (chmod 600 contacts.db)
- [ ] Backup diario automático (ya configurado)
- [ ] Monitorear logs de intentos fallidos

---

## 🆘 Problemas Comunes

### ❌ "Usuario o contraseña incorrectos"
```bash
# Verifica que el usuario existe y contraseña es correcta
# Por defecto: admin / 1234
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"1234"}'
```

### ❌ "Token expirado"
```bash
# JWT token expira en 24 horas
# Solución: hacer login nuevamente
curl -X POST http://localhost:5000/auth/login ...
```

### ❌ "Rate limit exceeded"
```bash
# Máximo 10 intentos de login por minuto
# Espera 60 segundos y reintenta
```

### ❌ "Campo requerido"
```bash
# Asegúrate de enviar todos los campos:
# - POST /auth/register: username, password, role, team_name
# - POST /auth/login: username, password
# - POST /auth/change-password: old_password, new_password, confirm_password
```

---

## 📚 Documentación Completa

```
AUTENTICACION.md              → Explicación detallada
AUTENTICACION_IMPLEMENTADA.md → Status técnico
CHANGELOG_V3_3_1.md          → Cambios de esta versión
README.md                     → Guía general
```

---

## ⚙️ Configuración Avanzada (Opcional)

### 1. Cambiar Token Expiration
En `server.py`, línea 270:
```python
exp = datetime.utcnow() + timedelta(hours=24)  # ← Cambiar aquí
```

### 2. Cambiar Bcrypt Rounds
En `server.py`, línea 250:
```python
hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=10))  # ← Cambiar aquí
```

### 3. Agregar HTTPS
```bash
# Generar certificado auto-firmado
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365

# En server.py línea ~1600:
app.run(ssl_context=('cert.pem', 'key.pem'), ...)
```

---

## 🎯 Próximos Pasos

1. **Cambiar contraseña** (CRÍTICO)
2. **Crear usuarios** según roles
3. **Instalar cliente** y hacer login desde GUI
4. **Revisar logs** para auditoría
5. **Hacer backup** de BD regularmente

---

## 📞 Soporte

Para preguntas o problemas, revisar:
- AUTENTICACION.md (completa)
- server.py líneas 548-699 (endpoints)
- Logs en consola (detallados)

---

**¡Sistema listo para usar!** ✅

Recuerda: **Cambia la contraseña de admin inmediatamente en producción.**
