# ✅ CHECKLIST - QUÉ ESPERAR AL USAR EL GENERADOR

## 🎬 ESCENA 1: ABRIR LA VENTANA

Cuando hagas clic en "📱 Generar CR":

- [ ] Se abre una nueva ventana (no reemplaza la principal)
- [ ] Tamaño: 750x700 píxeles (bastante grande)
- [ ] Se centra automáticamente en la pantalla
- [ ] Tiene un título: "🇨🇷 Generador de Números Telefónicos"
- [ ] Subtítulo: "Plan Nacional de Numeración SUTEL 2024"

**Tiempo esperado:** <1 segundo

---

## 🎨 ESCENA 2: INTERFAZ VISUAL

La ventana tiene 5 secciones:

### Sección 1: Información de Mercado
```
┌──────────────┬────────────────┬──────────────┐
│  Kölbi(ICE)  │   Telefónica   │    Claro     │
│     40%      │       35%      │      25%     │
│   (verde)    │     (azul)     │   (naranja)  │
└──────────────┴────────────────┴──────────────┘
```
- [ ] Tres cajas de información
- [ ] Colores: verde, azul, naranja
- [ ] Porcentajes de cada operadora

### Sección 2: Entrada de Datos
```
Cantidad de números:
[____________] (1 - 10,000)

Método de generación:
○ Estratificado (Recomendado) ⭐
○ Aleatorio Simple
💬 "Respeta la distribución real..."

✓ Importar automáticamente a la base de datos
```
- [ ] Campo de entrada numérica (largo)
- [ ] Dos opciones de radio button
- [ ] Una descripción que cambia con la selección
- [ ] Un checkbox para auto-importar
- [ ] Límites visibles (1-10,000)

### Sección 3: Botones de Acción
```
┌────────────────────────────────────────┐
│   🎲 Generar Números (botón verde)    │
└────────────────────────────────────────┘

┌──────────────┬──────────────┬──────────────┐
│  💾 CSV      │  💾 JSON     │  📋 Copiar  │
└──────────────┴──────────────┴──────────────┘
```
- [ ] Botón principal grande de color verde
- [ ] Tres botones secundarios para exportación
- [ ] Texto claro en cada botón
- [ ] Botones deshabilitados hasta generar

### Sección 4: Área de Resultados
```
┌────────────────────────────────────────┐
│ (Área vacía o con resultados)         │
│                                        │
│ (Scrolleable si texto largo)          │
│                                        │
└────────────────────────────────────────┘
```
- [ ] Área grande de texto (scrolleable)
- [ ] Inicialmente vacía o con instrucciones
- [ ] Se llena con resultados después de generar

---

## ⚙️ ESCENA 3: GENERAR NÚMEROS

### Paso a paso esperado:

1. **Ingresa cantidad:** Escribe `100`
   - [ ] El número aparece en el campo
   - [ ] Sin errores
   - [ ] Límites: 1-10,000

2. **Selecciona método:** Haz clic en "Estratificado"
   - [ ] Se marca el radio button
   - [ ] Cambia la descripción del método
   - [ ] Sin retrasos

3. **Marca auto-importar:** Haz clic en ✓
   - [ ] Se marca el checkbox
   - [ ] Puedes desmarcarlo si quieres

4. **Presiona "Generar Números"**
   - [ ] Botón se pone gris (deshabilitado)
   - [ ] Texto cambia a "⏳ Generando..."
   - [ ] Aparece mensaje en área de resultados: "⏳ Generando 100 números..."
   - [ ] UI responsiva (puedes mover ventana)

5. **Espera (5-30 segundos)**
   - [ ] Estatus en textbox se actualiza
   - [ ] Puedes cancelar si presionas X (con confirmación)
   - [ ] NO se congela la aplicación principal

---

## 📊 ESCENA 4: RESULTADOS

Después de generar, verás algo como:

```
✅ Generación completada!

Total: 100 números
Método: Estratificado

Distribución por operadora:
────────────────────────────
  Kölbi       40 (40.0%)
  Telefónica  35 (35.0%)
  Claro       25 (25.0%)

Base de datos:
  ✓ Importados:  98
  ⚠ Duplicados:  2

Primeros 5 números:
  1. +506-8000-1234 (Kölbi)
  2. +506-8100-5678 (Telefónica)
  3. +506-8700-9012 (Claro)
  4. +506-8000-3456 (Kölbi)
  5. +506-8100-7890 (Telefónica)
```

### Checklist de Resultados:
- [ ] Aparece ✅ al principio
- [ ] Muestra total de números generados
- [ ] Muestra el método usado
- [ ] Muestra distribución por operadora
- [ ] Si auto-importó, muestra cantidad importada y duplicados
- [ ] Muestra ejemplos de números generados
- [ ] Todos los números empiezan con +506
- [ ] Los números tienen operadora entre paréntesis
- [ ] El botón "Generar" vuelve a estar disponible (verde)
- [ ] Los botones de exportación se habilitan (verde)

**Tiempo esperado:** 5-30 segundos según cantidad

---

## 💾 ESCENA 5: DESCARGAR

### Opción 1: Descargar CSV

Presiona el botón "💾 CSV":

1. [ ] Se abre diálogo "Guardar archivo como..."
2. [ ] Nombre sugerido: `contactos_20251121_203200.csv`
3. [ ] Ubicación: Tu carpeta de descargas
4. [ ] Presionas "Guardar"
5. [ ] Se descarga el archivo
6. [ ] Mensaje de éxito (opcional)

**Archivo contiene:**
```
id,name,phone,notes
1,Contacto 1,+506-8000-1234,Kölbi
2,Contacto 2,+506-8100-5678,Telefónica
3,Contacto 3,+506-8700-9012,Claro
...
```

### Opción 2: Descargar JSON

Presiona el botón "💾 JSON":

1. [ ] Se abre diálogo "Guardar archivo como..."
2. [ ] Nombre sugerido: `contactos_20251121_203200.json`
3. [ ] Ubicación: Tu carpeta de descargas
4. [ ] Presionas "Guardar"
5. [ ] Se descarga el archivo

**Archivo contiene:**
```json
{
  "total": 100,
  "method": "stratified",
  "timestamp": "2025-11-21T20:32:47.123456",
  "distribution": {
    "Kölbi": 40,
    "Telefónica": 35,
    "Claro": 25
  },
  "contacts": [
    {
      "id": "1",
      "name": "Contacto 1",
      "phone": "+506-8000-1234",
      "notes": "Kölbi"
    },
    ...
  ]
}
```

### Opción 3: Copiar a Portapapeles

Presiona el botón "📋 Copiar JSON":

1. [ ] El JSON se copia automáticamente
2. [ ] Aparece mensaje (informativo)
3. [ ] Puedes pegar en otra aplicación con Ctrl+V
4. [ ] Sin diálogo de archivo

---

## ❌ ESCENA 6: ERRORES (si ocurren)

### Error 1: Cantidad vacía
```
❌ Error:
Campo requerido: Debes ingresar una cantidad
```
- [ ] Aparece mensaje claro
- [ ] La ventana NO se cierra
- [ ] Puedes corregir e intentar de nuevo

### Error 2: Cantidad no numérica
```
❌ Error:
Valor inválido: Solo se aceptan números (1-10,000)
```
- [ ] Aparece mensaje claro
- [ ] El botón se vuelve disponible nuevamente
- [ ] Puedes corregir e intentar

### Error 3: Fuera de rango
```
❌ Error:
Cantidad fuera de rango: Debe estar entre 1 y 10,000
```
- [ ] Mensaje específico del rango
- [ ] Puedes ajustar y reintentar

### Error 4: Servidor no disponible
```
❌ Error de conexión:
No se puede conectar al servidor (127.0.0.1:5000)
Por favor, asegúrate de que el servidor está activo
```
- [ ] Mensaje claro sobre la conexión
- [ ] Opción de revisar si el servidor está corriendo
- [ ] NO se cuelga

### Error 5: Timeout (más de 60 segundos)
```
❌ Error:
La generación tardó demasiado tiempo (timeout)
Intenta con una cantidad menor
```
- [ ] Aparece después de 60 segundos
- [ ] La UI vuelve a responder
- [ ] Puedes intentar de nuevo con menos números

---

## 🎭 ESCENA 7: INTERACCIONES

### Si cambias el método:
- [ ] La descripción se actualiza inmediatamente
- [ ] Puedes ver diferencia entre "Estratificado" y "Aleatorio"
- [ ] Sin delay

### Si desmarques Auto-importar:
- [ ] La generación sigue funcionando
- [ ] Los números no se guardan en BD
- [ ] No afecta la descarga de archivos

### Si cierras durante generación:
- [ ] Ventana pregunta: "¿Hay generación en progreso. ¿Deseas cerrar?"
- [ ] Opción de: [Sí, cerrar] [No, continuar]
- [ ] Si dices Sí, se detiene todo
- [ ] Si dices No, sigue generando

### Si haces clic en "Generar CR" nuevamente:
- [ ] La ventana existente se trae al frente
- [ ] NO abre una segunda ventana
- [ ] Es eficiente (patrón Singleton)

---

## 🎯 ESCENA 8: COMPORTAMIENTO ESPERADO

### Velocidad
- [ ] Generación: 5-30 segundos (depende de cantidad)
- [ ] Exportación: <1 segundo
- [ ] Copiar: Instantáneo (<100ms)
- [ ] UI: Siempre responsiva

### Apariencia
- [ ] Ventana: Profesional, clara, no confusa
- [ ] Colores: Coherentes (verde=Kölbi, azul=Telefónica, naranja=Claro)
- [ ] Texto: Legible, sin errores ortográficos
- [ ] Iconos: Apropiados (📱, 🎲, 💾, 📋, ✅, ❌)

### Funcionalidad
- [ ] Todo botón tiene acción inmediata
- [ ] Los mensajes son claros
- [ ] Los errores se explican bien
- [ ] Puedes reintentar sin problemas
- [ ] Los datos se generan correctamente

---

## 🎉 RESUMEN: QUÉ DEBERÍA PASAR

```
1. ✅ Haces clic en "📱 Generar CR"
           ↓
2. ✅ Se abre ventana profesional 750x700
           ↓
3. ✅ Ingresas cantidad (ej: 100)
           ↓
4. ✅ Seleccionas método (Estratificado)
           ↓
5. ✅ Marcas auto-importar
           ↓
6. ✅ Presionas "Generar Números"
           ↓
7. ✅ Botón se pone gris, aparece "⏳ Generando..."
           ↓
8. ✅ Esperas 5-30 segundos
           ↓
9. ✅ Aparecen resultados en textbox
           ↓
10. ✅ Botones de exportación se habilitan
           ↓
11. ✅ Descargas CSV, JSON o copias JSON
           ↓
12. ✅ Archivos se guardan correctamente
           ↓
13. 🎉 ¡ÉXITO TOTAL!
```

---

## 🎬 ¿LISTO PARA INTENTAR?

Ahora tienes claro exactamente qué esperar. La nueva versión es:

✅ **Estable** - Maneja errores correctamente  
✅ **Rápida** - No bloquea la UI  
✅ **Clara** - Interfaz profesional  
✅ **Flexible** - Múltiples opciones  
✅ **Segura** - Validación robusta  

### Instrucciones finales:
1. Abre CallManager
2. Login con admin/1234
3. Haz clic en "📱 Generar CR"
4. ¡Disfruta la nueva experiencia!

---

**Generado:** 21 de Noviembre, 2025  
**Estado:** Ready to use ✅
