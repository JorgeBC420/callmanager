# CHANGELOG CallManager v3.3.1

## [3.3.1] - 2024-11-21

### ✨ Nuevas Características

#### Sistema de Autenticación Completo
- **Autenticación con Usuario/Contraseña**
  - Endpoint `POST /auth/register` - Crear nuevos usuarios
  - Endpoint `POST /auth/login` - Login y obtener JWT token
  - Endpoint `POST /auth/change-password` - Cambiar contraseña seguramente
  - Contraseñas hasheadas con bcrypt (10 rondas) - OWASP compliant
  - Passwords nunca se guardan en plaintext

- **Tokens JWT**
  - JWT tokens con 24 horas de validez
  - Firmados con HS256 (imposibles de falsificar)
  - Payload incluye user_id, username, role para autorización
  - Endpoint para verificar tokens

- **Admin Management**
  - Endpoint `GET /admin/users` - Listar todos los usuarios (TI only)
  - Endpoint `DELETE /admin/users/<id>` - Desactivar usuarios (TI only)
  - Prevención de eliminación del último admin

- **Inicialización Automática**
  - Usuario por defecto: `admin` / `1234` (creado en primer inicio)
  - Script `init_default_user.py` para crear usuario si BD está vacía
  - Aviso de seguridad para cambiar contraseña por defecto

#### Seguridad Mejorada
- **Rate Limiting en Auth**
  - /auth/register: 5 registros por minuto
  - /auth/login: 10 intentos por minuto
  - Previene brute force attacks

- **Cryptographic Key Generation**
  - API Keys generadas con `secrets.token_urlsafe(32)`
  - Imposible adivinar o reproducir
  - Cada usuario tiene su propia API Key

- **Logging de Seguridad**
  - Intentos fallidos de login registrados
  - Cambios de contraseña auditados
  - Usuarios creados/desactivados registrados

#### Documentación
- **AUTENTICACION.md** (11 KB)
  - Explicación completa del sistema
  - Ejemplos de endpoints con curl
  - Ejemplos en Python y JavaScript
  - Flujos de seguridad
  - Checklist para IT teams
  - Manejo de incidentes

- **AUTENTICACION_IMPLEMENTADA.md** (Estado técnico)
  - Componentes implementados
  - Flujos de autenticación
  - Características de seguridad
  - Instrucciones de inicio
  - Próximos pasos

### 🔧 Cambios Técnicos

#### Backend (server.py)
```python
# Línea 11-12: Nuevos imports
import bcrypt
import jwt

# Línea 16: Import para claves criptográficas
import secrets

# Línea 156-159: User model actualizado
password_hash = Column(String, nullable=False)

# Línea 248-288: Funciones criptográficas
- hash_password(password) → bcrypt hash
- verify_password(password, hash) → Boolean  
- generate_jwt_token(user_id, username, role) → JWT
- verify_jwt_token(token) → payload dict

# Línea 548-699: Endpoints de autenticación
- POST /auth/register
- POST /auth/login
- POST /auth/change-password

# Línea 1512-1572: Endpoints de admin
- GET /admin/users
- DELETE /admin/users/<id>

# Línea 1527-1535: Inicialización automática
- Auto-crea usuario admin/1234 si BD vacía
```

#### Nuevos Archivos
- `init_default_user.py` (60 líneas) - Script de inicialización
- `AUTENTICACION.md` (11 KB) - Documentación completa
- `AUTENTICACION_IMPLEMENTADA.md` - Status técnico
- `test_auth_system.py` - Pruebas del sistema
- `migrate_db.py` - Herramienta de migración

#### Dependencias Actualizadas
```
bcrypt>=4.0.0      # Password hashing (nuevo)
PyJWT>=2.8.0       # JWT tokens (nuevo)
```

### 🚀 Mejoras de Usabilidad

- Usuario por defecto creado automáticamente
- Mensajes claros sobre cambio de contraseña requerido
- Aviso de seguridad en consola
- API Key mostrada y guardada en logs

### 🛡️ Mejoras de Seguridad

- ✅ Contraseñas nunca en plaintext
- ✅ Bcrypt con 10 rondas (0.1s por hash = balanceado)
- ✅ JWT con SECRET_KEY único
- ✅ Rate limiting en endpoints críticos
- ✅ Tokens expiran (previene hijacking indefinido)
- ✅ Logging de intentos fallidos

### 📊 Compatibilidad

- ✅ Python 3.8+
- ✅ Windows / Linux / Mac
- ✅ Backwards compatible (API Key auth aún funciona)

### 🧪 Testing

- ✅ test_auth_system.py - Pruebas bcrypt, JWT, usuario BD
- ✅ Manual testing con curl
- ✅ Verificación de usuario admin automático

### 📝 Documentación Actualizada

- **README.md** - Agregar sección de autenticación
- **AUTENTICACION.md** - Nueva, completa
- **AUTENTICACION_IMPLEMENTADA.md** - Nuevo, estado técnico
- **requirements.txt** - Dependencias actualizadas

### 🐛 Fixes

- Esquema de BD ahora incluye password_hash desde creación
- Función de inicialización usa `db.close()` correcto
- Rate limiting funciona en endpoints de auth

### ⚠️ IMPORTANTE - Cambios que Requieren Acción

1. **Cambiar contraseña por defecto**
   - Usuario admin/1234 DEBE cambiar contraseña en producción
   - Usar endpoint `/auth/change-password`

2. **Migración de BD existentes**
   - BDs anteriores necesitan `password_hash` agregado
   - Script `migrate_db.py` disponible para migración
   - O simplemente borrar BD para crear nueva

3. **Actualizar clientes**
   - Próximamente: agregar login GUI al cliente
   - Actualmente: sigue usando X-API-Key

### 📅 Roadmap Próximo

- [ ] Login GUI en cliente (`call_manager_app.py`)
- [ ] Usar JWT tokens en cliente en lugar de API Keys
- [ ] Refresh token endpoint (renovar sin re-login)
- [ ] User management GUI (crear/borrar usuarios desde app)
- [ ] 2FA (autenticación de 2 factores) - opcional
- [ ] LDAP/Active Directory integration - opcional

### 🔗 Referencias

- bcrypt: https://github.com/pyca/bcrypt
- PyJWT: https://github.com/jpadilla/pyjwt
- OWASP Password Storage: https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html

---

**Versión anterior**: v3.3.0  
**Cambios totales**: 6 archivos nuevos, 2 modificados, +500 líneas  
**Status**: ✅ Listo para usar, autenticación completa
