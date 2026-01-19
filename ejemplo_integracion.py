"""
EJEMPLO: Cómo integrar el recopilador de datos en main.py

Este archivo muestra las modificaciones necesarias en main.py
NO ejecutes este archivo directamente, solo úsalo como referencia
"""

# ============================================================================
# PASO 1: Agregar el import al inicio de main.py
# ============================================================================

# Al inicio del archivo, después de los otros imports:
from data_collector import GameDataCollector


# ============================================================================
# PASO 2: Modificar el __init__ de la clase Game
# ============================================================================

# En la clase Game, método __init__:
class Game:
    def __init__(self):
        # ... todo el código existente ...
        self.reset_game()
        
        # AGREGAR ESTO:
        # Inicializar recopilador de datos
        self.data_collector = GameDataCollector(data_dir="game_data")
        self.data_collector.start_session()
        print("[ML] Sistema de recopilación de datos activado")


# ============================================================================
# PASO 3: Modificar generate_problem()
# ============================================================================

# Buscar el método generate_problem() y modificarlo así:
def generate_problem(self):
    """Genera un nuevo problema matemático"""
    config = LEVEL_CONFIG[self.level]
    self.math_problem = MathProblem(config["num_range"])
    # Reiniciar el temporizador de la pregunta
    self.question_timer = self.question_timer_max
    
    # AGREGAR ESTO:
    # Registrar nuevo problema para ML
    self.data_collector.record_problem_start(self)


# ============================================================================
# PASO 4: Modificar process_answer()
# ============================================================================

# Buscar el método process_answer() y modificarlo así:
def process_answer(self, operation):
    """Procesa la respuesta del jugador"""
    # Establecer cooldown antes de procesar
    self.answer_cooldown = 90
    self.question_timer = self.question_timer_max
    
    # AGREGAR ESTO ANTES DE VERIFICAR LA RESPUESTA:
    is_correct = self.math_problem.check_answer(operation)
    
    # AGREGAR ESTO: Registrar respuesta para ML
    self.data_collector.record_response(operation, is_correct, self)
    
    # El resto del código sigue igual, pero usa is_correct:
    if is_correct:
        # Respuesta correcta
        self.player.correct_answers += 1
        # ... resto del código ...
    else:
        # Respuesta incorrecta
        self.player.incorrect_answers += 1
        # ... resto del código ...


# ============================================================================
# PASO 5: Modificar handle_timeout()
# ============================================================================

# Buscar el método handle_timeout() y modificarlo así:
def handle_timeout(self):
    """Maneja cuando se acaba el tiempo para responder"""
    # Establecer cooldown
    self.answer_cooldown = 90
    self.question_timer = self.question_timer_max
    
    # AGREGAR ESTO: Registrar timeout para ML
    self.data_collector.record_timeout(self)
    
    # El resto del código sigue igual:
    self.player.incorrect_answers += 1
    # ... resto del código ...


# ============================================================================
# PASO 6: Guardar datos al finalizar sesión
# ============================================================================

# Opción A: Guardar cuando el juego termina (ganar/perder)
# Buscar donde se cambia game_state a "win" o "lose":

if self.game_state == "win":
    # ... código existente ...
    # AGREGAR ESTO:
    self.data_collector.save_session()
    print("[ML] Datos de sesión guardados")

if self.game_state == "lose":
    # ... código existente ...
    # AGREGAR ESTO:
    self.data_collector.save_session()
    print("[ML] Datos de sesión guardados")


# Opción B: Guardar periódicamente (cada N problemas)
# En el método update() o process_answer(), agregar:

def process_answer(self, operation):
    # ... código existente ...
    
    # Guardar cada 20 problemas
    if len(self.data_collector.session_data) % 20 == 0:
        self.data_collector.save_session()
        print(f"[ML] Guardado automático: {len(self.data_collector.session_data)} problemas")


# Opción C: Guardar al salir del juego
# En el loop principal, cuando se cierra el juego:

def main():
    game = Game()
    running = True
    
    while running:
        # ... código del juego ...
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # AGREGAR ESTO ANTES DE SALIR:
                game.data_collector.save_session()
                print("[ML] Datos guardados al cerrar el juego")
                running = False


# ============================================================================
# PASO 7 (OPCIONAL): Mostrar estadísticas de recopilación
# ============================================================================

# Agregar un método para mostrar estadísticas en pantalla:

def draw_ml_stats(self):
    """Dibuja estadísticas de recopilación de datos (solo para debug)"""
    if len(self.data_collector.session_data) > 0:
        stats_text = f"Datos: {len(self.data_collector.session_data)} problemas"
        text = self.font_tiny.render(stats_text, True, CYAN)
        self.screen.blit(text, (SCREEN_WIDTH - 200, SCREEN_HEIGHT - 20))

# Llamar en el método draw() si quieres ver las estadísticas en tiempo real


# ============================================================================
# RESUMEN DE CAMBIOS
# ============================================================================

"""
CAMBIOS NECESARIOS EN main.py:

1. Import: from data_collector import GameDataCollector

2. En __init__:
   self.data_collector = GameDataCollector(data_dir="game_data")
   self.data_collector.start_session()

3. En generate_problem():
   self.data_collector.record_problem_start(self)

4. En process_answer():
   is_correct = self.math_problem.check_answer(operation)
   self.data_collector.record_response(operation, is_correct, self)
   # Luego usar is_correct en lugar de verificar de nuevo

5. En handle_timeout():
   self.data_collector.record_timeout(self)

6. Guardar datos:
   - Al ganar/perder: self.data_collector.save_session()
   - Al cerrar el juego: self.data_collector.save_session()
   - O periódicamente cada N problemas
"""





