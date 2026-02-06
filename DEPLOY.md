# Guía de Despliegue en Render

Esta guía te ayudará a desplegar el juego **Operación Relámpago** en Render.

## Opción 1: Despliegue Automático con render.yaml

1. **Conecta tu repositorio a Render:**
   - Ve a [render.com](https://render.com) y crea una cuenta
   - Haz clic en "New +" y selecciona "Blueprint"
   - Conecta tu repositorio de GitHub que contiene este proyecto
   - Render detectará automáticamente el archivo `render.yaml` y configurará el servicio

2. **El despliegue comenzará automáticamente:**
   - Render ejecutará el script `build.sh` para compilar el juego con Pygbag
   - Luego iniciará el servidor Flask con `python app.py`
   - El juego estará disponible en la URL proporcionada por Render

## Opción 2: Despliegue Manual

Si prefieres configurar manualmente:

1. **Crea un nuevo Web Service en Render:**
   - Ve a tu dashboard de Render
   - Haz clic en "New +" → "Web Service"
   - Conecta tu repositorio de GitHub

2. **Configura el servicio:**
   - **Name:** `starship-game` (o el nombre que prefieras)
   - **Environment:** `Python 3`
   - **Build Command:** 
     ```bash
     chmod +x build.sh && ./build.sh
     ```
   - **Start Command:**
     ```bash
     python app.py
     ```
   - **Environment Variables:**
     - `PORT`: `5000` (Render lo configurará automáticamente)

3. **Haz clic en "Create Web Service"**

## Notas Importantes

- **Tiempo de Build:** El primer despliegue puede tardar varios minutos ya que Pygbag necesita compilar el juego a WebAssembly
- **Recursos:** Asegúrate de que tu plan de Render tenga suficientes recursos (al menos 512 MB de RAM)
- **Archivos Estáticos:** El juego compilado se guardará en `build/web/`
- **Logs:** Si hay problemas, revisa los logs de build y runtime en el dashboard de Render

## Solución de Problemas

### El juego no se carga
- Verifica que el build se haya completado correctamente revisando los logs
- Asegúrate de que todos los archivos en `build/web/` estén presentes

### Error de compilación
- Verifica que todas las dependencias estén en `requirements.txt`
- Revisa que el archivo `main.py` sea el punto de entrada correcto

### El servidor no inicia
- Verifica que el puerto esté configurado correctamente (Render usa la variable `PORT`)
- Revisa los logs de runtime para ver errores específicos

## Desarrollo Local

Para probar localmente antes de desplegar:

```bash
# Instalar dependencias
pip install -r requirements.txt

# Compilar el juego
chmod +x build.sh
./build.sh

# Ejecutar el servidor
python app.py
```

Luego visita `http://localhost:5000` en tu navegador.

