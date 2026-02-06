# Optimizaciones para Rendimiento Web

Este documento explica las optimizaciones implementadas para mejorar el rendimiento del juego cuando se ejecuta en navegador web (desplegado en Render).

## 🚀 Optimizaciones Implementadas

### 1. **FPS Reducido**
- **Desktop:** 60 FPS
- **Web:** 30 FPS
- **Beneficio:** Reduce la carga de CPU y mejora la fluidez en navegadores

### 2. **Partículas Reducidas**
- **Estrellas de fondo:** 100 → 50 (en web)
- **Partículas del menú:** 90 → 28 (en web)
- **Símbolos flotantes:** 12 → 6 (en web)
- **Beneficio:** Menos objetos a renderizar = mejor rendimiento

### 3. **Calidad de Sonido Reducida**
- **Desktop:** 44.1 kHz (calidad CD)
- **Web:** 22.05 kHz (calidad reducida)
- **Buffer de audio:** 1024 → 512 (en web)
- **Beneficio:** Menos procesamiento de audio, carga más rápida

### 4. **Cache y Headers HTTP**
- Headers de cache para archivos estáticos
- Cache de 1 hora para recursos
- **Beneficio:** Recursos se cargan desde cache del navegador

## ⚠️ Limitaciones del Plan Gratuito de Render

### Problema Principal: "Cold Start"
- **Las instancias gratuitas se "duermen" después de 15 minutos de inactividad**
- **Primera carga después del sleep:** ~50 segundos de delay
- **Solución:** Considera actualizar a un plan de pago ($7/mes) para evitar este problema

### Otras Limitaciones
- **CPU limitada:** Menos potencia de procesamiento
- **Memoria limitada:** 512 MB RAM
- **Sin CDN:** Los archivos se sirven desde un solo servidor

## 🔧 Mejoras Adicionales Recomendadas

### Para Mejor Rendimiento:

1. **Actualizar a Plan de Pago**
   - Elimina el "cold start"
   - Más CPU y memoria
   - Mejor rendimiento general

2. **Optimizar Recursos**
   - Comprimir archivos de sonido (.ogg más pequeños)
   - Reducir tamaño de imágenes
   - Usar formatos modernos (WebP para imágenes)

3. **CDN para Assets**
   - Servir recursos estáticos desde CDN
   - Mejor velocidad de carga global

4. **Lazy Loading**
   - Cargar sonidos solo cuando se necesiten
   - Cargar niveles bajo demanda

## 📊 Comparación de Rendimiento

| Aspecto | Desktop | Web (Free) | Web (Paid) |
|---------|---------|------------|------------|
| FPS | 60 | 30 | 30-45 |
| Partículas | 100% | 50% | 70% |
| Calidad Audio | 44.1 kHz | 22.05 kHz | 22.05 kHz |
| Cold Start | N/A | ~50s | ~2s |
| Latencia | Baja | Media | Baja |

## 🎮 Cómo Funciona la Detección Web

El juego detecta automáticamente si está ejecutándose en web mediante:
- Variable de entorno `PYGBAG`
- Módulos de Pygbag cargados
- Características de la plataforma

Cuando detecta web, aplica automáticamente todas las optimizaciones.

## 💡 Tips para Usuarios

1. **Primera carga:** Espera ~50 segundos si la instancia estaba dormida
2. **Cargas subsecuentes:** Deberían ser mucho más rápidas
3. **Si es muy lento:** Considera actualizar a plan de pago
4. **Navegador:** Usa Chrome/Edge para mejor rendimiento de WebAssembly

