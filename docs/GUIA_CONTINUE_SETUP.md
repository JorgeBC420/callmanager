# 🤖 Guía de Configuración: Continue + Ollama (Offline)

## Estado Actual

✅ **Configuración completada:**
- Archivo `config.yaml` creado en `C:\Users\bjorg\.continue\`
- 4 modelos Ollama configurados
- CallManager v2.0 listo

## Modelos Disponibles (Offline)

```yaml
1. DeepSeek V3     → deepseek-v3      (Muy rápido, excelente código)
2. DeepSeek R1     → deepseek-r1      (Razonamiento, buenas explicaciones)
3. Llama 3.2 11B   → llama3.2-11b     (Ligero, rápido)
4. GPT OSS 120B    → gpt-oss-120b     (Más pesado pero poderoso)
```

## ⚙️ Cómo Activar Continue Offline

### Paso 1: Iniciar Ollama
```powershell
ollama serve
```
Debe mostrar:
```
Listening on 127.0.0.1:11434
```

### Paso 2: Abrir VS Code
- Presiona `Ctrl + K` (Abre Quick Commands)
- Escribe: `Continue`
- Selecciona: `Continue: Open Chat`

### Paso 3: Seleccionar Modelo
- En el chat de Continue, busca el dropdown de modelos
- Selecciona uno de los 4 modelos Ollama disponibles
- Ej: "DeepSeek V3 (Offline)"

### Paso 4: ¡A Usar!
```
[Chat Input] ¿Cómo optimizo esta función?
[Continue]   Usa el modelo offline seleccionado
```

## 🔧 Troubleshooting

### ❌ "Cannot connect to Ollama"
```powershell
# Verifica que Ollama esté ejecutándose
ollama list

# Si no ve modelos, descárgate uno:
ollama pull deepseek-v3
```

### ❌ "No models available"
```powershell
# Asegúrate de que está en C:\Users\bjorg\.continue\config.yaml
Get-Content "$env:USERPROFILE\.continue\config.yaml"
```

### ❌ Continue no aparece en VS Code
```
1. Instala extensión: "Continue - Coding with AI"
2. Recarga VS Code: Ctrl+Shift+P → Developer: Reload Window
3. Abre Continue: Ctrl+Shift+C
```

## 📋 Configuración Actual

**Archivo:** `C:\Users\bjorg\.continue\config.yaml`

```yaml
models:
  - provider: "ollama"
    apiBase: "http://localhost:11434"
    models: 
      - deepseek-v3
      - deepseek-r1
      - llama3.2-11b
      - gpt-oss-120b
```

## 🚀 Ventajas de Usar Offline

✅ **Sin límites de uso**
- Chats ilimitados
- Sin cuota de API
- Sin throttling

✅ **Privacidad**
- Tu código nunca sale de tu PC
- Información sensible protegida
- Funciona sin conexión a internet

✅ **Velocidad**
- Más rápido que esperar por API remota
- CPU/GPU local optimizadas
- Ideal para desarrollo local

## 💡 Tips de Uso

**Para Coding:**
```
"DeepSeek V3" - Mejor para código Python
"DeepSeek R1" - Mejor para debugging
```

**Para Documentación:**
```
"Llama 3.2 11B" - Más rápido para docs
```

**Para Análisis Profundo:**
```
"GPT OSS 120B" - Más potente pero lento
```

## ✅ Checklist

- [x] Configuración de Continue creada
- [x] Modelos Ollama agregados a config.yaml
- [x] Archivo copiado a ~/.continue/
- [ ] Ollama instalado y ejecutándose (`ollama serve`)
- [ ] Extensión Continue instalada en VS Code
- [ ] Probado con al menos 1 modelo

## 📝 Para la Próxima Sesión

1. **Inicia Ollama:**
   ```powershell
   ollama serve
   ```

2. **Abre VS Code y prueba Continue:**
   - Ctrl+Shift+C
   - Selecciona un modelo
   - ¡Disfruta coding con IA offline!

---

**Última actualización:** 21 Noviembre 2025
**Estado:** ✅ Lista para usar
