# Configuración para Render.com

## 📋 Resumen

Este proyecto está configurado para desplegarse en Render.com usando Pygbag para compilar el juego de Pygame a WebAssembly y Flask para servir los archivos.

## 🚀 Pasos para Desplegar

### 1. Preparar el Repositorio

Asegúrate de que todos los archivos estén en tu repositorio de GitHub:
- ✅ `app.py` - Servidor Flask
- ✅ `build.sh` - Script de compilación
- ✅ `render.yaml` - Configuración de Render
- ✅ `requirements.txt` - Dependencias actualizadas

### 2. Conectar con Render

1. Ve a [render.com](https://render.com) e inicia sesión
2. Haz clic en **"New +"** → **"Blueprint"**
3. Conecta tu repositorio de GitHub
4. Render detectará automáticamente el archivo `render.yaml`

### 3. Configuración Manual (Alternativa)

Si prefieres configurar manualmente:

1. **Crear Web Service:**
   - **Name:** `starship-game`
   - **Environment:** `Python 3`
   - **Region:** Elige la más cercana a tus usuarios
   - **Branch:** `main` (o la rama que uses)

2. **Build Settings:**
   ```
   Build Command: chmod +x build.sh && ./build.sh
   ```

3. **Start Command:**
   ```
   python app.py
   ```

4. **Environment Variables:**
   - `PORT`: Render lo configura automáticamente
   - No necesitas agregar variables adicionales

5. **Plan:**
   - **Free:** Funciona para pruebas
   - **Starter ($7/mes):** Recomendado para producción

### 4. Desplegar

1. Haz clic en **"Create Web Service"**
2. Render comenzará el proceso de build
3. El primer build puede tardar **5-10 minutos** (compilación de WebAssembly)
4. Una vez completado, tu juego estará disponible en la URL proporcionada

## ⚙️ Estructura del Proyecto

```
Starship-Game/
├── app.py              # Servidor Flask
├── main.py             # Punto de entrada del juego
├── game.py             # Lógica principal del juego
├── build.sh            # Script de compilación
├── render.yaml         # Configuración de Render
├── requirements.txt    # Dependencias Python
└── build/web/          # Archivos compilados (generados)
```

## 🔧 Solución de Problemas

### Error: "Build failed"

**Causa común:** Pygbag no puede compilar el juego

**Solución:**
1. Revisa los logs de build en Render
2. Verifica que todas las dependencias estén en `requirements.txt`
3. Asegúrate de que `main.py` sea el punto de entrada correcto

### Error: "404 Not Found" al cargar el juego

**Causa común:** Los archivos no se compilaron correctamente

**Solución:**
1. Verifica que `build/web/` contenga los archivos
2. Revisa que el script `build.sh` se ejecutó sin errores
3. Verifica los permisos del script: `chmod +x build.sh`

### El juego no carga en el navegador

**Causa común:** Problemas con WebAssembly o recursos faltantes

**Solución:**
1. Abre la consola del navegador (F12) y revisa errores
2. Verifica que todos los recursos (sonidos, imágenes, fuentes) estén incluidos
3. Asegúrate de que el navegador soporte WebAssembly

### Timeout durante el build

**Causa común:** El build tarda demasiado (límite de 45 min en plan gratuito)

**Solución:**
1. Considera usar un plan de pago con más tiempo
2. Optimiza el proceso de build
3. Verifica que no haya dependencias innecesarias

## 📝 Notas Importantes

- **Primera compilación:** Puede tardar 5-10 minutos
- **Compilaciones subsecuentes:** 2-5 minutos (solo cambios)
- **Recursos:** El juego necesita al menos 512 MB de RAM
- **Archivos grandes:** Los sonidos y assets pueden aumentar el tiempo de build

## 🔄 Actualizar el Juego

1. Haz push de tus cambios a GitHub
2. Render detectará automáticamente los cambios
3. Iniciará un nuevo build automáticamente
4. El servicio se actualizará cuando el build termine

## 🌐 URLs y Dominios

- Render proporciona una URL gratuita: `tu-app.onrender.com`
- Puedes agregar un dominio personalizado en la configuración
- Los cambios de dominio pueden tardar unos minutos en propagarse

## 💡 Alternativas

Si Pygbag no funciona en Render, considera:

1. **GitHub Pages + Pygbag:** Compilar localmente y subir a GitHub Pages
2. **Netlify:** Similar a Render pero con mejor soporte para WebAssembly
3. **Vercel:** Otra opción para aplicaciones web estáticas
4. **Replit:** Para desarrollo y despliegue rápido

## 📞 Soporte

- [Documentación de Render](https://render.com/docs)
- [Documentación de Pygbag](https://pygbag.readthedocs.io/)
- [Issues del Proyecto](https://github.com/SalazarBryan13/Starship-Game/issues)

