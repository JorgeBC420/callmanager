# ✅ CHECKLIST DE VERIFICACIÓN POST-AUDITORÍA
**Use este documento para verificar que todo está funcionando correctamente**

---

## 🚀 ANTES DE EMPEZAR - SETUP INICIAL

- [ ] Navega a la carpeta del proyecto
- [ ] Verifica que Python 3.7+ está instalado: `python --version`
- [ ] Verifica que pip está disponible: `pip --version`
- [ ] Instala dependencias: `pip install -r requirements.txt`

---

## 📝 PASO 1: VALIDAR CÓDIGO

```powershell
# Compilar archivos para verificar errores de syntax
python -m py_compile server.py
python -m py_compile client/call_manager_app.py
python -m py_compile run_demo.py
python -m py_compile demo_contacts.py
python -m py_compile init_users.py
python -m py_compile test_roles.py
```

**Resultado esperado:** Sin errores de compilación

- [ ] ✅ server.py compila
- [ ] ✅ call_manager_app.py compila
- [ ] ✅ run_demo.py compila
- [ ] ✅ demo_contacts.py compila
- [ ] ✅ init_users.py compila
- [ ] ✅ test_roles.py compila

---

## 🗄️ PASO 2: INICIALIZAR BASE DE DATOS

```powershell
# Generar contactos de prueba (demo_contacts.py)
python demo_contacts.py
```

**Esperado:**
- [ ] ✅ Archivo `demo_contacts.json` creado
- [ ] ✅ Archivo `demo_contacts.csv` creado

```powershell
# Inicializar usuarios de prueba
python init_users.py
```

**Esperado:**
- [ ] ✅ Mensaje "✅ Database initialized"
- [ ] ✅ Archivo `contacts.db` creado
- [ ] ✅ Tabla `contact` creada
- [ ] ✅ Tabla `user` creada
- [ ] ✅ Tabla `user_metrics` creada
- [ ] ✅ 7 usuarios de prueba creados
- [ ] ✅ 15 contactos de prueba importados
- [ ] ✅ Keys de API mostradas en consola

**Guarda las API keys mostradas** para los tests posteriores.

---

## 🖥️ PASO 3: INICIAR SERVIDOR

**Terminal 1:**
```powershell
cd c:/Users/bjorg/OneDrive/Desktop/callmanager
python run_demo.py
```

**Esperado en consola:**
- [ ] ✅ "CALLMANAGER - MODO DEMO LOCAL"
- [ ] ✅ "✅ Contactos generados"
- [ ] ✅ "Iniciando servidor..."
- [ ] ✅ "Socket.IO: EventletAsync" o similar
- [ ] ✅ "Running on http://0.0.0.0:5000"
- [ ] ✅ Sin errores de excepción

**No cierres esta terminal - el servidor debe seguir corriendo**

---

## 🎨 PASO 4: INICIAR CLIENTE GUI

**Terminal 2 (NUEVA):**
```powershell
cd c:/Users/bjorg/OneDrive/Desktop/callmanager/client
python call_manager_app.py
```

**Esperado:**
- [ ] ✅ Se abre ventana GUI con título "Call Manager - Gestor de Llamadas"
- [ ] ✅ Muestra botones: 📥 Importar, 🔄 Refrescar, ℹ️ Estado
- [ ] ✅ Muestra "Cargando contactos..."
- [ ] ✅ En consola: "Attempting to connect to http://127.0.0.1:5000"
- [ ] ✅ En consola: "Connected to server" (en ~2 segundos)

---

## 📥 PASO 5: IMPORTAR CONTACTOS EN GUI

1. En la ventana GUI, haz clic en **📥 Importar Excel**
2. Navega a: `../demo_contacts.csv`
3. Selecciona el archivo y confirma

**Esperado:**
- [ ] ✅ Mensaje: "Importación completada"
- [ ] ✅ Muestra: "Insertados: 15, Actualizados: 0"
- [ ] ✅ Ahora la lista muestra 15 contactos
- [ ] ✅ Cada contacto muestra: nombre, teléfono, estado

---

## 🔄 PASO 6: PROBAR FUNCIONALIDAD GUI

### Test 1: Refrescar Contactos
- [ ] ✅ Haz clic en **🔄 Refrescar**
- [ ] ✅ Contactos se recargan sin errores

### Test 2: Ver Estado
- [ ] ✅ Haz clic en **ℹ️ Estado**
- [ ] ✅ Muestra información del sistema
- [ ] ✅ Socket.IO: Conectado
- [ ] ✅ Cantidad de contactos correcta

### Test 3: Bloquear Contacto
- [ ] ✅ Haz clic en **🔒 Bloquear** en cualquier contacto
- [ ] ✅ Botón cambia a **🔓 Desbloquear**
- [ ] ✅ Contacto muestra "🔒 Bloqueado por usuario_local"

### Test 4: Desbloquear Contacto
- [ ] ✅ Haz clic en **🔓 Desbloquear**
- [ ] ✅ Botón vuelve a **🔒 Bloquear**
- [ ] ✅ Desaparece el indicador de bloqueo

### Test 5: Llamar (InterPhone)
- [ ] ✅ Haz clic en **📞 Llamar** en cualquier contacto
- [ ] ✅ Si no tienes InterPhone: Muestra error "No se encontró InterPhone"
- [ ] ✅ Si tienes InterPhone: Intenta marcar

---

## 🧪 PASO 7: EJECUTAR PRUEBAS DE ROLES

**Terminal 3 (NUEVA, con servidor activo):**
```powershell
cd c:/Users/bjorg/OneDrive/Desktop/callmanager
python test_roles.py
```

**Esperado en consola:**

#### Health Check
- [ ] ✅ "✅ [200] GET /health"

#### Métricas Personales (Todos)
- [ ] ✅ "✅ [200] Agent: GET /metrics/personal"
- [ ] ✅ "✅ [200] TeamLead: GET /metrics/personal"
- [ ] ✅ "✅ [200] PM: GET /metrics/personal"
- [ ] ✅ "✅ [200] TI: GET /metrics/personal"

#### Métricas de Equipo (TeamLead+)
- [ ] ✅ "❌ [403] Agent: GET /metrics/team (forbidden)"
- [ ] ✅ "✅ [200] TeamLead: GET /metrics/team"
- [ ] ✅ "✅ [200] PM: GET /metrics/team"
- [ ] ✅ "✅ [200] TI: GET /metrics/team"

#### Métricas Globales (PM/TI)
- [ ] ✅ "❌ [403] Agent: GET /metrics/all (forbidden)"
- [ ] ✅ "❌ [403] TeamLead: GET /metrics/all (forbidden)"
- [ ] ✅ "✅ [200] PM: GET /metrics/all"
- [ ] ✅ "✅ [200] TI: GET /metrics/all"

#### Configuración - GET (PM/TI)
- [ ] ✅ "❌ [403] Agent: GET /config (forbidden)"
- [ ] ✅ "❌ [403] TeamLead: GET /config (forbidden)"
- [ ] ✅ "✅ [200] PM: GET /config"
- [ ] ✅ "✅ [200] TI: GET /config"

#### Configuración - POST (Solo TI)
- [ ] ✅ "❌ [403] Agent: POST /config (forbidden)"
- [ ] ✅ "❌ [403] TeamLead: POST /config (forbidden)"
- [ ] ✅ "❌ [403] PM: POST /config (forbidden)"
- [ ] ✅ "✅ [200] TI: POST /config"

#### Resumen Final
- [ ] ✅ "✅ PRUEBAS COMPLETADAS"
- [ ] ✅ Todos los ✅ donde corresponde
- [ ] ✅ Todos los ❌ donde corresponde (acceso denegado)

---

## 🔐 PASO 8: VALIDAR SEGURIDAD

### Test de Autenticación
```powershell
# Intentar sin API key (debe fallar)
curl http://127.0.0.1:5000/contacts

# Resultado esperado: Error 401 (Unauthorized) o 403
- [ ] ✅ Rechazado sin API key
```

```powershell
# Intentar con API key válida
curl -H "X-API-Key: dev-key-change-in-production" \
  http://127.0.0.1:5000/contacts

# Resultado esperado: Lista de contactos (JSON)
- [ ] ✅ Acepta con API key válida
```

### Test de Rate Limiting
```powershell
# Hacer múltiples requests en loop (después de 1000 en una hora, debería rechazar)
for ($i = 1; $i -le 10; $i++) {
    curl -H "X-API-Key: dev-key-change-in-production" \
      http://127.0.0.1:5000/health
}

# Resultado esperado: Los primeros 1000 funcionan, después 429 (Too Many Requests)
- [ ] ✅ Rate limiting está activo
```

---

## 📊 PASO 9: VERIFICAR LOGS

```powershell
# Ver últimas líneas del log
Get-Content callmanager.log -Tail 30
```

**Esperado:**
- [ ] ✅ Accesos registrados
- [ ] ✅ Cambios de contactos registrados
- [ ] ✅ Bloqueos/desbloqueos registrados
- [ ] ✅ Intentos de autorización registrados

---

## 💾 PASO 10: VERIFICAR BASE DE DATOS

```powershell
# Verificar que exists contacts.db
Test-Path contacts.db

# Resultado esperado: True
- [ ] ✅ contacts.db existe

# Verificar tamaño
(Get-Item contacts.db).Length

# Resultado esperado: > 50 KB (tiene datos)
- [ ] ✅ Database tiene contenido
```

---

## 🎯 RESUMEN FINAL

Si todos los ✅ están marcados, entonces:

- ✅ Sistema compila sin errores
- ✅ Base de datos inicializada correctamente
- ✅ Servidor inicia sin errores
- ✅ Cliente GUI conecta al servidor
- ✅ Importación de contactos funciona
- ✅ GUI funcional (botones, actualización)
- ✅ Roles y permisos funcionan correctamente
- ✅ Autenticación valida API key
- ✅ Rate limiting está activo
- ✅ Logs se registran correctamente

**VEREDICTO:** ✅ **SISTEMA COMPLETAMENTE FUNCIONAL**

---

## 🐛 SI ALGO FALLA

### Error: "No se pudo conectar al servidor"
- [ ] Asegúrate de que `python run_demo.py` sigue corriendo en Terminal 1
- [ ] Verifica que el puerto 5000 NO está bloqueado por firewall
- [ ] Intenta: `netstat -an | findstr 5000`

### Error: "Module not found: customtkinter"
- [ ] Instala: `pip install customtkinter`
- [ ] Actualiza: `pip install -r requirements.txt --upgrade`

### Error: "API key inválida"
- [ ] Asegúrate de ejecutar `init_users.py` primero
- [ ] Reemplaza las API keys en `test_roles.py` con las nuevas

### Error: "SyntaxError in run_demo.py"
- [ ] Verifica que tienes la versión corregida (con forward slashes)
- [ ] Delete cualquier `.pyc` viejo: `rm -r __pycache__`

### Database está vacía o corrupta
- [ ] Elimina: `contacts.db`
- [ ] Re-ejecuta: `python init_users.py`

---

## 📞 DOCUMENTACIÓN DE REFERENCIA

Para más detalles, consulta:

1. **QUICK_START_GUIA_RAPIDA.md** - Cómo empezar
2. **AUDITORIA_CALLMANAGER_COMPLETA.md** - Detalles técnicos
3. **ROLES_Y_AUTORIZACION.md** - Matriz de permisos
4. **ARQUITECTURA_FASE3.md** - Arquitectura del sistema
5. **ERRORES_ENCONTRADOS_Y_CORREGIDOS.md** - Qué se arregló

---

## ✨ FELICITACIONES

Si completaste todos los pasos, tu sistema CallManager está **100% funcional**.

🎉 **¡Listo para desarrollo y testing!** 🎉

---

**Checklist Versión:** 1.0  
**Fecha:** 21 de Noviembre, 2025  
**Sistema:** CallManager v3.3.1

*Usa este checklist para validar que todo funciona correctamente después de cambios o redeploys.*
