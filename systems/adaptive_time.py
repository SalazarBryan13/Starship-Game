# -*- coding: utf-8 -*-
"""
Sistema de tiempo adaptativo usando Machine Learning
"""

# Importar librerías opcionales
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

try:
    import joblib
    HAS_JOBLIB = True
except ImportError:
    HAS_JOBLIB = False


class TiempoAdaptativo:
    """
    Sistema de tiempo adaptativo para el modo infinito usando ML.
    Predice el tiempo de respuesta del jugador y ajusta dinámicamente
    el tiempo disponible para cada pregunta.
    """
    
    def __init__(self, tiempo_base=10.0, min_tiempo=2.0, max_tiempo=10.0):
        self.tiempo_base = tiempo_base
        self.tiempo_actual = tiempo_base
        self.min_tiempo = min_tiempo
        self.max_tiempo = max_tiempo
        self.factor_ajuste = 0.5
        self.modelo = None
        self.usar_modelo = False
        self.historial = []
        # Mapeo de signos según el entrenamiento del modelo
        self.signo_map = {'*': 0, '+': 1, '-': 2, '/': 3}
        
        # Intentar cargar el modelo ML
        if HAS_JOBLIB and HAS_NUMPY:
            try:
                self.modelo = joblib.load('mejor_modelo_tiempo.pkl')
                self.usar_modelo = True
                print("✅ Modelo ML cargado correctamente para modo infinito")
            except FileNotFoundError:
                print("⚠️ Archivo mejor_modelo_tiempo.pkl no encontrado")
                self.usar_modelo = False
            except Exception as e:
                print(f"⚠️ Error al cargar el modelo: {e}")
                self.usar_modelo = False
        else:
            print("⚠️ joblib o numpy no disponible, usando tiempo fijo")
    
    def predecir_tiempo(self, signo, respuestas_correctas, vidas, nivel):
        """Predice el tiempo de respuesta usando el modelo ML."""
        if not self.usar_modelo or not HAS_NUMPY:
            return self.tiempo_actual
        
        try:
            signo_encoded = self.signo_map.get(signo, 1)
            features = np.array([[signo_encoded, respuestas_correctas, vidas, nivel]])
            tiempo_predicho = self.modelo.predict(features)[0]
            return float(tiempo_predicho)
        except Exception as e:
            print(f"Error en predicción: {e}")
            return self.tiempo_actual
    
    def obtener_tiempo(self, signo, respuestas_correctas, vidas, nivel):
        """Obtiene el tiempo asignado para la siguiente pregunta."""
        tiempo_pred = self.predecir_tiempo(signo, respuestas_correctas, vidas, nivel)
        
        # Sumar 3 segundos extra según solicitud
        tiempo_pred = tiempo_pred + 3.0
        
        # Combinar predicción con historial reciente
        if len(self.historial) >= 3:
            promedio_reciente = sum(self.historial[-3:]) / 3
            tiempo_final = 0.7 * tiempo_pred + 0.3 * promedio_reciente
        else:
            tiempo_final = tiempo_pred
        
        # Aplicar límites
        tiempo_final = max(self.min_tiempo, min(self.max_tiempo, tiempo_final))
        return round(tiempo_final, 2)
    
    def registrar_respuesta(self, tiempo_usado, fue_correcta):
        """Registra el tiempo de respuesta para ajustar el sistema."""
        self.historial.append(tiempo_usado)
        
        # Mantener solo los últimos 10 registros
        if len(self.historial) > 10:
            self.historial.pop(0)
        
        # Ajustar tiempo base según rendimiento (modo difícil para la máquina)
        if fue_correcta:
            # Respuesta correcta → reducir un poco el tiempo (dificultad progresiva)
            self.tiempo_actual = max(self.min_tiempo, self.tiempo_actual - 0.3)
        # Si falla, NO aumentar tiempo (sin ayuda al jugador)
    
    def reset(self):
        """Reinicia el sistema adaptativo."""
        self.tiempo_actual = self.tiempo_base
        self.historial = []
