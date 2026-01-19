# 🎮 Sistema de Tiempo Adaptativo con Machine Learning

## Nave Matemática - Modo Infinito

---

## 📋 Resumen

El juego "Operación Relámpago" incluye un **Modo Infinito** que utiliza un modelo de Machine Learning (ML) para ajustar dinámicamente el tiempo disponible para responder cada pregunta matemática. Este sistema hace el juego más desafiante al adaptarse al rendimiento del jugador.

---

## 🧠 ¿Qué hace el modelo de IA?

El modelo **predice cuánto tiempo tardará el jugador en responder** una pregunta matemática, basándose en:

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| **Signo operacional** | El tipo de operación matemática | `+`, `-`, `*`, `/` |
| **Respuestas correctas** | Cantidad acumulada de aciertos | 0, 5, 10, ... |
| **Vidas actuales** | Cuántas vidas le quedan al jugador | 1-5 |
| **Nivel** | El nivel de dificultad visual actual | 1, 2, 3 |

---

## 🔧 ¿Cómo funciona?

### 1. Carga del Modelo

Cuando el jugador selecciona **"MODO INFINITO"**, el juego:

```python
self.tiempo_adaptativo = TiempoAdaptativo()
```

Esto carga el archivo `mejor_modelo_tiempo.pkl` que contiene un modelo **GradientBoostingRegressor** pre-entrenado.

### 2. Predicción del Tiempo

Cada vez que se genera una nueva pregunta, el sistema:

1. **Codifica el signo** de la operación (ej: `*`=0, `+`=1, `-`=2, `/`=3)
2. **Prepara las variables**: `[signo, respuestas_correctas, vidas, nivel]`
3. **El modelo predice** cuántos segundos tardará el jugador
4. **Se suman 7 segundos** a la predicción para dar tiempo suficiente

```python
# Ejemplo de predicción
features = [signo_encoded, respuestas_correctas, vidas, nivel]
# [1, 5, 4, 2] → Suma, 5 correctas, 4 vidas, nivel 2

tiempo_predicho = modelo.predict(features)  # ≈ 3 segundos
tiempo_final = tiempo_predicho + 7.0        # ≈ 10 segundos
```

### 3. Ajuste con Historial

Si el jugador ya ha respondido varias preguntas, el sistema combina:
- **70%** de la predicción del modelo
- **30%** del promedio de sus últimos 3 tiempos de respuesta

Esto suaviza los cambios bruscos de tiempo.

### 4. Límites de Seguridad

El tiempo siempre se mantiene entre:
- **Mínimo**: 2 segundos
- **Máximo**: 10 segundos

---

## 📊 Flujo del Sistema

```
┌─────────────────────────────────────────────────────────┐
│                    MODO INFINITO                        │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│  1. Se genera una nueva pregunta matemática             │
│     Ejemplo: "15 ? 3 = 45"                              │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│  2. El sistema obtiene las variables:                   │
│     • Signo: * (multiplicación)                         │
│     • Respuestas correctas: 8                           │
│     • Vidas: 4                                          │
│     • Nivel: 2                                          │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│  3. El modelo ML predice: 2.8 segundos                  │
│     (tiempo estimado que tardará el jugador)            │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│  4. Se suman 7 segundos: 2.8 + 7.0 = 9.8 segundos       │
│     (para dar margen de respuesta)                      │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│  5. El temporizador muestra: 9.8 segundos               │
│     El jugador debe responder antes de que llegue a 0   │
└─────────────────────────────────────────────────────────┘
```

---

## 🎯 Impacto en el Juego

### Si el jugador responde rápido y correcto:
- El modelo aprende que necesita menos tiempo
- Las siguientes preguntas tendrán tiempos más ajustados
- **El juego se vuelve más desafiante**

### Si el jugador responde lento o incorrecto:
- El historial registra tiempos más largos
- Las siguientes preguntas mantienen tiempos generosos
- **El juego es más permisivo**

---

## 📁 Archivos Relacionados

| Archivo | Descripción |
|---------|-------------|
| `main.py` | Contiene la clase `TiempoAdaptativo` (líneas 896-980) |
| `mejor_modelo_tiempo.pkl` | Modelo ML entrenado (GradientBoostingRegressor) |
| `resultados.json` | Registro de todas las respuestas del jugador |

---

## 🔬 Tecnologías Utilizadas

- **scikit-learn**: Biblioteca de Machine Learning
- **joblib**: Para cargar el modelo serializado
- **numpy**: Para preparar los datos de entrada

---

## ⚙️ Configuración Actual

```python
TiempoAdaptativo(
    tiempo_base = 10.0,   # Tiempo inicial en segundos
    min_tiempo  = 2.0,    # Mínimo permitido
    max_tiempo  = 10.0    # Máximo permitido
)
```

La predicción del modelo (~3s) + 7 segundos adicionales = **~10 segundos** de tiempo para responder.

---

## 🚀 Diferencia entre Modos

| Característica | Modo Normal | Modo Infinito |
|----------------|-------------|---------------|
| Niveles | 3 niveles fijos | Sin niveles (oleadas infinitas) |
| Tiempo por pregunta | Fijo (10s) | Adaptativo (2-10s según ML) |
| Victoria | Al completar nivel 3 | No hay victoria (hasta perder) |
| Indicador UI | "Nivel X/3" | "Oleada X" |

---

## 🌲 ¿Qué es GradientBoostingRegressor?

**Gradient Boosting Regressor** es un algoritmo de Machine Learning para **predecir valores numéricos** (regresión). En nuestro caso, predice **cuántos segundos** tardará el jugador en responder.

### Concepto Básico: "Muchos expertos débiles = Un experto fuerte"

Imagina que quieres predecir algo difícil. En lugar de crear UN modelo muy complejo, creas **muchos modelos simples (árboles de decisión)** que trabajan en equipo.

```
Modelo Final = Árbol₁ + Árbol₂ + Árbol₃ + ... + Árbolₙ
```

Cada árbol se especializa en **corregir los errores** del árbol anterior.

---

### 📖 Explicación Paso a Paso

#### Paso 1: El Primer Árbol
El algoritmo crea un **primer árbol de decisión** simple que hace predicciones iniciales.

```
Ejemplo para predecir tiempo de respuesta:

                    ┌─────────────────┐
                    │ ¿Signo = * o /? │
                    └────────┬────────┘
                   Sí ──────┴────── No
                    │                 │
              ┌─────▼─────┐     ┌─────▼─────┐
              │ Predecir  │     │ Predecir  │
              │  4.2 seg  │     │  2.8 seg  │
              └───────────┘     └───────────┘
```

Este primer árbol comete errores. Por ejemplo:
- Predicción: 4.2 segundos
- Valor real: 5.0 segundos
- **Error: 0.8 segundos**

#### Paso 2: El Segundo Árbol (Corrige Errores)
El segundo árbol **NO predice el tiempo**, sino que predice **cuánto error cometió el primer árbol**.

```
Árbol 2: "Si respuestas_correctas > 10, el error del Árbol 1 tiende a ser +0.5"
```

#### Paso 3: Combinación
La predicción final combina todos los árboles:

```
Predicción Final = Árbol₁ + (tasa_aprendizaje × Árbol₂) + (tasa_aprendizaje × Árbol₃) + ...
```

La **tasa de aprendizaje** (ej: 0.1) controla cuánto aporta cada árbol, evitando cambios bruscos.

---

### 🎯 ¿Por qué "Gradient" (Gradiente)?

El algoritmo usa el concepto matemático de **gradiente** para encontrar la dirección de mejora.

Piensa en estar en una montaña con niebla queriendo bajar al valle:
1. Sientes la pendiente del suelo (el gradiente)
2. Das un paso hacia abajo
3. Repites hasta llegar al punto más bajo

```
Paso 1:  ⛰️ ────────────────────────────────── Error alto
         ↓ (calcula gradiente)
Paso 2:  ⛰️ ─────────────────────────── Error medio
         ↓ (calcula gradiente)
Paso 3:  ⛰️ ───────────────── Error bajo
         ↓ (calcula gradiente)
Paso N:  🏖️ ──── Error mínimo (valle)
```

Cada árbol nuevo "da un paso" hacia el valle (menor error).

---

### 🔢 Ejemplo Numérico Simplificado

**Datos de entrenamiento:**

| Signo | Correctas | Vidas | Nivel | Tiempo Real |
|-------|-----------|-------|-------|-------------|
| +     | 0         | 5     | 1     | 4.5 seg     |
| *     | 5         | 4     | 2     | 3.2 seg     |
| -     | 10        | 3     | 2     | 2.8 seg     |
| /     | 2         | 5     | 1     | 5.1 seg     |

**Entrenamiento:**

```
Árbol 1: Predicción inicial → Error promedio = 0.6 seg
Árbol 2: Corrige errores   → Error promedio = 0.4 seg
Árbol 3: Corrige errores   → Error promedio = 0.25 seg
...
Árbol 100: Error final     → Error promedio = 0.1 seg
```

**Predicción para nueva pregunta:**
```
Entrada: [signo=+, correctas=3, vidas=4, nivel=1]

Árbol 1 dice: 4.0 seg
Árbol 2 dice: +0.3 corrección
Árbol 3 dice: -0.1 corrección
...
Predicción final: 4.0 + 0.3 - 0.1 + ... = 4.15 seg
```

---

### 🆚 Comparación con Otros Modelos

| Modelo | Ventajas | Desventajas |
|--------|----------|-------------|
| **Regresión Lineal** | Simple, rápido | Solo relaciones lineales |
| **Árbol de Decisión** | Interpreta fácil | Puede sobreajustar |
| **Random Forest** | Robusto, paralelo | Menos preciso que Boosting |
| **Gradient Boosting** ✅ | Muy preciso | Más lento, secuencial |

---

### ⚙️ Parámetros del Modelo

El modelo en el juego probablemente fue entrenado con estos parámetros:

```python
from sklearn.ensemble import GradientBoostingRegressor

modelo = GradientBoostingRegressor(
    n_estimators=100,      # Número de árboles
    learning_rate=0.1,     # Tasa de aprendizaje (paso)
    max_depth=3,           # Profundidad de cada árbol
    random_state=42        # Reproducibilidad
)

# Entrenamiento
modelo.fit(X_train, y_train)

# Guardar modelo
joblib.dump(modelo, 'mejor_modelo_tiempo.pkl')
```

---

### 📈 Resumen Visual

```
┌─────────────────────────────────────────────────────────────┐
│              GRADIENT BOOSTING REGRESSOR                    │
└─────────────────────────────────────────────────────────────┘

   Datos ──▶ Árbol₁ ──▶ Errores₁ ──▶ Árbol₂ ──▶ Errores₂ ──▶ ...
                │                       │
                ▼                       ▼
            Predicción             Corrección
               base                  +0.3

   ┌─────────────────────────────────────────────────────────┐
   │  Predicción Final = Σ (todos los árboles × sus pesos)  │
   └─────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │   3.2 segundos  │
                    │   (predicción)  │
                    └─────────────────┘
```

---

### 🎮 En el Contexto del Juego

1. **Se entrenó** con datos históricos de jugadores (tiempos de respuesta reales)
2. **Aprendió patrones** como:
   - División y multiplicación toman más tiempo que suma/resta
   - Jugadores con más respuestas correctas responden más rápido
   - Menos vidas = más presión = tiempos variados
3. **Predice** el tiempo esperado para ajustar el temporizador dinámicamente
