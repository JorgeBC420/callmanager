# 👨‍💼 GUÍA DE USO - GENERADOR DE NÚMEROS TELEFÓNICOS

## 🚀 INICIO RÁPIDO

### Paso 1: Abre CallManager
```powershell
python call_manager_app.py
```

### Paso 2: Login (primera vez)
```
Username: admin
Password: 1234
```

### Paso 3: Haz clic en "📱 Generar CR"
El botón verde está en la barra superior de la aplicación.

---

## 📱 INTERFAZ DETALLADA

### 1. ENCABEZADO
```
🇨🇷 Generador de Números Telefónicos
Plan Nacional de Numeración SUTEL 2024
```

### 2. INFORMACIÓN DE MERCADO
Muestra la distribución actual de operadores:
```
┌──────────────┬────────────────┬──────────────┐
│  Kölbi(ICE)  │   Telefónica   │    Claro     │
│     40%      │       35%      │      25%     │
│   (verde)    │     (azul)     │   (naranja)  │
└──────────────┴────────────────┴──────────────┘
```

### 3. CONFIGURACIÓN

#### Cantidad de números
```
Rango: 1 - 10,000
Ejemplo: 500 (genera 500 números)
```

#### Método de generación
```
○ Estratificado (RECOMENDADO) ⭐
  → Respeta la distribución real del mercado
  → Garantiza proporción correcta
  → Mejor para análisis estadístico

○ Aleatorio Simple
  → Completamente aleatorio
  → Sin garantía de distribución
  → Más rápido
```

#### Auto-importar a BD
```
✓ Marcar: Los números se guardan automáticamente
□ Desmarcar: Solo genera, no guarda
```

### 4. BOTONES DE ACCIÓN

#### 🎲 Generar Números (PRINCIPAL)
- Presiona para iniciar generación
- Cambio de texto: "⏳ Generando..." (durante proceso)
- Se deshabilita durante la generación
- Espera típica: 5-30 segundos

#### 💾 CSV
- Descarga los números en Excel
- Formato: `.csv` (comma-separated values)
- Columnas: ID, Nombre, Teléfono, Notas
- Abre automáticamente diálogo de guardado

#### 💾 JSON
- Descarga en formato JSON
- Incluye metadatos (total, método, timestamp)
- Ideal para integración con APIs
- Abre automáticamente diálogo de guardado

#### 📋 Copiar JSON
- Copia los datos al portapapeles
- Formato JSON completo
- Pega directamente en otras aplicaciones
- Sin necesidad de archivo

### 5. ÁREA DE RESULTADOS
```
✅ Generación completada!

Total: 500 números
Método: Estratificado

Distribución por operadora:
────────────────────────────
  Kölbi       200 (40.0%)
  Telefónica  175 (35.0%)
  Claro       125 (25.0%)

Base de datos:
  ✓ Importados:  498
  ⚠ Duplicados:  2

Primeros 5 números:
  1. +506-8000-1234 (Kölbi)
  2. +506-8100-5678 (Telefónica)
  3. +506-8700-9012 (Claro)
  4. +506-8000-3456 (Kölbi)
  5. +506-8100-7890 (Telefónica)
```

---

## 📖 CASOS DE USO COMUNES

### Caso 1: Generar 100 números para prueba
```
1. Haz clic en "📱 Generar CR"
2. Escribe: 100
3. Selecciona: Estratificado
4. Marca: ✓ Auto-importar
5. Presiona: "🎲 Generar Números"
6. Espera: ~10 segundos
7. Resultado: 40 Kölbi, 35 Telefónica, 25 Claro
```

### Caso 2: Descargar contactos a Excel
```
1. Genera números (ver Caso 1)
2. Presiona: "💾 CSV"
3. Elige ubicación y nombre
4. Se abre automáticamente en Excel
```

### Caso 3: Pasar a otra aplicación
```
1. Genera números
2. Presiona: "📋 Copiar JSON"
3. Abre la otra aplicación
4. Presiona: Ctrl+V para pegar
```

### Caso 4: Generar solo, sin guardar en BD
```
1. Genera números
2. Desmarca: ✓ Auto-importar
3. Presiona: "🎲 Generar Números"
4. Los números se generan pero NO se guardan
5. Puedes descargar CSV/JSON manualmente
```

---

## ⚠️ MENSAJES DE ERROR Y SOLUCIONES

### "❌ Error: Campo vacío"
```
CAUSA: No ingresaste cantidad
SOLUCIÓN: Escribe un número entre 1 y 10,000
```

### "❌ Error: Valor no numérico"
```
CAUSA: Escribiste letras o caracteres especiales
SOLUCIÓN: Solo números (123, 500, 1000, etc)
```

### "❌ Error: Cantidad fuera de rango"
```
CAUSA: Pediste menos de 1 o más de 10,000
SOLUCIÓN: Elige número entre 1 y 10,000
```

### "❌ Error: Timeout"
```
CAUSA: Generación tardó más de 60 segundos
SOLUCIÓN: Intenta con cantidad menor
```

### "❌ Error de conexión al servidor"
```
CAUSA: Servidor offline o no accesible
SOLUCIÓN: 
1. Abre terminal: python server.py
2. Espera a que diga "wsgi starting up"
3. Intenta de nuevo
```

### "❌ Error: No se pudo descargar archivo"
```
CAUSA: Problema con permisos de carpeta
SOLUCIÓN: Elige una carpeta donde tengas permisos
```

---

## 🎨 INTERFAZ VISUAL

### Colores
```
Verde (#2ecc71):    Botón principal, Kölbi
Azul (#3498db):     Información, Telefónica
Naranja (#e67e22):  Claro
Negro/Gris:         Texto y fondo
```

### Tamaño y Posición
```
Ancho:      750 píxeles
Alto:       700 píxeles
Posición:   Centrada en pantalla
Resizable:  No (tamaño fijo)
Modal:      Sí (bloquea ventana padre mientras genera)
```

---

## ⌨️ ATAJOS DE TECLADO

```
Tab         → Navega entre campos
Shift+Tab   → Navega atrás
Enter       → Presiona botón principal
Escape      → Cierra ventana (si no está generando)
Ctrl+V      → Pega (en campos de entrada)
```

---

## 📊 DATOS GENERADOS

### Formato de Número
```
+506-8000-1234

Estructura:
  +506    = Código país Costa Rica
  8XXX    = Área/Operadora
  1234    = Número secuencial

Rangos por operadora:
  Kölbi:       8000-8099, 8600-8699
  Telefónica:  8100-8199, 8700-8799
  Claro:       8200-8299, 8800-8999
```

### Metadatos en JSON
```json
{
  "total": 500,
  "method": "stratified",
  "timestamp": "2025-11-21T20:32:47.123456",
  "distribution": {
    "Kölbi": 200,
    "Telefónica": 175,
    "Claro": 125
  },
  "contacts": [...]
}
```

---

## 🔐 SEGURIDAD

✅ Validación de entrada en todos los campos  
✅ Timeout para evitar congelamiento  
✅ Threading para no bloquear UI  
✅ Manejo de excepciones robusto  
✅ Sin envío de datos a servidores externos  
✅ Encriptación de BD en servidor  

---

## 🐛 SOLUCIÓN DE PROBLEMAS

### La ventana no abre
```
1. Verifica que customtkinter esté instalado
   pip install customtkinter
2. Reinicia la aplicación
3. Revisa los logs en callmanager.log
```

### La generación es muy lenta
```
1. El servidor está ocupado
2. Intenta con cantidad menor (100 en lugar de 5000)
3. Prueba más tarde cuando hay menos tráfico
```

### Los números no se guardan en BD
```
1. Desmarca "Auto-importar"
2. Presiona generar nuevamente
3. Si persiste, revisa logs del servidor
```

### No puedo descargar archivo
```
1. Verifica permisos de carpeta
2. Intenta escribir en Desktop o Documentos
3. Revisa que no esté abierto en otro programa
```

---

## 📞 SOPORTE

Para reportar problemas o sugerencias:
1. Revisa los logs: `callmanager.log`
2. Intenta regenerar la base de datos
3. Contacta al administrador

---

**Última actualización:** 21 de Noviembre, 2025  
**Versión:** 1.0 - Production Ready
