# ⚡ GUÍA RÁPIDA LUNES - CallManager Deployment Fase 1

**Horario sugerido:**
- Mañana (08:00-10:00): Preparación + configuración
- Tarde (14:00-16:00): Testing + validación
- Resultado esperado: Sistema operativo lunes EOD

---

## 🎯 Paso 1: Preparación (Mañana 08:00)

### PC Central (Servidor)

```powershell
# 1. Verificar conectividad
ipconfig  # Notar IP en "IPv4 Address" (ej: 192.168.1.XXX)

# 2. Abrir PowerShell como Admin
# 3. Ir a carpeta del proyecto
cd C:\Users\usuario\OneDrive\Desktop\callmanager

# 4. Instalar dependencias
python -m pip install -r requirements.txt
# Esperar ~3-5 minutos

# 5. Iniciar servidor
python server.py

# 6. Debe mostrar esto (copiar pantalla para verificar):
"""
============================================================
Starting CallManager Server
Host: 0.0.0.0:5000
Database: contacts.db
Backups: backups
Auth enabled: True
============================================================
"""
```

**Si falla:**
- [ ] Ver si puerto 5000 está ocupado: `netstat -ano | findstr :5000`
- [ ] Cambiar puerto en `config.py`: `SERVER_PORT = 5001`
- [ ] Revisar Python 3.8+: `python --version`

---

## 🎯 Paso 2: Configurar Clientes (Mañana 09:00)

### Cada PC de Trabajador

```powershell
# 1. Copiar carpeta callmanager (ya debe estar)
# 2. Crear archivo config_local.json en carpeta client/:

# Ejemplo: C:\Users\usuario\OneDrive\Desktop\callmanager\client\config_local.json

# Contenido:
{
  "SERVER_URL": "http://192.168.1.100:5000",
  "API_KEY": "dev-key-change-in-production"
}

# CAMBIAR 192.168.1.100 por la IP real del servidor

# 3. Instalar dependencias
cd C:\Users\usuario\OneDrive\Desktop\callmanager
python -m pip install -r requirements.txt

# 4. Iniciar cliente
cd client
python call_manager_app.py
```

**Resultado esperado:**
```
✅ Ventana se abre
✅ "Cargando contactos..." aparece
✅ Botón "ℹ️ Estado" muestra "Socket.IO: Conectado"
```

---

## 🧪 Paso 3: Testing (Tarde 14:00)

### Test 1: Conexión Básica (5 min)

**En cliente:**
1. Presionar botón "ℹ️ Estado"
2. Verificar:
   ```
   Socket.IO: Conectado ✅
   Contactos: 0 (si es primera vez)
   ```
3. Presionar "🔄 Refrescar"
4. Debe cargar sin errores

**Si falla:** Ver log en servidor
```powershell
Get-Content callmanager.log -Tail 20
```

---

### Test 2: Importación Excel (10 min)

**Crear archivo test.xlsx:**
```
| phone          | name            | status         |
|----------------|-----------------|----------------|
| +506-5123-4567 | Juan Pérez      | SIN GESTIONAR  |
| 506-5789-0123  | María García    | LLAMADO        |
| 5551234567     | Bob Smith       | COMPLETADO     |
| +506-5123-4567 | Juan ACTUALIZADO| PROCESANDO     |  ← DUPLICADO
```

**En cliente:**
1. Presionar "📥 Importar Excel"
2. Seleccionar test.xlsx
3. **Resultado esperado:**
   ```
   Importación completada:
   - Insertados: 3
   - Actualizados: 1  ← ¡Vio el duplicado!
   ```
4. Presionar "🔄 Refrescar"
5. **Verificar:** Deben aparecer 3 contactos (no 4)

**Si falla:**
```powershell
# Ver error en logs
Get-Content callmanager.log | Select-String "ERROR" -Last 5
```

---

### Test 3: Marcar Número con +506 (10 min)

**En cliente:**
1. Ver tarjeta de contacto con +506
2. Debe mostrar: `☎️ +506-5123-4567 (51234567)` ✅
3. Abrir InterPhone en otra ventana
4. Click "📞 Llamar" en cliente
5. **Resultado esperado:**
   - InterPhone mostrará: `51234567` (sin +506)
   - Sin errores
   - Logs muestran: "Call initiated via Enter key for 51234567"

**Si falla:**
- [ ] Confirmar título de ventana: `InterPhone - ...`
- [ ] Ver logs: `Get-Content callmanager.log | Select-String "interphone" -Last 10`

---

### Test 4: Bloqueo de Edición (5 min)

**PC1:**
1. Presionar "🔒 Bloquear" en contacto
2. Ver: "🔒 Bloqueado por usuario_local"

**PC2:**
1. Ver contacto: "🔒 Bloqueado por usuario_local"
2. Intentar "🔒 Bloquear"
3. **Resultado esperado:** Mensaje "Bloqueado por usuario_local"

---

## 📊 Resultado Final (16:00)

| Test | Status | Observación |
|------|--------|-------------|
| 1. Conexión | ✅/❌ | |
| 2. Duplicados | ✅/❌ | |
| 3. Prefijo +506 | ✅/❌ | |
| 4. Bloqueo | ✅/❌ | |

**Si todos ✅:** 🎉 **GREENLIGHT PARA PRODUCCIÓN**

**Si alguno ❌:** Revisar logs y DEPLOYMENT.md

---

## 🚨 Troubleshooting Rápido

### "No se conecta"
```powershell
# 1. ¿Servidor está corriendo?
tasklist | findstr python

# 2. ¿Puerto abierto?
netstat -ano | findstr :5000

# 3. ¿Firewall?
netsh advfirewall firewall show rule name="CallManager"

# 4. ¿IP correcta en config_local.json?
# Debe ser la misma que en "ipconfig"
```

### "Error al importar Excel"
```powershell
# Ver error exacto
Get-Content callmanager.log | Select-String "ERROR" -Last 10

# Verificar formato Excel:
# - Primera fila: headers (phone, name, status)
# - Filas con datos debajo
```

### "InterPhone no se detecta"
```powershell
# 1. Confirmar que está abierto
tasklist | findstr InterPhone

# 2. Ver título exacto (debe ser "InterPhone - ...")
# 3. Revisar logs en callmanager.log
Get-Content callmanager.log | Select-String "InterPhone"
```

---

## 📞 Si Necesitas Ayuda

**Antes de preguntar, revisar:**
1. `callmanager.log` en PC central
2. Consola del cliente (si ejecutaste con `-verbose`)
3. DEPLOYMENT.md (sección Troubleshooting)

**Cambios nuevos (Fase 2):**
- Documentación: `MEJORAS_FASE2_COSTA_RICA.md`
- Funciones: `normalize_phone()` y `normalize_phone_for_interphone()`

---

## ✅ Checklist Final Lunes EOD

- [ ] Servidor corriendo sin errores
- [ ] 3+ clientes conectados
- [ ] Importación de Excel funcionando
- [ ] Números con +506 se marcan sin error
- [ ] Bloqueo de edición funciona
- [ ] Logs sin errores CRÍTICOS
- [ ] Backup automático en carpeta `backups/`
- [ ] Pantalla capturada para prueba de concepto

**Si TODO ✅:** Sistema listo para deployment gradual la semana que viene.

---

**Tiempo total:** 2 horas (mañana + tarde)  
**Resultado:** Sistema MVP operativo en producción

¡Mucho éxito el lunes! 🚀
