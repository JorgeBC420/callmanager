# 🎮 MODO DEMO - Prueba Local de CallManager

## ⚡ Quick Start (2 minutos)

### Paso 1: Abrir Terminal 1 (Servidor)
```bash
cd c:\Users\bjorg\OneDrive\Desktop\callmanager
python run_demo.py
```

**Debería ver:**
```
╔════════════════════════════════════════════════════════════════╗
║              CALLMANAGER - MODO DEMO LOCAL                    ║
║                      Test UI & Features                       ║
╚════════════════════════════════════════════════════════════════╝

✅ Contactos generados
🚀 Iniciando servidor Flask...
   ✅ Servidor iniciando en http://127.0.0.1:5000
```

### Paso 2: Abrir Terminal 2 (Cliente)
```bash
cd c:\Users\bjorg\OneDrive\Desktop\callmanager\client
python call_manager_app.py
```

**Debería ver:**
- Ventana de CallManager
- Botones: 📥 Importar Excel | 🔄 Refrescar | ℹ️ Estado
- Área vacía de contactos (se rellenarán después de importar)

---

## ✅ Pruebas a Realizar

### TEST 1: Conexión Socket.IO ✓
**Objetivo:** Verificar que el cliente se conecta al servidor

1. En la ventana del cliente, haz clic en **ℹ️ Estado**
2. Debería mostrar:
   - ✅ Socket.IO: Conectado
   - ✅ Servidor: http://127.0.0.1:5000
   - ✅ Contactos: 0 (aún sin importar)

**Resultado esperado:** ✅ Conexión exitosa

---

### TEST 2: Importar Contactos (FUNCIÓN PRINCIPAL) ✓
**Objetivo:** Verificar importación de Excel/CSV sin errores

1. Haz clic en **📥 Importar Excel**
2. Selecciona: `demo_contacts.csv` (está en la carpeta principal)
3. Debería mostrar:
   - Importación completada
   - Insertados: 15
   - Actualizados: 0

**Después:**
- Los 15 contactos aparecen en la lista
- Cada tarjeta muestra:
  - 📱 Nombre
  - ☎️ Teléfono (+506-5001-0001 → 50010001)
  - Status: NC, CUELGA, SIN_GESTIONAR, etc.
  - Botones: 📞 Llamar | 🔒 Bloquear

**Resultado esperado:** ✅ 15 contactos cargados sin errores

---

### TEST 3: Re-importar (Prueba de Duplicados) ✓
**Objetivo:** Verificar que NO crea duplicados

1. Haz clic nuevamente en **📥 Importar Excel**
2. Selecciona el mismo archivo: `demo_contacts.csv`
3. Debería mostrar:
   - Importación completada
   - Insertados: 0 (no hay nuevos)
   - Actualizados: 15 (se actualizaron)
   - **Duplicados fusionados: 15** ← ESTO ES LO IMPORTANTE

**Resultado esperado:** ✅ Detecta duplicados, NO crea duplicados

---

### TEST 4: UI - Botones y Layout ✓
**Objetivo:** Verificar que NO hay botones superpuestos

**Para cada contacto, verifica:**
- ✅ Nombre visible y legible
- ✅ Teléfono con formato: `+506-XXXX-XXXX (XXXXXXXX)`
- ✅ Status visible
- ✅ Botones 📞 Llamar y 🔒 Bloquear alineados sin superposición
- ✅ Sin scroll horizontal (todo cabe en pantalla)
- ✅ Espaciado consistente entre tarjetas

**Resultado esperado:** ✅ UI limpia, sin problemas de layout

---

### TEST 5: Refrescar (GET /contacts) ✓
**Objetivo:** Verificar que los contactos se cargan ordenados

1. Haz clic en **🔄 Refrescar**
2. Debería recargar los contactos
3. **Verificar el ORDEN:**
   - Primero: NC (No Contesta)
   - Segundo: CUELGA
   - Después: SIN_GESTIONAR
   - Etc.

**Resultado esperado:** ✅ Contactos ordenados por prioridad

---

### TEST 6: Prefijo +506 (Costa Rica) ✓
**Objetivo:** Verificar que se muestra y limpia correctamente

**En cualquier contacto:**
- Debería ver: `☎️ +506-5001-0001 (50010001)`
- Original: `+506-5001-0001`
- Para marcar: `50010001` (sin +506)

**Resultado esperado:** ✅ Ambos formatos visibles

---

### TEST 7: Bloquear Contacto ✓
**Objetivo:** Verificar sistema de locks

1. Haz clic en **🔒 Bloquear** en algún contacto
2. El botón debería cambiar a **🔓 Desbloquear**
3. Debería mostrar: 🔒 Bloqueado por [tu usuario]

**Resultado esperado:** ✅ Lock funciona

---

### TEST 8: Estados Dinámicos ✓
**Objetivo:** Verificar que los estados se muestran con visibilidad

En la tarjeta de cada contacto debería ver:
```
Status: NC [⏰ 0 meses]              ← Hoy se actualizó
Status: NC [⏰ 3 meses]             ← NO_EXISTE (automático)
Status: NC [⏰ 6 meses]             ← SIN_RED (automático)
Status: NC [⏰ 8+ meses]            ← NO_CONTACTO (automático)
```

**Resultado esperado:** ✅ Estados con indicadores visuales

---

## 🔍 Checklist Completo

### UI / Layout
- [ ] Todos los botones están VISIBLES
- [ ] Ningún botón está SUPERPUESTO
- [ ] El texto no sale del área (sin truncado incómodo)
- [ ] La ventana tiene scroll vertical si necesita
- [ ] Margins y padding consistentes

### Funcionalidad
- [ ] ✅ TEST 1: Conexión Socket.IO
- [ ] ✅ TEST 2: Importar contactos (15 = éxito)
- [ ] ✅ TEST 3: Detecta duplicados (15 actualizados)
- [ ] ✅ TEST 4: Botones sin superposición
- [ ] ✅ TEST 5: Ordenamiento por prioridad
- [ ] ✅ TEST 6: Prefijo +506 visible
- [ ] ✅ TEST 7: Bloqueo funciona
- [ ] ✅ TEST 8: Estados dinámicos mostrados

### Datos
- [ ] ✅ 15 contactos cargados
- [ ] ✅ Todos los teléfonos válidos
- [ ] ✅ Todos los estados presentes
- [ ] ✅ No hay errores en logs

---

## 📊 Archivos de Demo

```
demo_contacts.csv     ← Archivo para importar
demo_contacts.json    ← Mismos datos en JSON
contacts.db           ← Se crea automáticamente
callmanager.log       ← Logs (revisar si hay errores)
```

---

## 🐛 Troubleshooting

### Error: "No se puede conectar al servidor"
**Solución:**
```bash
# Verifica que el servidor está en otra terminal
# Terminal 1: python run_demo.py
# Debería mostrar: ✅ Servidor iniciando en http://127.0.0.1:5000
```

### Botones superpuestos
**Solución:**
- Aumenta el tamaño de la ventana
- Verifica: `client/call_manager_app.py` línea que ajusta geometría
- Default: `self.geometry('1000x700')`

### No aparecen contactos después de importar
**Solución:**
```bash
# Terminal del servidor, debería mostrar:
# INFO - Retrieved 15 contacts (sorted by priority)

# Si no ve esto, revisar en logs:
# callmanager.log
```

### ImportError: No module named...
**Solución:**
```bash
pip install -r requirements.txt
```

---

## 🎯 Resultado Esperado

✅ **DEMO EXITOSA** = Todos los tests pasan sin errores

Si hay problemas, consulta:
- Logs del servidor (consola Terminal 1)
- Logs del cliente (consola Terminal 2)
- Archivo `callmanager.log`

---

## 📝 Próximo Paso

Después de pasar todos los tests:

```bash
# Commit final
git add demo_contacts.py run_demo.py
git commit -m "Agregar scripts de demo para testing local"
git push origin main
```

---

**Estado:** Listo para demo local  
**Última actualización:** Noviembre 17, 2025
