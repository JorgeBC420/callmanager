# 🚀 Quick Start - Phone Generator Integration

**Versión**: CallManager v3.3.1 + Phone Generator v1.0  
**Status**: ✅ READY FOR TESTING  
**Última Actualización**: Session Actual

---

## ¡Listo para usar! 🎉

La integración del generador de contactos de Costa Rica está **completamente implementada** y lista para probar.

---

## 1. Inicio Rápido (3 minutos)

### Opción A: Usar `run_demo.py` (RECOMENDADO)

```bash
cd c:/Users/bjorg/OneDrive/Desktop/callmanager
python run_demo.py
```

Esto:
1. ✅ Inicia el servidor Flask en puerto 5000
2. ✅ Inicia el cliente GUI automáticamente
3. ✅ Abre la lista de contactos

### Opción B: Iniciar por separado

**Terminal 1 - Servidor:**
```bash
cd c:/Users/bjorg/OneDrive/Desktop/callmanager
python server.py
```

**Terminal 2 - Cliente:**
```bash
cd c:/Users/bjorg/OneDrive/Desktop/callmanager
python client/call_manager_app.py
```

---

## 2. Usar el Generador (5 pasos)

### Paso 1: Identificar el Botón
```
Barra Superior del Cliente:
┌─────────────────────────────────────────┐
│ Servidor: http://localhost:5000         │
│                                         │
│ [📥 Importar Excel] [🎲 Generar]        │
│ [🔄 Refrescar] [ℹ️ Estado]             │
└─────────────────────────────────────────┘
```

Busca el botón **"🎲 Generar"**

### Paso 2: Click en el Botón
```
Haz clic en "🎲 Generar"
```

Se abrirá un diálogo:
```
┌──────────────────────────────────┐
│  Generar Contactos               │
├──────────────────────────────────┤
│                                  │
│  Cantidad de contactos:          │
│  [100________________]           │
│                                  │
│  Método:                         │
│  [stratified ▼]                 │
│                                  │
│        [Generar]                 │
│                                  │
└──────────────────────────────────┘
```

### Paso 3: Configurar Cantidad
```
Campo: "Cantidad de contactos"
Default: 100

Opciones válidas: 1 - 1000
Recomendado para test: 50
```

Borra el 100 e ingresa: `50`

### Paso 4: Seleccionar Método
```
Dropdown: "Método"
Default: stratified

Opciones:
┌─────────────────────────┐
│ stratified (Recomendado)│  ← 40% Kölbi, 35% Telefónica, 25% Claro
│ simple                  │  ← 33% cada operador
│ random                  │  ← Puramente aleatorio
└─────────────────────────┘

Selecciona: stratified (ya está)
```

### Paso 5: Generar
```
Click en botón [Generar]
```

Espera mensaje:
```
╔════════════════════════════════════╗
║  ✅ Éxito                          ║
║                                    ║
║  Se generaron 50 contactos        ║
║  de Costa Rica                     ║
║                                    ║
║              [OK]                  ║
╚════════════════════════════════════╝
```

### Paso 6: Verificar
```
✅ Dialog se cierra
✅ Lista se recarga automáticamente
✅ 50 números nuevos aparecen:
   
   Nombre: Costa Rica Kölbi
   Teléfono: 8123-4567
   
   Nombre: Costa Rica Telefónica
   Teléfono: 6012-3456
   
   Nombre: Costa Rica Claro
   Teléfono: 7012-3456
```

---

## 3. Validar Números Generados

### Estructura de Números
```
Costa Rica utiliza 8 dígitos:

Formato: XXXX-XXXX
Ejemplo: 8123-4567

Operadores por Prefijo:
├─ 8xxx: Kölbi (40%)
│  └─ Rangos: 8000-8999
│
├─ 6xxx: Telefónica (35%)
│  └─ Rangos: 6000-6500
│
└─ 7xxx: Claro (25%)
   └─ Rangos: 7000-7300
```

### Verificar Base de Datos
```bash
# Abrir SQLite
sqlite3 callmanager.db

# Ver contactos generados
SELECT COUNT(*) FROM contact;
SELECT phone, name FROM contact LIMIT 10;

# Contar por operador
SELECT 
  SUBSTR(phone, 1, 1) AS prefijo,
  CASE
    WHEN SUBSTR(phone, 1, 1) = '8' THEN 'Kölbi'
    WHEN SUBSTR(phone, 1, 1) = '6' THEN 'Telefónica'
    WHEN SUBSTR(phone, 1, 1) = '7' THEN 'Claro'
  END AS operador,
  COUNT(*) AS cantidad
FROM contact
GROUP BY prefijo;
```

---

## 4. Pruebas Automáticas (Opcional)

### Test API Directamente
```bash
# Terminal de PowerShell

# Test 1: Generar 10 números
curl -X POST http://localhost:5000/api/generate_contacts `
  -H "Content-Type: application/json" `
  -H "X-API-Key: test-key" `
  -d '{
    "amount": 10,
    "method": "stratified",
    "save": true
  }' | ConvertFrom-Json | Format-Table -Property success, count, saved

# Respuesta esperada:
# success   count  saved
# -------   -----  -----
# True      10     10
```

### Test 2: Validar Error (amount > 1000)
```bash
curl -X POST http://localhost:5000/api/generate_contacts `
  -H "Content-Type: application/json" `
  -H "X-API-Key: test-key" `
  -d '{
    "amount": 2000,
    "method": "stratified"
  }'

# Respuesta esperada:
# {"error": "amount debe ser 1-1000"}
```

### Test 3: Validar Error (method inválido)
```bash
curl -X POST http://localhost:5000/api/generate_contacts `
  -H "Content-Type: application/json" `
  -H "X-API-Key: test-key" `
  -d '{
    "amount": 100,
    "method": "invalid"
  }'

# Respuesta esperada:
# {"error": "method debe ser: stratified, simple, random"}
```

---

## 5. Resultados Esperados

### GUI
```
✅ Botón visible y funcional
✅ Dialog abre sin errores
✅ Validaciones funcionan
✅ Messagebox de éxito aparece
✅ Lista se recarga automáticamente
✅ 50 contactos nuevos visibles
```

### Backend
```
✅ Endpoint accessible: POST /api/generate_contacts
✅ Valida parámetros correctamente
✅ Genera números sin duplicados
✅ Guarda en base de datos
✅ Logs registran operación
✅ Respuestas JSON correctas
```

### Base de Datos
```
✅ 50 Contact records creados
✅ Nombres: "Costa Rica {Operator}"
✅ Teléfonos: Formato "XXXX-XXXX"
✅ Distribución respeta método:
   - Stratified: ~20 Kölbi, ~17 Telefónica, ~13 Claro
   - Simple: ~17 cada uno
   - Random: Variado
```

---

## 6. Solución de Problemas

### Problema 1: Button No Aparece
```
Solución:
1. Reinicia el cliente
2. Verifica que versión de CustomTkinter esté actualizada
3. Check: python -c "import customtkinter; print(customtkinter.__version__)"
```

### Problema 2: Dialog No Abre
```
Solución:
1. Revisa la consola para error messages
2. Verifica que requests esté instalado: pip install requests
3. Reinicia el cliente
```

### Problema 3: Error al Conectar al Servidor
```
Solución:
1. Verifica servidor: http://localhost:5000/health
2. Verifica puerto 5000 disponible: netstat -ano | findstr :5000
3. Reinicia servidor: python server.py
4. Reinicia cliente: python client/call_manager_app.py
```

### Problema 4: API Key Invalid
```
Solución:
1. Verifica config en client/config_loader.py
2. Verifica API_KEY en server.py
3. Deben coincidir
```

### Problema 5: Números No Guardan en BD
```
Solución:
1. Verifica permisos de archivo: callmanager.db
2. Cierra SQLite si está abierto
3. Verifica espacio en disco
4. Revisa logs para detalles: "Error saving phone"
```

---

## 7. Ejemplos de Uso

### Caso 1: Test Rápido
```
1. Open client
2. Click 🎲 Generar
3. Ingresa: 10
4. Selecciona: stratified
5. Click Generar
6. Espera: "Se generaron 10 contactos"
7. Verifica lista
```

### Caso 2: Bulk de Datos
```
1. Click 🎲 Generar
2. Ingresa: 500
3. Selecciona: stratified
4. Click Generar
5. Espera: "Se generaron 500 contactos"
6. Verifica distribución: 200 Kölbi, 175 Telefónica, 125 Claro
```

### Caso 3: Test de Métodos
```
Generar 3 veces:
1. 100 contactos con "stratified"
2. 100 contactos con "simple"
3. 100 contactos con "random"

Comparar distribuciones en BD
```

---

## 8. Información Técnica

### Estructura del Request
```json
POST /api/generate_contacts
Content-Type: application/json
X-API-Key: test-key

{
  "amount": 50,           # (int) 1-1000, default 100
  "method": "stratified", # (str) stratified|simple|random, default stratified
  "save": true            # (bool) Guardar en BD, default false
}
```

### Estructura de Response (Exitoso)
```json
{
  "success": true,
  "count": 50,
  "saved": 50,
  "phones": [
    {
      "number": "81234567",
      "operator": "Kölbi",
      "formatted": "8123-4567"
    },
    {
      "number": "60123456",
      "operator": "Telefónica",
      "formatted": "6012-3456"
    },
    ...
  ]
}
```

### Estructura de Response (Error)
```json
{
  "error": "amount debe ser 1-1000"
}
```

---

## 9. Checklist de Verificación

- [ ] Servidor inicia sin errores
- [ ] Cliente conecta al servidor
- [ ] Botón "🎲 Generar" visible
- [ ] Click abre dialog
- [ ] Dialog contiene campos esperados
- [ ] Validación rechaza "abc"
- [ ] Validación rechaza "0"
- [ ] Validación rechaza "2000"
- [ ] Generación con 50 contactos funciona
- [ ] Messagebox muestra éxito
- [ ] Lista se actualiza
- [ ] 50 contactos nuevos aparecen
- [ ] Contactos tienen nombre y teléfono válidos
- [ ] Números siguen formato XXXX-XXXX
- [ ] Distribución por operador es correcta
- [ ] Base de datos contiene registros

---

## 10. Recursos

| Recurso | Ubicación |
|---------|-----------|
| Servidor | `server.py` línea 1096 |
| Cliente | `client/call_manager_app.py` línea 54, 285 |
| Generador | `phone_generator.py` completo |
| Docs | `INTEGRACION_GENERADOR_CONTACTOS.md` |
| Visual | `RESUMEN_VISUAL_INTEGRACION.md` |
| Checklist | `CHECKLIST_PHONE_GENERATOR.md` |

---

## 11. Comandos Útiles

```bash
# Iniciar todo
python run_demo.py

# Iniciar solo servidor
python server.py

# Iniciar solo cliente
cd client
python call_manager_app.py

# Test de sintaxis
python -m py_compile server.py client/call_manager_app.py phone_generator.py

# Ver logs
tail -f server.log

# Test de API
curl http://localhost:5000/health

# Iniciar SQLite
sqlite3 callmanager.db
```

---

## 12. Próximos Pasos Después de Testing

✅ Si todo funciona:
1. Hacer commit a git
2. Crear pull request
3. Merge a main branch
4. Deploy a producción

❌ Si hay problemas:
1. Documentar error
2. Verificar logs
3. Hacer debugging
4. Ajustar código
5. Reintentar test

---

## 13. Contacto & Soporte

Si encuentras problemas:

1. Revisa los logs en `server.log`
2. Consulta `CHECKLIST_PHONE_GENERATOR.md`
3. Verifica error messages en dialog
4. Mira la consola del cliente

---

**¡Listo para empezar!** 🚀

Para comenzar:
```bash
cd c:/Users/bjorg/OneDrive/Desktop/callmanager
python run_demo.py
```

Luego click en el botón **"🎲 Generar"** en la GUI.

---

**Versión**: CallManager v3.3.1  
**Feature**: Phone Generator v1.0  
**Status**: ✅ READY FOR TESTING
