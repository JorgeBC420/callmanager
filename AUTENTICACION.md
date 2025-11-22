# 🔐 AUTENTICACIÓN CallManager v3.3.1

**Sistema de Login + Contraseña + API Key**

---

## 📋 Resumen

CallManager implementa **autenticación de 2 niveles**:

1. **Usuarios con Contraseña** (login/password)
   - Usuario/contraseña para login humano
   - JWT token para mantener sesión
   - Permite cambiar contraseña

2. **API Key** (para integraciones)
   - Token para automatizaciones
   - No expira
   - Cada usuario tiene su propia API Key

---

## 👤 Usuarios por Defecto

Cuando se crea la base de datos por primera vez, se crea automáticamente:

```
Username: admin
Password: 1234
Role: TI (Admin)
```

**⚠️ IMPORTANTE**: Cambiar esta contraseña inmediatamente en producción.

---

## 🔑 Endpoints de Autenticación

### 1. Registrar Usuario

```bash
POST /auth/register
Content-Type: application/json

{
  "username": "agente1",
  "password": "mi_contraseña_segura",
  "role": "Agent",
  "team_name": "Equipo Ventas"
}
```

**Response** (201):
```json
{
  "success": true,
  "user_id": "user_agente1_1234567890",
  "username": "agente1",
  "role": "Agent",
  "api_key": "abcd1234efgh5678...",
  "message": "Usuario creado exitosamente. Guarda tu API Key en lugar seguro."
}
```

**Validaciones**:
- ✅ Username: mínimo 3 caracteres
- ✅ Password: mínimo 4 caracteres
- ✅ Role: Agent, TeamLead, ProjectManager o TI
- ✅ No permite duplicar usernames

**Rate Limit**: 5 registros por minuto

---

### 2. Login de Usuario

```bash
POST /auth/login
Content-Type: application/json

{
  "username": "agente1",
  "password": "mi_contraseña_segura"
}
```

**Response** (200):
```json
{
  "success": true,
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "user_agente1_1234567890",
    "username": "agente1",
    "role": "Agent",
    "team_name": "Equipo Ventas"
  }
}
```

**Errores**:
- 400: Username y password requeridos
- 401: Usuario o contraseña incorrectos
- 401: Usuario inactivo/desactivado

**Rate Limit**: 10 intentos por minuto

**Token válido por**: 24 horas

---

### 3. Cambiar Contraseña

```bash
POST /auth/change-password
Content-Type: application/json
X-API-Key: tu_api_key_valida

{
  "old_password": "contraseña_actual",
  "new_password": "nueva_contraseña",
  "confirm_password": "nueva_contraseña"
}
```

**Response** (200):
```json
{
  "success": true,
  "message": "Contraseña actualizada exitosamente"
}
```

**Validaciones**:
- ✅ old_password debe ser correcta
- ✅ new_password: mínimo 4 caracteres
- ✅ new_password === confirm_password

**Errors**:
- 400: Campos requeridos
- 401: Contraseña actual incorrecta
- 400: Contraseñas no coinciden

---

### 4. Listar Usuarios (Solo TI)

```bash
GET /admin/users
X-API-Key: tu_api_key_admin

```

**Response** (200):
```json
[
  {
    "id": "user_admin_default",
    "username": "admin",
    "role": "TI",
    "team_name": "Administración",
    "email": null,
    "last_login": "2024-11-21T15:30:45.123456",
    "created_at": "2024-11-21T14:00:00.000000"
  },
  {
    "id": "user_agente1_1234567890",
    "username": "agente1",
    "role": "Agent",
    "team_name": "Equipo Ventas",
    "email": null,
    "last_login": "2024-11-21T16:45:30.654321",
    "created_at": "2024-11-21T14:15:00.000000"
  }
]
```

**Permiso**: Solo TI

---

### 5. Desactivar Usuario (Solo TI)

```bash
DELETE /admin/users/<user_id>
X-API-Key: tu_api_key_admin

```

**Response** (200):
```json
{
  "success": true,
  "message": "Usuario agente1 desactivado"
}
```

**Validaciones**:
- ✅ No permite borrar el último admin
- ✅ Solo marca como inactivo (no elimina)

**Permiso**: Solo TI

---

## 🛡️ Seguridad de Contraseñas

### Hash bcrypt

```python
# Las contraseñas se hashean con bcrypt (10 rondas)
# No se almacenan en texto plano
# Imposible recuperar la contraseña original

password = "1234"
password_hash = hash_password(password)
# Resultado: $2b$10$...48 caracteres...

# Verificar:
if verify_password("1234", password_hash):
    print("✅ Contraseña correcta")
```

### Validación

```python
def validate_password_strength(password: str) -> bool:
    """
    Requisitos mínimos:
    - Mínimo 4 caracteres (se puede aumentar en producción)
    - Recomendado: 8+ caracteres
    - Recomendado: Incluir números, mayúsculas, símbolos
    """
```

---

## 🎫 JWT Token

### Estructura

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.
eyJ1c2VyX2lkIjoiMTIzIiwidXNlcm5hbWUiOiJhZ2VudGUxIiwicm9sZSI6IkFnZW50In0.
TJVA95OrM7E2cBab30RMHrHDcEfxjoYZgeFONFh7HgQ

┌─────────────────────────────────────────────────┐
│ Header | Payload | Signature                     │
└─────────────────────────────────────────────────┘

Header:
{
  "alg": "HS256",
  "typ": "JWT"
}

Payload:
{
  "user_id": "user_agente1_1234567890",
  "username": "agente1",
  "role": "Agent",
  "iat": 1700598000,  # Issued at
  "exp": 1700684400   # Expiration (24 horas después)
}

Signature:
  HMAC(SECRET_KEY, header.payload)
```

### Cómo Usar

**Opción 1: Header X-API-Key** (Para integraciones):
```bash
curl -H "X-API-Key: abc123def456..." http://localhost:5000/contacts
```

**Opción 2: JWT Token** (Para usuarios):
```bash
curl -H "Authorization: Bearer eyJhbGciOiJIUzI1NiI..." http://localhost:5000/contacts
```

---

## 👥 Roles y Permisos

| Rol | Lectura | Crear | Actualizar | Borrar | Admin |
|-----|---------|-------|-----------|--------|-------|
| Agent | ✅ | ✅ | ✅ | ❌ | ❌ |
| TeamLead | ✅ | ✅ | ✅ | ❌ | ❌ |
| ProjectManager | ✅ | ✅ | ✅ | ✅ | ❌ |
| TI | ✅ | ✅ | ✅ | ✅ | ✅ |

**Admin (TI) puede**:
- Crear/borrar usuarios
- Cambiar roles de usuarios
- Ver todos los usuarios
- Desactivar usuarios
- Ver logs de seguridad

---

## 🔄 Flujo de Login Recomendado

### 1. Usuario se Registra

```bash
POST /auth/register
{
  "username": "juan",
  "password": "MiPass123!",
  "role": "Agent",
  "team_name": "Equipo Ventas"
}
```

Admin/IT guarda la **API Key** en lugar seguro.

### 2. Usuario Hace Login

```bash
POST /auth/login
{
  "username": "juan",
  "password": "MiPass123!"
}
```

Recibe **JWT token** válido por 24 horas.

### 3. Usar JWT Token

```bash
GET /contacts
Authorization: Bearer <jwt_token>
```

O para integraciones, usar API Key:

```bash
GET /contacts
X-API-Key: <api_key_guardada>
```

### 4. Cambiar Contraseña (Anual)

```bash
POST /auth/change-password
X-API-Key: <api_key>
{
  "old_password": "MiPass123!",
  "new_password": "MiNuevaPass456!",
  "confirm_password": "MiNuevaPass456!"
}
```

---

## 🚨 Casos de Seguridad

### Contraseña Débil

```bash
POST /auth/register
{
  "username": "agente2",
  "password": "123"  # ❌ Muy corta
}

Response (400):
{
  "error": "Password debe tener mínimo 4 caracteres"
}
```

### Intento de Login Fallido

```bash
POST /auth/login
{
  "username": "agente1",
  "password": "wrong_password"
}

Response (401):
{
  "error": "Usuario o contraseña incorrectos"
}

Log:
WARN: Failed login attempt for user: agente1
```

### Token Expirado

```bash
GET /contacts
Authorization: Bearer <token_expirado>

Response (401):
{
  "error": "Token expired"
}

Solución:
→ Hacer login nuevamente
→ Obtener nuevo token
```

---

## 📝 Checklist de Seguridad para IT

### Antes de Producción

- [ ] Cambiar contraseña de admin (de "1234" a algo seguro)
- [ ] Crear usuarios en cada rol necesario
- [ ] Cada usuario tiene su propia contraseña (no compartida)
- [ ] API Keys guardadas en lugar seguro (NOT en código)
- [ ] JWT_SECRET en .env, distinto en producción
- [ ] HTTPS/SSL habilitado
- [ ] Firewall solo permite puerto 443 (HTTPS)
- [ ] Logs monitoreados para intentos fallidos

### Monitoring

```bash
# Ver intentos fallidos de login
grep "Failed login attempt" callmanager.log

# Ver logins exitosos
grep "User logged in" callmanager.log

# Ver cambios de contraseña
grep "Password changed" callmanager.log

# Ver usuarios creados
grep "New user registered" callmanager.log
```

### Incidente de Seguridad

Si sospechas que una contraseña fue comprometida:

```bash
# 1. Desactivar usuario
DELETE /admin/users/<user_id>
X-API-Key: admin_key

# 2. El usuario debe registrarse nuevamente
# 3. Generar nueva contraseña y API Key

# 4. Revisar logs para actividades sospechosas
tail -200 callmanager.log | grep "user_comprometido"
```

---

## 🔗 Flujo HTTP Completo

```
┌─────────────────────────────────────────────────┐
│ Cliente                                          │
└────────────────────┬────────────────────────────┘
                     │
                     │ POST /auth/register
                     │ (usuario/contraseña)
                     ▼
        ┌────────────────────────────┐
        │ Validar username/password   │
        │ Hash password con bcrypt    │
        │ Generar API Key             │
        │ Guardar en BD               │
        └────────────────┬─────────────┘
                         │
                         │ Response: user_id, api_key
                         ▼
                    Guardar API Key
                         │
                         │ POST /auth/login
                         │ (username/password)
                         ▼
        ┌────────────────────────────┐
        │ Buscar usuario              │
        │ Verificar password          │
        │ Generar JWT token           │
        │ Actualizar last_login       │
        └────────────────┬─────────────┘
                         │
                         │ Response: jwt_token
                         ▼
                    Guardar JWT token
                         │
                         │ GET /contacts
                         │ Authorization: Bearer <token>
                         ▼
        ┌────────────────────────────┐
        │ Verificar JWT token válido  │
        │ Extraer user_id, role       │
        │ Ejecutar operación          │
        │ Aplicar RBAC                │
        └────────────────┬─────────────┘
                         │
                         │ Response: datos según rol
                         ▼
                    Procesar respuesta
```

---

## 📚 Ejemplos de Código

### Python - Registrar Usuario

```python
import requests

response = requests.post(
    'http://localhost:5000/auth/register',
    json={
        'username': 'agente1',
        'password': 'MiContraseña123!',
        'role': 'Agent',
        'team_name': 'Ventas'
    }
)

data = response.json()
if response.status_code == 201:
    api_key = data['api_key']
    print(f"✅ Usuario creado. API Key: {api_key}")
else:
    print(f"❌ Error: {data['error']}")
```

### Python - Login

```python
response = requests.post(
    'http://localhost:5000/auth/login',
    json={
        'username': 'agente1',
        'password': 'MiContraseña123!'
    }
)

data = response.json()
if response.status_code == 200:
    token = data['token']
    # Usar token para futuras requests
else:
    print("❌ Login fallido")
```

### Python - Usar API

```python
headers = {
    'Authorization': f'Bearer {token}',
    # O: 'X-API-Key': api_key
}

response = requests.get(
    'http://localhost:5000/contacts',
    headers=headers
)

contacts = response.json()
```

### JavaScript / Node.js

```javascript
// Registrar
const register = async () => {
  const res = await fetch('http://localhost:5000/auth/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      username: 'agente1',
      password: 'MiContraseña123!',
      role: 'Agent'
    })
  });
  const data = await res.json();
  localStorage.setItem('api_key', data.api_key);
};

// Login
const login = async () => {
  const res = await fetch('http://localhost:5000/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      username: 'agente1',
      password: 'MiContraseña123!'
    })
  });
  const data = await res.json();
  localStorage.setItem('token', data.token);
};

// Usar API
const getContacts = async () => {
  const token = localStorage.getItem('token');
  const res = await fetch('http://localhost:5000/contacts', {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  return res.json();
};
```

---

**Versión**: CallManager v3.3.1  
**Fecha**: Noviembre 2024  
**Status**: Autenticación Completa ✅
