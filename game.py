# -*- coding: utf-8 -*-
"""
Game - Clase principal del juego
"""

import pygame
import random
import math
import os
import json
import sys

from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS,
    BLACK, WHITE, RED, DARK_RED, GREEN, DARK_GREEN,
    BLUE, DARK_BLUE, YELLOW, GOLD, ORANGE, PURPLE, CYAN, PINK, SILVER,
    DARK_PURPLE, STAR_COLOR,
    L1_BG_START, L1_BG_END, L1_STAR,
    L2_BG_START, L2_BG_END, L2_STAR,
    L3_BG_START, L3_BG_END, L3_STAR,
    LEVEL_CONFIG, KEY_TO_OPERATION, OPERATION_TO_KEY, ENEMIES_PER_LEVEL
)
from entities import Player, Enemy, Projectile
from effects import (
    Explosion, MenuParticle, FloatingMathSymbol,
    ComboIndicator, ComboShockwave, LightningBolt, ComboTextPopup, ComboParticleBurst
)
from ui import Button, Slider, CircularButton
from systems import MathProblem, TiempoAdaptativo, SoundManager, MascotaAnimada, InfiniteMode, VictoryCelebration
from visuals import SpaceObject


class Game:
    """Clase principal del juego"""
    
    def __init__(self):
        self.fullscreen = False
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Operación Relámpago - Juego Educativo")
        self.clock = pygame.time.Clock()
        
        # === FUENTES PIXEL ART PARA ESTÉTICA RETRO ===
        # Intentar cargar la fuente pixel art PressStart2P
        pixel_font_path = os.path.join(os.path.dirname(__file__), "fonts", "PressStart2P.ttf")
        
        try:
            if os.path.exists(pixel_font_path):
                # Fuentes pixel art (tamaños más pequeños porque PressStart2P es grande)
                self.font_large = pygame.font.Font(pixel_font_path, 28)   # Título
                self.font_medium = pygame.font.Font(pixel_font_path, 16)  # Subtítulos
                self.font_small = pygame.font.Font(pixel_font_path, 12)   # Texto normal
                self.font_tiny = pygame.font.Font(pixel_font_path, 8)     # Texto pequeño
                self.font_pixel = pygame.font.Font(pixel_font_path, 32)   # Para efectos
                self.font_button = pygame.font.Font(pixel_font_path, 14)  # Botones
                print("✓ Fuente pixel art cargada correctamente")
            else:
                raise FileNotFoundError("Fuente no encontrada")
        except Exception as e:
            print(f"⚠ Usando fuentes de respaldo: {e}")
            # Fallback a fuentes del sistema
            self.font_large = pygame.font.Font(None, 56)
            self.font_medium = pygame.font.Font(None, 36)
            self.font_small = pygame.font.Font(None, 24)
            self.font_tiny = pygame.font.Font(None, 18)
            self.font_pixel = pygame.font.Font(None, 72)
            self.font_button = pygame.font.Font(None, 50)
        self.running = True
        self.game_state = "menu"  # menu, controls, settings, level_intro, playing, paused, pre_victory, victory, lose
        self.sound_manager = SoundManager()
        self.level_intro_timer = 0
        self.menu_blink = 0
        self.sound_volume = 1.0  # Volumen de sonido (0.0 a 1.0)
        self.music_volume = 0.1  # Volumen de música (0.0 a 1.0)
        self.paused = False
        
        # Variables para modo infinito con tiempo adaptativo ML
        self.modo_infinito = False
        self.tiempo_adaptativo = None
        self.infinite_mode = None  # Instancia de InfiniteMode para manejo de oleadas
        self.victory_celebration = None  # Animación de victoria

        
        # Inicializar botones del menú
        self.menu_buttons = []
        self.controls_buttons = []
        self.settings_buttons = []
        self.pause_buttons = []
        self.sliders = []
        self._init_menu_buttons()
        
        self.sliders = []
        self._init_menu_buttons()
        
        # Generar estrellas de fondo (fijas)
        self.stars = []
        for _ in range(100):
            self.stars.append((
                random.randint(0, SCREEN_WIDTH),
                random.randint(0, SCREEN_HEIGHT),
                random.choice([1, 1, 1, 2, 2, 3]),  # tamaño
                random.randint(50, 255)  # brillo
            ))
        
        # === OPTIMIZACIÓN: Cache de fondos prerenderizados ===
        self.cached_backgrounds = {}
        self._cache_all_backgrounds()
        
        # Objetos espaciales decorativos
        self.space_objects = []
        
        # Explosiones y efectos visuales
        self.explosions = []
        
        # Sistema de COMBO
        self.combo_streak = 0           # Contador de respuestas correctas consecutivas
        self.combo_threshold = 5        # Umbral para activar combo attack
        self.combo_indicator = ComboIndicator()  # UI del combo
        self.combo_effects = []         # Lista de efectos visuales activos
        self.screen_shake = 0           # Duración del screen shake
        self.screen_shake_intensity = 0 # Intensidad del shake
        self.screen_flash = 0           # Duración del flash de pantalla
        
        # Partículas del menú para animación dinámica - MÁS IMPACTANTE
        self.menu_particles = []
        # Estrellas fugaces - MUCHAS MÁS
        for _ in range(15):
            self.menu_particles.append(MenuParticle('star'))
        # Polvo cósmico
        for _ in range(50):
            self.menu_particles.append(MenuParticle('dust'))
        # Chispas de energía - MUCHAS MÁS
        for _ in range(25):
            self.menu_particles.append(MenuParticle('spark'))
        
        # Símbolos matemáticos flotantes - MÁS GRANDES Y VISIBLES
        self.floating_math_symbols = []
        for _ in range(12):
            symbol = FloatingMathSymbol()
            symbol.y = random.randint(100, SCREEN_HEIGHT - 100)
            self.floating_math_symbols.append(symbol)
        
        # Temporizador para disparos automáticos del menú
        self.menu_shoot_timer = 0
        self.menu_projectiles = []
        self.menu_explosions = []
        
        # SCREEN SHAKE para impacto visual
        self.menu_screen_shake = 0
        self.menu_shake_intensity = 0
        
        # Cargar imágenes del menú
        self.menu_left_img = None
        self.menu_right_img = None
        try:
            if os.path.exists("menu_left.png"):
                self.menu_left_img = pygame.image.load("menu_left.png").convert_alpha()
                # Escalar si es necesario (ajustar tamaño según diseño)
                self.menu_left_img = pygame.transform.scale(self.menu_left_img, (150, 150))
            
            if os.path.exists("menu_right.png"):
                self.menu_right_img = pygame.image.load("menu_right.png").convert_alpha()
                # Escalar si es necesario
                self.menu_right_img = pygame.transform.scale(self.menu_right_img, (150, 150))
        except Exception as e:
            print(f"Advertencia: No se pudieron cargar las imágenes del menú: {e}")
        
        self.reset_game()
        
        # Iniciar música del menú (desde 0.4s)
        self.sound_manager.play_menu_music(self.music_volume)
    
    def _init_menu_buttons(self):
        """Inicializa los botones del menú principal"""
        button_width = 380
        button_height = 65
        button_spacing = 90
        # Centrar verticalmente los 2 botones principales
        total_buttons_height = button_height * 2 + button_spacing
        start_y = (SCREEN_HEIGHT // 2) - (total_buttons_height // 2) + 50
        center_x = SCREEN_WIDTH // 2
        
        # Colores monocromáticos
        BTN_COLOR = (70, 70, 80)
        BTN_HOVER = (120, 120, 130)
        
        # Botón Jugar (Modo Normal)
        self.menu_buttons.append(Button(
            center_x - button_width // 2,
            start_y,
            button_width,
            button_height,
            "MODO NIVELES",
            self.font_button,
            color=BTN_COLOR,
            hover_color=BTN_HOVER,
            icon="play"
        ))
        
        # Botón Modo Infinito (NUEVO - con ML adaptativo)
        self.menu_buttons.append(Button(
            center_x - button_width // 2,
            start_y + button_spacing + button_height,
            button_width,
            button_height,
            "MODO INFINITO",
            self.font_button,
            color=BTN_COLOR,
            hover_color=BTN_HOVER,
            icon="infinity"
        ))
        
        # Botones circulares en el lado derecho (disposición vertical)
        self.circular_buttons = []
        circle_radius = 28
        circle_spacing = 70
        circle_x = SCREEN_WIDTH - 50
        circle_start_y = SCREEN_HEIGHT // 2 - circle_spacing
        
        # Botón Controles (gamepad)
        self.circular_buttons.append(CircularButton(
            circle_x,
            circle_start_y,
            circle_radius,
            "gamepad",
            tooltip="Controles",
            color=(0, 200, 255)  # Cian
        ))
        
        # Botón Sonido (speaker)
        self.circular_buttons.append(CircularButton(
            circle_x,
            circle_start_y + circle_spacing,
            circle_radius,
            "sound",
            tooltip="Sonido",
            color=(255, 200, 100)  # Naranja
        ))
        
        # Botón Salir (power)
        self.circular_buttons.append(CircularButton(
            circle_x,
            circle_start_y + circle_spacing * 2,
            circle_radius,
            "power",
            tooltip="Salir",
            color=(255, 100, 100)  # Rojo
        ))

        
        # Botón Volver (para controles y settings) - posicionado más abajo
        back_button_controls = Button(
            center_x - button_width // 2,
            SCREEN_HEIGHT - 90,
            button_width,
            button_height,
            "VOLVER",
            self.font_button,
            color=BTN_COLOR,
            hover_color=BTN_HOVER,
            icon="back"
        )
        back_button_settings = Button(
            center_x - button_width // 2,
            SCREEN_HEIGHT - 90,
            button_width,
            button_height,
            "VOLVER",
            self.font_button,
            color=BTN_COLOR,
            hover_color=BTN_HOVER,
            icon="back"
        )
        self.controls_buttons.append(back_button_controls)
        self.settings_buttons.append(back_button_settings)
        
        # Botones del menú de pausa
        pause_start_y = 180
        self.pause_buttons.append(Button(
            center_x - button_width // 2,
            pause_start_y,
            button_width,
            button_height,
            "REANUDAR",
            self.font_button,
            color=BTN_COLOR,
            hover_color=BTN_HOVER,
            icon="resume"
        ))
        self.pause_buttons.append(Button(
            center_x - button_width // 2,
            pause_start_y + button_spacing,
            button_width,
            button_height,
            "CONTROLES",
            self.font_button,
            color=BTN_COLOR,
            hover_color=BTN_HOVER,
            icon="controls"
        ))
        self.pause_buttons.append(Button(
            center_x - button_width // 2,
            pause_start_y + button_spacing * 2,
            button_width,
            button_height,
            "CONFIGURAR SONIDO",
            self.font_button,
            color=BTN_COLOR,
            hover_color=BTN_HOVER,
            icon="settings"
        ))
        self.pause_buttons.append(Button(
            center_x - button_width // 2,
            pause_start_y + button_spacing * 3,
            button_width,
            button_height,
            "SALIR AL MENÚ",
            self.font_button,
            color=BTN_COLOR,
            hover_color=BTN_HOVER,
            icon="menu"
        ))
        
        # Sliders para configuración de sonido
        slider_width = 500
        slider_height = 8
        slider_x = center_x - slider_width // 2
        music_slider_y = 220
        sound_slider_y = 340
        
        self.music_slider = Slider(
            slider_x, music_slider_y, slider_width, slider_height,
            min_value=0.0, max_value=1.0, initial_value=self.music_volume,
            color=(120, 120, 140)
        )
        self.sound_slider = Slider(
            slider_x, sound_slider_y, slider_width, slider_height,
            min_value=0.0, max_value=1.0, initial_value=self.sound_volume,
            color=(120, 140, 120)
        )
    
    def _sync_sliders(self):
        """Sincroniza los valores de los sliders con las variables de volumen"""
        if hasattr(self, 'music_slider'):
            self.music_slider.value = self.music_volume
        if hasattr(self, 'sound_slider'):
            self.sound_slider.value = self.sound_volume
    
    def toggle_fullscreen(self):
        """Alterna entre modo ventana y pantalla completa"""
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            # Obtener resolución de pantalla completa
            info = pygame.display.Info()
            self.screen = pygame.display.set_mode(
                (info.current_w, info.current_h),
                pygame.FULLSCREEN
            )
        else:
            # Volver a modo ventana
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    
    def reset_game(self):
        """Reinicia el juego"""
        # Detener el sonido final si está reproduciéndose
        self.sound_manager.stop_final_sound()
        
        self.level = 1
        self.player = Player(SCREEN_WIDTH // 2 - 25, SCREEN_HEIGHT - 80)
        self.enemies = []  # Lista de enemigos (múltiples)
        self.player_projectiles = []
        self.enemy_projectiles = []
        self.math_problem = None
        self.feedback_text = ""
        self.feedback_timer = 0
        self.answer_cooldown = 0  # Cooldown entre respuestas (en frames)
        self.question_timer = 600  # Temporizador de 10 segundos (600 frames a 60 FPS)
        self.question_timer_max = 600  # Tiempo máximo en frames
        self.explosions = []
        
        # Resetear sistema de combo
        self.combo_streak = 0
        self.combo_effects = []
        
        # Mascota animada (robot que da ánimos)
        self.mascota = MascotaAnimada()
        
        self.generate_enemies()
        self.generate_problem()
        self.generate_space_objects()
    
    def generate_enemies(self):
        """Genera múltiples enemigos según el nivel actual"""
        config = LEVEL_CONFIG[self.level]
        num_enemies = ENEMIES_PER_LEVEL[self.level]
        self.enemies = []
        
        # Distribuir enemigos horizontalmente
        spacing = SCREEN_WIDTH // (num_enemies + 1)
        start_x = spacing
        
        for i in range(num_enemies):
            # Variar ligeramente la posición Y para más dinamismo
            y_offset = random.randint(-20, 20)
            enemy = Enemy(
                start_x + i * spacing - 30,
                100 + y_offset,  # Bajado para no tapar la UI superior
                config["enemy_hp"],
                config["enemy_speed"],
                self.level
            )
            # Variar dirección inicial
            enemy.direction = random.choice([-1, 1])
            enemy.move_counter = random.randint(0, 30)
            self.enemies.append(enemy)
    
    def generate_enemies_infinite(self, wave_config):
        """Genera enemigos para modo infinito con configuración escalable"""
        num_enemies = wave_config["num_enemies"]
        enemy_hp = wave_config["enemy_hp"]
        enemy_speed = wave_config["enemy_speed"]
        visual_level = wave_config["visual_level"]
        
        self.enemies = []
        
        # Distribuir enemigos horizontalmente
        spacing = SCREEN_WIDTH // (num_enemies + 1)
        start_x = spacing
        
        for i in range(num_enemies):
            # Variar ligeramente la posición Y para más dinamismo
            y_offset = random.randint(-20, 20)
            enemy = Enemy(
                start_x + i * spacing - 30,
                100 + y_offset,
                enemy_hp,
                enemy_speed,
                visual_level  # Usar visual_level para el diseño del enemigo
            )
            # Variar dirección inicial
            enemy.direction = random.choice([-1, 1])
            enemy.move_counter = random.randint(0, 30)
            self.enemies.append(enemy)
    
    def generate_space_objects(self):
        """Genera objetos espaciales decorativos según el nivel (OPTIMIZADO)"""
        self.space_objects = []
        
        # Asteroides (reducido en nivel 3 para mejor rendimiento)
        asteroid_counts = {1: 5, 2: 6, 3: 6}  # Era 5, 8, 10
        for _ in range(asteroid_counts.get(self.level, 5)):
            self.space_objects.append(SpaceObject(
                'asteroid',
                random.randint(0, SCREEN_WIDTH),
                random.randint(-200, SCREEN_HEIGHT),
                self.level
            ))
        
        # Planetas (menos frecuentes)
        for _ in range(2 if self.level >= 2 else 1):
            self.space_objects.append(SpaceObject(
                'planet',
                random.randint(0, SCREEN_WIDTH),
                random.randint(-300, 0),
                self.level
            ))
        
        # Nebulosas (solo nivel 2 y 3, reducido)
        if self.level >= 2:
            nebula_count = 2 if self.level == 3 else 3  # Reducido en nivel 3
            for _ in range(nebula_count):
                self.space_objects.append(SpaceObject(
                    'nebula',
                    random.randint(0, SCREEN_WIDTH),
                    random.randint(-400, SCREEN_HEIGHT),
                    self.level
                ))
        
        # Cometas (solo nivel 3, reducido a 1)
        if self.level == 3:
            for _ in range(1):  # Reducido de 2 a 1
                self.space_objects.append(SpaceObject(
                    'comet',
                    random.randint(0, SCREEN_WIDTH),
                    random.randint(-500, -100),
                    self.level
                ))
    
    def generate_problem(self):
        """Genera un nuevo problema matemático"""
        config = LEVEL_CONFIG[self.level]
        self.math_problem = MathProblem(config["num_range"])
        
        # En modo infinito, usar tiempo adaptativo ML
        if self.modo_infinito and self.tiempo_adaptativo:
            # Predecir tiempo usando el modelo ML
            tiempo_segundos = self.tiempo_adaptativo.obtener_tiempo(
                self.math_problem.operation,
                self.player.correct_answers,
                self.player.lives,
                self.level
            )
            # Convertir segundos a frames (FPS = 60)
            self.question_timer_max = int(tiempo_segundos * FPS)
            self.question_timer = self.question_timer_max
        else:
            # Modo normal: timer fijo
            self.question_timer = self.question_timer_max

    
    def handle_input(self, keys, events):
        """Maneja la entrada del usuario"""
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = False
        mouse_down = pygame.mouse.get_pressed()[0]
        
        # Procesar eventos
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Click izquierdo
                    mouse_clicked = True
            
            if event.type == pygame.KEYDOWN:
                # Tecla F11 para alternar pantalla completa (funciona en cualquier estado)
                if event.key == pygame.K_F11:
                    self.toggle_fullscreen()
                    continue
                
                # Durante el juego - ESC para pausar (verificar primero para no interferir con WASD)
                if self.game_state == "playing":
                    if event.key == pygame.K_ESCAPE:
                        self.game_state = "paused"
                        self.paused = True
                        continue  # Continuar para no procesar otras teclas
                    # Verificar teclas de operaciones SOLO si estamos jugando
                    if self.answer_cooldown == 0 and event.key in KEY_TO_OPERATION:
                        operation = KEY_TO_OPERATION[event.key]
                        self.process_answer(operation)
                        continue
                
                # Menú principal - navegación con teclado
                if self.game_state == "menu":
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    continue
                
                # Menú de pausa - ESC para reanudar
                if self.game_state == "paused":
                    if event.key == pygame.K_ESCAPE:
                        self.game_state = "playing"
                        self.paused = False
                    continue
                
                # Pantallas de controles y settings - ESC para volver
                if self.game_state in ["controls", "settings"]:
                    if event.key == pygame.K_ESCAPE:
                        if self.paused:
                            self.game_state = "paused"
                        else:
                            self.game_state = "menu"
                    continue
                
                # Introducción de nivel
                if self.game_state == "level_intro":
                    if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                        self.game_state = "playing"
                        self.paused = False
                        # La música continúa desde el nivel anterior, no se reinicia
                    continue
                
                # Tecla R para reiniciar
                if event.key == pygame.K_r and self.game_state in ["victory", "lose"]:
                    # Detener el sonido final antes de volver al menú
                    self.sound_manager.stop_final_sound()
                    self.game_state = "menu"
                    self.sound_manager.play_menu_music(self.music_volume)
                    self.paused = False
                    continue
        
        # Manejar clicks en botones del menú
        if self.game_state == "menu":
            # Botones principales rectangulares
            for i, button in enumerate(self.menu_buttons):
                button.update(mouse_pos)
                if button.is_clicked(mouse_pos, mouse_clicked):
                    if i == 0:  # Jugar (Modo Normal)
                        self.modo_infinito = False
                        self.tiempo_adaptativo = None
                        self.game_state = "level_intro"
                        self.level_intro_timer = 180
                        self.level = 1
                        self.reset_game()
                        self.sound_manager.change_level_music(1, self.music_volume)
                    elif i == 1:  # MODO INFINITO (con ML adaptativo)
                        self.modo_infinito = True
                        self.tiempo_adaptativo = TiempoAdaptativo()
                        self.infinite_mode = InfiniteMode()
                        self.game_state = "level_intro"
                        self.level_intro_timer = 180
                        # Obtener primera oleada
                        wave_config = self.infinite_mode.next_wave()
                        self.level = wave_config["visual_level"]
                        self.reset_game()
                        # Regenerar enemigos con config de oleada infinita
                        self.generate_enemies_infinite(wave_config)
                        self.sound_manager.change_level_music(self.level, self.music_volume)
            
            # Botones circulares (Controles, Sonido, Salir)
            for i, btn in enumerate(self.circular_buttons):
                btn.update(mouse_pos)
                if btn.is_clicked(mouse_pos, mouse_clicked):
                    if i == 0:  # Controles
                        self.game_state = "controls"
                    elif i == 1:  # Sonido
                        self.game_state = "settings"
                    elif i == 2:  # Salir
                        self.running = False

        
        # Manejar clicks en botones de controles
        elif self.game_state == "controls":
            for button in self.controls_buttons:
                button.update(mouse_pos)
                if button.is_clicked(mouse_pos, mouse_clicked):
                    if button.text == "VOLVER":
                        self.game_state = "menu"
        
        # Manejar clicks en botones de settings y sliders
        elif self.game_state == "settings":
            # Actualizar sliders (importante: hacerlo antes de los botones)
            self.music_slider.update(mouse_pos, mouse_down, mouse_clicked)
            self.sound_slider.update(mouse_pos, mouse_down, mouse_clicked)
            self.music_volume = self.music_slider.value
            self.sound_volume = self.sound_slider.value
            pygame.mixer.music.set_volume(self.music_volume)
            
            for button in self.settings_buttons:
                button.update(mouse_pos)
                if button.is_clicked(mouse_pos, mouse_clicked):
                    if button.text == "VOLVER":
                        if self.paused:
                            self.game_state = "paused"
                        else:
                            self.game_state = "menu"
        
        # Manejar clicks en botones del menú de pausa
        elif self.game_state == "paused":
            for i, button in enumerate(self.pause_buttons):
                button.update(mouse_pos)
                if button.is_clicked(mouse_pos, mouse_clicked):
                    if i == 0:  # Reanudar
                        self.game_state = "playing"
                        self.paused = False
                    elif i == 1:  # Controles
                        self.game_state = "controls"
                    elif i == 2:  # Configurar Sonido
                        self.game_state = "settings"
                        self._sync_sliders()
                    elif i == 3:  # Salir al Menú
                        self.game_state = "menu"
                        self.sound_manager.change_level_music(1, self.music_volume) # Reiniciar música
                        self.sound_manager.play_menu_music(self.music_volume)
        
        # Manejar pantalla de victoria o game over
        elif self.game_state in ["victory", "lose"]:
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        # Detener el sonido final antes de reiniciar o volver al menú
                        self.sound_manager.stop_final_sound()
                        # Reiniciar juego
                        self.reset_game()
                        # Si era victoria y reinicia, el nivel vuelve a 1
                        self.game_state = "level_intro"
                        self.level_intro_timer = 180
                        self.sound_manager.change_level_music(self.level, self.music_volume)
                    elif event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                        # Detener el sonido final antes de volver al menú
                        self.sound_manager.stop_final_sound()
                        # Volver al menú
                        self.game_state = "menu"
                        self.sound_manager.play_menu_music(self.music_volume)

                        self.paused = False
    
    def process_answer(self, operation):
        """Procesa la respuesta del jugador"""
        # Calcular tiempo de respuesta ANTES de reiniciar el temporizador
        # question_timer_max y question_timer están en frames → convertir a segundos
        elapsed_frames = self.question_timer_max - self.question_timer
        response_time = max(0.0, elapsed_frames / FPS)
        
        # Capturar tiempo total de la pregunta ANTES de reiniciar
        total_time = self.question_timer_max / FPS  # Tiempo total en segundos
        
        # Obtener la tecla presionada
        key_pressed = OPERATION_TO_KEY.get(operation, "UNKNOWN")

        # Establecer cooldown antes de procesar (evita múltiples procesamientos)
        self.answer_cooldown = 90  # 1.5 segundos a 60 FPS
        
        # Reiniciar el temporizador de la pregunta
        self.question_timer = self.question_timer_max
        
        if self.math_problem.check_answer(operation):
            # Respuesta correcta
            self.player.correct_answers += 1
            self.player.score += 10
            self.feedback_text = "¡CORRECTO! +10"
            self.feedback_timer = 60
            self.feedback_color = GREEN
            self.sound_manager.play_sound('correct', 0.3, self.sound_volume)
            
            # Incrementar combo streak
            self.combo_streak += 1
            self.combo_indicator.update(self.combo_streak)
            
            # Verificar si se activa el COMBO ATTACK
            if self.combo_streak >= self.combo_threshold:
                self.trigger_combo_attack()
                self.combo_streak = 0  # Resetear después de usar
            else:
                # Disparo normal a un solo enemigo
                if self.enemies:
                    target_enemy = None
                    for enemy in self.enemies:
                        if not enemy.is_dead():
                            target_enemy = enemy
                            break
                    
                    if target_enemy:
                        start_x = self.player.x + self.player.width // 2
                        start_y = self.player.y
                        projectile = Projectile(
                            start_x, 
                            start_y, 
                            -8,
                            GREEN, 
                            True,
                            target_enemy
                        )
                        self.player_projectiles.append(projectile)
                        self.sound_manager.play_sound('shoot', 0.2, self.sound_volume)
            
            # Activar celebración de la mascota y obtener bonus
            bonus = self.mascota.celebrar()
            if bonus > 0:
                self.player.score += bonus
                self.feedback_text = f"¡CORRECTO! +10 (BONUS +{bonus})"
                
        else:
            # Respuesta incorrecta
            self.player.incorrect_answers += 1
            self.player.score = max(0, self.player.score - 5)
            self.feedback_text = "¡INCORRECTO!"
            self.feedback_timer = 60
            self.feedback_color = RED
            self.sound_manager.play_sound('wrong', 0.3, self.sound_volume)
            
            # RESETEAR COMBO
            self.combo_streak = 0
            self.combo_indicator.update(0)
            
            # Resetear racha de la mascota
            self.mascota.reset_streak()
            
            # Los enemigos atacan
            if self.enemies:
                enemy = random.choice(self.enemies)
                start_x = enemy.x + enemy.width // 2
                start_y = enemy.y + enemy.height
                projectile = Projectile(
                    start_x,
                    start_y,
                    8,
                    RED,
                    False,
                    None,
                    self.player
                )
                self.enemy_projectiles.append(projectile)
                self.sound_manager.play_sound('shoot', 0.15, self.sound_volume)
        
        # Registrar resultado en archivo JSON
        self._log_answer_result(operation, response_time, total_time, key_pressed)
        
        # Registrar respuesta en el sistema de tiempo adaptativo (modo infinito)
        if self.modo_infinito and self.tiempo_adaptativo:
            fue_correcta = self.math_problem.check_answer(operation)
            self.tiempo_adaptativo.registrar_respuesta(response_time, fue_correcta)

    def trigger_combo_attack(self):
        """Activa el ataque de combo masivo que daña a TODOS los enemigos"""
        # Bonus de puntos por combo
        combo_bonus = 50
        self.player.score += combo_bonus
        self.feedback_text = f"⚡ COMBO x5! ⚡ +{combo_bonus}"
        self.feedback_timer = 120  # Más tiempo para el mensaje de combo
        self.feedback_color = GOLD
        
        # Posición del jugador para los efectos
        player_center_x = self.player.x + self.player.width // 2
        player_center_y = self.player.y + self.player.height // 2
        
        # Screen shake y flash
        self.screen_shake = 30
        self.screen_shake_intensity = 12
        self.screen_flash = 15
        
        # Crear efectos visuales
        # 1. Onda expansiva desde el jugador
        shockwave = ComboShockwave(player_center_x, player_center_y)
        self.combo_effects.append(shockwave)
        
        # 2. Explosión de partículas
        particles = ComboParticleBurst(player_center_x, player_center_y)
        self.combo_effects.append(particles)
        
        # 3. Texto de combo
        text_y = SCREEN_HEIGHT // 2 - 50
        combo_text = ComboTextPopup(SCREEN_WIDTH // 2, text_y)
        self.combo_effects.append(combo_text)
        
        # 4. Dañar a TODOS los enemigos y crear rayos hacia cada uno
        for enemy in self.enemies:
            if not enemy.is_dead():
                # Crear rayo hacia el enemigo
                enemy_center_x = enemy.x + enemy.width // 2
                enemy_center_y = enemy.y + enemy.height // 2
                lightning = LightningBolt(
                    player_center_x, player_center_y,
                    enemy_center_x, enemy_center_y
                )
                self.combo_effects.append(lightning)
                
                # Dañar al enemigo
                enemy.take_damage(2)  # Daño doble
                
                # Crear explosión en el enemigo
                from effects import Explosion
                explosion = Explosion(enemy_center_x, enemy_center_y)
                self.explosions.append(explosion)
        
        # Sonido épico
        # Si existe el sonido especial de combo, usarlo con prioridad y volumen alto
        if 'laser_combo' in self.sound_manager.sounds and self.sound_manager.sounds['laser_combo']:
            self.sound_manager.play_sound('laser_combo', 1.0, self.sound_volume)
        else:
            # Fallback a combinación de sonidos
            self.sound_manager.play_sound('correct', 0.8, self.sound_volume)
            self.sound_manager.play_sound('shoot', 0.5, self.sound_volume)
        
        # Actualizar indicador de combo (resetear visualmente)
        self.combo_indicator.update(0)


    def _log_answer_result(self, operation, response_time, total_time, key_pressed):
        """Registra datos de cada respuesta en resultados.json"""
        try:
            # Manejar caso de timeout (operation puede ser None)
            signo_operacional = self.math_problem.operation if operation is not None else "TIMEOUT"
            
            entry = {
                "nivel_actual": self.level,
                "vidas_actuales": self.player.lives,
                "puntaje_actual": self.player.score,
                "respuestas_correctas_acumuladas": self.player.correct_answers,
                "tiempo_respuesta_pregunta": response_time,
                "tiempo_total_pregunta": total_time,
                "tecla_presionada": key_pressed,
                "numero_1": self.math_problem.num1,
                "numero_2": self.math_problem.num2,
                "signo_operacional": signo_operacional,
                "resultado_operacional": self.math_problem.answer,
            }

            # Cargar datos existentes si el archivo ya existe
            resultados = []
            if os.path.exists("resultados.json"):
                with open("resultados.json", "r", encoding="utf-8") as f:
                    try:
                        resultados = json.load(f)
                    except json.JSONDecodeError:
                        resultados = []

            resultados.append(entry)

            # Guardar lista actualizada
            with open("resultados.json", "w", encoding="utf-8") as f:
                json.dump(resultados, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error al guardar resultados en resultados.json: {e}")
    
    def handle_timeout(self):
        """Maneja cuando se acaba el tiempo para responder"""
        # Capturar tiempo total ANTES de reiniciar
        total_time = self.question_timer_max / FPS  # Tiempo total en segundos
        response_time = total_time  # Usó todo el tiempo disponible
        
        # Establecer cooldown
        self.answer_cooldown = 90
        
        # Reiniciar temporizador
        self.question_timer = self.question_timer_max
        
        # El enemigo ataca por tiempo agotado
        self.player.incorrect_answers += 1
        # Restar 5 puntos, sin bajar de 0
        self.player.score = max(0, self.player.score - 5)
        self.feedback_text = "¡TIEMPO AGOTADO!"
        self.feedback_timer = 60
        self.feedback_color = RED
        self.sound_manager.play_sound('wrong', 0.3, self.sound_volume)
        
        # Resetear racha de la mascota
        self.mascota.reset_streak()
        
        # Los enemigos disparan - disparos dirigidos al jugador
        if self.enemies:
            # Solo un enemigo dispara
            enemy = random.choice(self.enemies)
            # Crear proyectil dirigido al jugador
            start_x = enemy.x + enemy.width // 2
            start_y = enemy.y + enemy.height
            projectile = Projectile(
                start_x,
                start_y,
                8,  # Velocidad
                RED,
                False,  # Es disparo enemigo
                None,  # Sin objetivo enemigo
                self.player  # Objetivo: jugador
            )
            self.enemy_projectiles.append(projectile)
            self.sound_manager.play_sound('shoot', 0.15, self.sound_volume)
        
        # Registrar resultado en archivo JSON (timeout = sin tecla presionada)
        self._log_answer_result(None, response_time, total_time, "TIMEOUT")
        
        # NO reducir vida aquí - solo cuando el proyectil golpee al jugador
    
    def update_menu_simulation(self):
        """Simula el juego en el fondo del menú con animación dinámica"""
        # Mover jugador suavemente (piloto automático con movimiento más dinámico)
        time_ms = pygame.time.get_ticks()
        self.player.x += math.sin(time_ms * 0.001) * 2
        self.player.y = SCREEN_HEIGHT - 100 + math.sin(time_ms * 0.002) * 10
        # Mantener jugador en pantalla
        self.player.x = max(0, min(SCREEN_WIDTH - self.player.width, self.player.x))
        
        # Actualizar enemigos (movimiento normal)
        for enemy in self.enemies:
            enemy.update()
            
            # Si tocan los bordes, cambiar dirección
            if enemy.x <= 0 or enemy.x >= SCREEN_WIDTH - enemy.width:
                enemy.speed *= -1
        
        # === SISTEMA DE BATALLA SIMULADA - MÁS INTENSO ===
        self.menu_shoot_timer += 1
        
        # Actualizar screen shake
        if self.menu_screen_shake > 0:
            self.menu_screen_shake -= 1
            self.menu_shake_intensity *= 0.9
        
        # Jugador dispara automáticamente cada 25 frames (MÁS RÁPIDO)
        if self.menu_shoot_timer % 25 == 0 and self.enemies:
            target_enemy = random.choice(self.enemies)
            projectile = Projectile(
                self.player.x + self.player.width // 2,
                self.player.y,
                -12,  # Más rápido
                GREEN,
                True,
                target_enemy
            )
            self.menu_projectiles.append(projectile)
        
        # Enemigos disparan aleatoriamente cada 40 frames (MÁS FRECUENTE)
        if self.menu_shoot_timer % 40 == 0 and self.enemies:
            shooter = random.choice(self.enemies)
            projectile = Projectile(
                shooter.x + shooter.width // 2,
                shooter.y + shooter.height,
                10,  # Más rápido
                RED,
                False,
                None,
                self.player
            )
            self.menu_projectiles.append(projectile)
        
        # Actualizar proyectiles del menú
        for projectile in self.menu_projectiles[:]:
            projectile.update()
            
            # Verificar colisiones con enemigos (proyectiles del jugador)
            if projectile.is_player_shot:
                for enemy in self.enemies[:]:
                    if projectile.get_rect().colliderect(
                        pygame.Rect(enemy.x, enemy.y, enemy.width, enemy.height)
                    ):
                        # Crear explosión GRANDE
                        self.menu_explosions.append(Explosion(
                            enemy.x + enemy.width // 2,
                            enemy.y + enemy.height // 2
                        ))
                        # SCREEN SHAKE en explosión
                        self.menu_screen_shake = 15
                        self.menu_shake_intensity = 8
                        # Remover proyectil
                        if projectile in self.menu_projectiles:
                            self.menu_projectiles.remove(projectile)
                        # Dañar enemigo
                        enemy.take_damage()
                        if enemy.is_dead():
                            self.enemies.remove(enemy)
                            # Explosión extra al morir
                            self.menu_screen_shake = 25
                            self.menu_shake_intensity = 15
                        break
            
            # Verificar colisión con jugador (proyectiles enemigos) - solo visual, sin daño
            elif not projectile.is_player_shot:
                if projectile.get_rect().colliderect(
                    pygame.Rect(self.player.x, self.player.y, self.player.width, self.player.height)
                ):
                    # Explosión visual pequeña
                    self.menu_explosions.append(Explosion(
                        self.player.x + self.player.width // 2,
                        self.player.y + self.player.height // 2
                    ))
                    if projectile in self.menu_projectiles:
                        self.menu_projectiles.remove(projectile)
            
            # Eliminar proyectiles fuera de pantalla
            if projectile.is_off_screen() and projectile in self.menu_projectiles:
                self.menu_projectiles.remove(projectile)
        
        # Actualizar explosiones del menú
        for explosion in self.menu_explosions[:]:
            explosion.update()
            if explosion.is_dead():
                self.menu_explosions.remove(explosion)
        
        # Regenerar enemigos si hay muy pocos (para mantener la acción)
        if len(self.enemies) < 2:
            # Agregar nuevos enemigos
            for i in range(3):
                enemy = Enemy(
                    random.randint(100, SCREEN_WIDTH - 100),
                    random.randint(50, 150),
                    2,  # HP bajo para que mueran rápido
                    random.uniform(1, 2),
                    random.randint(1, 3)  # Nivel aleatorio para variedad visual
                )
                enemy.direction = random.choice([-1, 1])
                self.enemies.append(enemy)
        
        # === ACTUALIZAR PARTÍCULAS DEL MENÚ ===
        for particle in self.menu_particles:
            particle.update()
        
        # === ACTUALIZAR SÍMBOLOS MATEMÁTICOS ===
        for symbol in self.floating_math_symbols:
            symbol.update()
        
        # Actualizar objetos espaciales (estrellas, planetas)
        for obj in self.space_objects:
            obj.update()
            
        # Generar nuevos objetos espaciales ocasionalmente
        if random.random() < 0.02:
            self.generate_space_objects()

    def update(self):
        """Actualiza el estado del juego"""
        # Actualizar menú
        if self.game_state == "menu":
            self.menu_blink = (self.menu_blink + 1) % 60
            self.update_menu_simulation()
            return
        
        # Actualizar controles/settings
        if self.game_state == "controls":
            return
        elif self.game_state == "settings":
            # Sincronizar sliders antes de actualizar
            self._sync_sliders()
            # Los sliders se actualizan en handle_input
            mouse_pos = pygame.mouse.get_pos()
            mouse_down = pygame.mouse.get_pressed()[0]
            self.music_slider.update(mouse_pos, mouse_down, False)
            self.sound_slider.update(mouse_pos, mouse_down, False)
            self.music_volume = self.music_slider.value
            self.sound_volume = self.sound_slider.value
            pygame.mixer.music.set_volume(self.music_volume)
            return
        elif self.game_state == "paused":
            return
        
        # Actualizar introducción de nivel
        if self.game_state == "level_intro":
            self.level_intro_timer -= 1
            if self.level_intro_timer <= 0:
                self.game_state = "playing"
                # La música continúa desde el nivel anterior, no se reinicia
            return
        # Actualizar pre-victoria (animación de celebración)
        if self.game_state == "pre_victory":
            # Actualizar explosiones restantes
            for explosion in self.explosions[:]:
                explosion.update()
                if explosion.is_dead():
                    self.explosions.remove(explosion)
            
            # Actualizar efectos de combo
            for effect in self.combo_effects[:]:
                effect.update()
                if effect.is_dead():
                    self.combo_effects.remove(effect)
            
            # Actualizar celebración de victoria
            if self.victory_celebration:
                self.victory_celebration.update()
                if self.victory_celebration.is_finished():
                    self.game_state = "victory"
                    self.sound_manager.stop_background_music()
            return
        
        if self.game_state != "playing":
            return
        
        # Actualizar jugador
        self.player.update()
        
        # Movimiento del jugador con flechas
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.player.move_left()
        if keys[pygame.K_RIGHT]:
            self.player.move_right()
        self.player.apply_movement()
        
        # Actualizar mascota animada
        self.mascota.update()
        
        # Actualizar enemigos
        for enemy in self.enemies[:]:
            enemy.update()
            if enemy.is_dead():
                # Crear explosión final si no se creó antes
                explosion = Explosion(
                    enemy.x + enemy.width // 2,
                    enemy.y + enemy.height // 2
                )
                self.explosions.append(explosion)
                
                # Remover enemigo
                self.enemies.remove(enemy)
                
                # Verificar si todos murieron
                if len(self.enemies) == 0:
                    self.player_projectiles.clear()
                    
                    if self.modo_infinito and self.infinite_mode:
                        # Regenerar en modo infinito con dificultad escalable
                        wave_config = self.infinite_mode.next_wave()
                        self.level = wave_config["visual_level"]
                        self.level_intro_timer = 90
                        self.game_state = "level_intro"
                        self.generate_enemies_infinite(wave_config)
                        self.generate_space_objects()
                        # Cambiar música si el nivel visual cambió
                        self.sound_manager.change_level_music(self.level, self.music_volume)
                    else:
                        # Lógica normal de niveles
                        if self.level < 3:
                            self.level_intro_timer = 180
                            self.game_state = "level_intro"
                            self.level += 1
                            self.generate_enemies()
                            self.generate_space_objects()
                            self.sound_manager.change_level_music(self.level, self.music_volume)
                        else:
                            # Fin del juego - ir a pre_victory para mostrar animación
                            self.game_state = "pre_victory"
                            self.victory_celebration = VictoryCelebration()
                            
                            # Detener música de fondo SIEMPRE al ganar
                            self.sound_manager.stop_background_music()
                            
                            # Reproducir sonido final si existe (prioridad sobre 'win')
                            # Reproducir en loop infinito (-1) hasta que el usuario presione 'r'
                            if 'final' in self.sound_manager.sounds and self.sound_manager.sounds['final']:
                                # Reproducir con volumen máximo en loop infinito
                                self.sound_manager.play_sound('final', 1.0, 1.0, loops=-1)
                            else:
                                self.sound_manager.play_sound('win', 1.0, self.sound_volume)
        
        # Actualizar objetos espaciales
        for obj in self.space_objects:
            obj.update()
        
        # Actualizar explosiones
        for explosion in self.explosions[:]:
            explosion.update()
            if explosion.is_dead():
                self.explosions.remove(explosion)
        
        # Actualizar efectos de combo
        for effect in self.combo_effects[:]:
            effect.update()
            if effect.is_dead():
                self.combo_effects.remove(effect)
        
        # Actualizar screen shake
        if self.screen_shake > 0:
            self.screen_shake -= 1
        
        # Actualizar screen flash
        if self.screen_flash > 0:
            self.screen_flash -= 1
        
        # Actualizar indicador de combo
        self.combo_indicator.update(self.combo_streak)
        
        # Actualizar proyectiles del jugador
        for projectile in self.player_projectiles[:]:
            # Si el proyectil tenía un objetivo que ya murió, redirigirlo a otro enemigo
            if projectile.is_player_shot and projectile.target_enemy:
                if projectile.target_enemy.is_dead() or projectile.target_enemy not in self.enemies:
                    # Buscar otro enemigo vivo como objetivo
                    if self.enemies:
                        projectile.target_enemy = random.choice(self.enemies)
                    else:
                        # No hay enemigos, eliminar proyectil
                        self.player_projectiles.remove(projectile)
                        continue
            
            projectile.update()
            
            # Colisión con enemigos
            hit_enemy = None
            for enemy in self.enemies:
                if projectile.get_rect().colliderect(
                    pygame.Rect(enemy.x, enemy.y, enemy.width, enemy.height)
                ):
                    enemy.take_damage()
                    hit_enemy = enemy
                    if projectile in self.player_projectiles:
                        self.player_projectiles.remove(projectile)
                    self.sound_manager.play_sound('hit', 0.8, self.sound_volume)  # Volumen alto para sonido explosivo
                    break
            
            # Verificar si algún enemigo fue derrotado
            if hit_enemy and hit_enemy.is_dead():
                # Crear explosión
                explosion = Explosion(
                    hit_enemy.x + hit_enemy.width // 2,
                    hit_enemy.y + hit_enemy.height // 2
                )
                self.explosions.append(explosion)
                self.sound_manager.play_sound('explosion', 0.4, self.sound_volume)
                
                # Remover enemigo
                if hit_enemy in self.enemies:
                    self.enemies.remove(hit_enemy)
                
                # Si todos los enemigos fueron derrotados
                if len(self.enemies) == 0:
                    # Limpiar proyectiles restantes
                    self.player_projectiles.clear()
                    
                    if self.modo_infinito and self.infinite_mode:
                        # Modo infinito: regenerar con dificultad escalable
                        wave_config = self.infinite_mode.next_wave()
                        self.level = wave_config["visual_level"]
                        self.level_intro_timer = 90
                        self.game_state = "level_intro"
                        # Limpiar combo streak y efectos para evitar que ataquen en vacio
                        self.combo_streak = 0
                        self.combo_effects = []
                        self.generate_enemies_infinite(wave_config)
                        self.generate_problem()
                        self.generate_space_objects()
                        self.sound_manager.change_level_music(self.level, self.music_volume)
                    else:
                        # Modo normal: avanzar de nivel o ganar
                        if self.level < 3:
                            self.level += 1
                            self.game_state = "level_intro"
                            self.level_intro_timer = 180
                            # Limpiar combo streak y efectos para evitar que ataquen en vacio
                            self.combo_streak = 0
                            self.combo_effects = []
                            self.generate_enemies()
                            self.generate_problem()
                            self.generate_space_objects()
                            # La música continúa, no se reinicia al pasar de nivel
                        else:
                            # Fin del juego - ir a pre_victory para mostrar animación
                            self.game_state = "pre_victory"
                            self.victory_celebration = VictoryCelebration()
                            
                            print("DEBUG: Entrando a lógica de victoria. Estado de sonidos:")
                            print(f"DEBUG: Keys disponibles: {list(self.sound_manager.sounds.keys())}")
                            print(f"DEBUG: 'final' cargado: {'final' in self.sound_manager.sounds and self.sound_manager.sounds['final'] is not None}")
                            
                            # Detener música de fondo SIEMPRE al ganar
                            self.sound_manager.stop_background_music()
                            print("DEBUG: Música de fondo detenida")
                            
                            # Reproducir sonido final si existe (prioridad sobre 'win')
                            # Reproducir en loop infinito (-1) hasta que el usuario presione 'r'
                            if 'final' in self.sound_manager.sounds and self.sound_manager.sounds['final']:
                                # Reproducir con volumen máximo en loop infinito
                                self.sound_manager.play_sound('final', 1.0, 1.0, loops=-1)
                                print("DEBUG: ¡VICTORIA! Reproduciendo sonido final.wav en loop")
                            else:
                                print(f"DEBUG: No se encontró 'final', reproduciendo 'win'")
                                self.sound_manager.play_sound('win', 1.0, self.sound_volume)
            
            # Eliminar proyectiles fuera de pantalla solo si no tienen objetivo válido
            if projectile in self.player_projectiles:
                if projectile.is_off_screen():
                    # Si está fuera de pantalla pero tiene objetivo, mantenerlo (puede volver)
                    if not (projectile.is_player_shot and projectile.target_enemy and 
                           projectile.target_enemy in self.enemies):
                        self.player_projectiles.remove(projectile)
        
        # Actualizar proyectiles del enemigo
        for projectile in self.enemy_projectiles[:]:
            # Si el proyectil tiene objetivo (jugador), actualizar dirección
            if not projectile.is_player_shot and projectile.target_player:
                # El proyectil ya se actualiza automáticamente hacia el jugador en update()
                pass
            
            projectile.update()
            
            # Colisión con el jugador
            if projectile.get_rect().colliderect(
                pygame.Rect(self.player.x, self.player.y, self.player.width, self.player.height)
            ):
                self.player.take_damage()
                if projectile in self.enemy_projectiles:
                    self.enemy_projectiles.remove(projectile)
                self.sound_manager.play_sound('hit', 0.8, self.sound_volume)  # Volumen alto para sonido explosivo
                # Reproducir sonido de daño cuando recibe impacto
                self.sound_manager.play_sound('damage', 0.5, self.sound_volume)
                if self.player.lives <= 0:
                    self.game_state = "lose"
                    # Detener música cuando se pierde el juego
                    self.sound_manager.stop_background_music()
            
            # Eliminar proyectiles fuera de pantalla solo si no tienen objetivo
            elif projectile.is_off_screen():
                if not (not projectile.is_player_shot and projectile.target_player):
                    if projectile in self.enemy_projectiles:
                        self.enemy_projectiles.remove(projectile)
        
        # Actualizar feedback
        if self.feedback_timer > 0:
            self.feedback_timer -= 1
        
        # Actualizar temporizador de la pregunta
        if (self.game_state == "playing" and 
            self.answer_cooldown == 0 and 
            self.question_timer > 0):
            self.question_timer -= 1
            
            if self.question_timer == 0:
                self.handle_timeout()
        
        # Actualizar cooldown de respuesta
        if self.answer_cooldown > 0:
            self.answer_cooldown -= 1
            if self.answer_cooldown == 0:
                self.generate_problem()
    
    def draw_ui(self):
        """Dibuja la interfaz de usuario mejorada"""
        
        # Temporizador de la pregunta (en esquina superior izquierda)
        time_remaining = self.question_timer / FPS  # Tiempo en segundos
        time_percentage = self.question_timer / self.question_timer_max
        
        # Barra de tiempo (en esquina superior izquierda)
        timer_bar_width = 200
        timer_bar_height = 25
        timer_bar_x = 20
        timer_bar_y = 10
        
        # Fondo semitransparente para el temporizador
        timer_bg = pygame.Surface((timer_bar_width + 10, timer_bar_height + 30), pygame.SRCALPHA)
        timer_bg.fill((0, 0, 0, 180))
        self.screen.blit(timer_bg, (timer_bar_x - 5, timer_bar_y - 5))
        
        # Etiqueta "TIEMPO"
        time_label = self.font_tiny.render("TIEMPO", True, CYAN)
        self.screen.blit(time_label, (timer_bar_x, timer_bar_y - 3))
        
        # Fondo de la barra de tiempo
        pygame.draw.rect(self.screen, (50, 50, 50), 
                        (timer_bar_x, timer_bar_y + 15, timer_bar_width, timer_bar_height))
        
        # Barra de progreso del tiempo (disminuye)
        if time_percentage > 0:
            progress_width = int(timer_bar_width * time_percentage)
            
            # Color dinámico con gradientes y pulsación
            if time_percentage > 0.5:
                # Verde estable
                timer_color = GREEN
                glow_alpha = 0
            elif time_percentage > 0.25:
                # Amarillo con pulso suave
                pulse = abs(math.sin(pygame.time.get_ticks() * 0.005)) * 0.3 + 0.7
                timer_color = (int(255 * pulse), int(220 * pulse), 0)
                glow_alpha = 30
            else:
                # Rojo con pulso intenso y urgente
                pulse = abs(math.sin(pygame.time.get_ticks() * 0.015)) * 0.5 + 0.5
                timer_color = (int(255 * pulse), int(50 * pulse), int(50 * pulse))
                glow_alpha = int(80 * pulse)
                
                # Efecto de glow pulsante cuando queda poco tiempo
                glow_surface = pygame.Surface((timer_bar_width + 20, timer_bar_height + 20), pygame.SRCALPHA)
                pygame.draw.rect(glow_surface, (255, 0, 0, glow_alpha), 
                               (0, 0, timer_bar_width + 20, timer_bar_height + 20), border_radius=5)
                self.screen.blit(glow_surface, (timer_bar_x - 10, timer_bar_y + 5))
            
            # Barra principal
            pygame.draw.rect(self.screen, timer_color, 
                           (timer_bar_x, timer_bar_y + 15, progress_width, timer_bar_height))
            
            # Efecto de brillo en la barra
            if progress_width > 5:
                pygame.draw.rect(self.screen, (255, 255, 255), 
                               (timer_bar_x, timer_bar_y + 15, progress_width, 10), 1)
        
        # Borde de la barra
        pygame.draw.rect(self.screen, WHITE, 
                        (timer_bar_x, timer_bar_y + 15, timer_bar_width, timer_bar_height), 2)
        
        # Texto del tiempo restante
        if self.answer_cooldown == 0:  # Solo mostrar si no hay cooldown activo
            time_text = self.font_small.render(f"{time_remaining:.1f}s", True, WHITE)
            time_text_shadow = self.font_small.render(f"{time_remaining:.1f}s", True, BLACK)
            time_text_rect = time_text.get_rect(center=(timer_bar_x + timer_bar_width // 2, timer_bar_y + 27))
            self.screen.blit(time_text_shadow, (time_text_rect.x + 1, time_text_rect.y + 1))
            self.screen.blit(time_text, time_text_rect)
        
        # Indicador de MODO INFINITO (si está activo)
        if self.modo_infinito:
            infinite_y = timer_bar_y + timer_bar_height + 25
            
            # Fondo para el indicador
            mode_bg = pygame.Surface((timer_bar_width + 10, 24), pygame.SRCALPHA)
            mode_bg.fill((100, 0, 150, 180))  # Púrpura semitransparente
            self.screen.blit(mode_bg, (timer_bar_x - 5, infinite_y))
            
            # Texto del modo
            mode_text = self.font_tiny.render("⚡ MODO INFINITO", True, PINK)
            self.screen.blit(mode_text, (timer_bar_x, infinite_y + 4))
            
            # Mostrar tiempo adaptativo si el sistema está activo
            if self.tiempo_adaptativo and self.tiempo_adaptativo.usar_modelo:
                ml_text = self.font_tiny.render("ML", True, GREEN)
            else:
                ml_text = self.font_tiny.render("--", True, YELLOW)
            ml_rect = ml_text.get_rect(right=timer_bar_x + timer_bar_width, centery=infinite_y + 12)
            self.screen.blit(ml_text, ml_rect)

        
        # Panel del problema matemático (ubicado más abajo para no tapar al enemigo)
        problem_y_offset = 250  # Posición ajustada para estar más arriba
        problem_bg = pygame.Surface((SCREEN_WIDTH - 40, 100), pygame.SRCALPHA)
        problem_bg.fill((0, 0, 0, 200))
        self.screen.blit(problem_bg, (20, problem_y_offset))
        
        # Obtener texto del problema y separar el signo "?"
        problem_str = self.math_problem.get_text()
        
        # Encontrar la posición del "?" para destacarlo
        if "?" in problem_str:
            parts = problem_str.split("?")
            pre_question = parts[0]
            
            # Renderizar parte antes del "?"
            pre_text = self.font_large.render(pre_question, True, YELLOW)
            pre_shadow = self.font_large.render(pre_question, True, BLACK)
            
            # Calcular posición centrada
            total_width = pre_text.get_width()
            
            # Signo "?" animado con glow
            pulse = abs(math.sin(pygame.time.get_ticks() * 0.008)) * 0.5 + 0.5
            question_scale = 1.0 + pulse * 0.2  # Escala pulsante
            
            # Colores dinámicos para el "?"
            q_r = int(255 * pulse + 100 * (1 - pulse))
            q_g = int(100 * pulse + 255 * (1 - pulse))
            q_b = int(255)
            question_color = (q_r, q_g, q_b)
            
            question_text = self.font_large.render("?", True, question_color)
            question_shadow = self.font_large.render("?", True, (0, 0, 0))
            
            # Escalar el "?"
            q_width = int(question_text.get_width() * question_scale)
            q_height = int(question_text.get_height() * question_scale)
            if q_width > 0 and q_height > 0:
                question_text = pygame.transform.scale(question_text, (q_width, q_height))
                question_shadow = pygame.transform.scale(question_shadow, (q_width, q_height))
            
            total_width += q_width
            
            # Renderizar parte después del "?" (si existe)
            post_text = None
            if len(parts) > 1:
                post_question = parts[1]
                post_text = self.font_large.render(post_question, True, YELLOW)
                post_shadow = self.font_large.render(post_question, True, BLACK)
                total_width += post_text.get_width()
            
            # Dibujar glow detrás del "?"
            glow_size = int(30 + 10 * pulse)
            glow_surface = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
            glow_alpha = int(100 * pulse)
            pygame.draw.circle(glow_surface, (*question_color, glow_alpha), 
                             (glow_size, glow_size), glow_size)
            
            # Posicionar todo centrado
            start_x = SCREEN_WIDTH // 2 - total_width // 2
            y_pos = problem_y_offset + 25
            
            # Dibujar sombra y texto previo
            self.screen.blit(pre_shadow, (start_x + 2, y_pos + 2))
            self.screen.blit(pre_text, (start_x, y_pos))
            
            # Posición del "?"
            q_x = start_x + pre_text.get_width()
            q_y = y_pos - (q_height - pre_text.get_height()) // 2
            
            # Dibujar glow, sombra y "?" animado
            self.screen.blit(glow_surface, (q_x + q_width // 2 - glow_size, q_y + q_height // 2 - glow_size))
            self.screen.blit(question_shadow, (q_x + 3, q_y + 3))
            self.screen.blit(question_text, (q_x, q_y))
            
            # Dibujar texto posterior
            if post_text:
                post_x = q_x + q_width
                self.screen.blit(post_shadow, (post_x + 2, y_pos + 2))
                self.screen.blit(post_text, (post_x, y_pos))
        else:
            # Fallback si no hay "?"
            problem_text = self.font_large.render(problem_str, True, YELLOW)
            problem_shadow = self.font_large.render(problem_str, True, BLACK)
            problem_rect = problem_text.get_rect(center=(SCREEN_WIDTH // 2, problem_y_offset + 30))
            self.screen.blit(problem_shadow, (problem_rect.x + 2, problem_rect.y + 2))
            self.screen.blit(problem_text, problem_rect)
        
        # Instrucciones mejoradas
        # Instrucciones mejoradas
        if self.answer_cooldown > 0:
            # Mostrar mensaje de espera cuando hay cooldown
            wait_time = (self.answer_cooldown / FPS)  # Tiempo restante en segundos
            instructions = f"Espera {wait_time:.1f}s para responder..."
            inst_text = self.font_small.render(instructions, True, ORANGE)
            inst_rect = inst_text.get_rect(center=(SCREEN_WIDTH // 2, problem_y_offset + 65))
            self.screen.blit(inst_text, inst_rect)
        else:
            # Dibujar teclas visuales (W, A, S, D)
            # Dibujar teclas visuales (W, A, S, D) - REDISEÑADO
            # Configuración: Tecla, Operación, Color
            controls_config = [
                ('W', '+', RED), 
                ('A', '-', BLUE), 
                ('S', '*', YELLOW), 
                ('D', '/', GREEN)
            ]
            
            # Configuración de diseño
            button_size = 50
            spacing = 110
            total_width = len(controls_config) * spacing
            start_x = SCREEN_WIDTH // 2 - total_width // 2 + spacing // 2 - button_size // 2
            y_pos = problem_y_offset + 75
            
            for i, (key, op, color) in enumerate(controls_config):
                x_pos = start_x + i * spacing
                
                # Rectángulo del botón (Operación)
                btn_rect = pygame.Rect(x_pos, y_pos, button_size, button_size)
                
                # Sombra (offset)
                shadow_color = (max(0, color[0]-50), max(0, color[1]-50), max(0, color[2]-50))
                shadow_rect = pygame.Rect(x_pos, y_pos + 5, button_size, button_size)
                pygame.draw.rect(self.screen, shadow_color, shadow_rect, border_radius=12)
                
                # Botón principal
                pygame.draw.rect(self.screen, color, btn_rect, border_radius=12)
                
                # Borde blanco suave
                pygame.draw.rect(self.screen, WHITE, btn_rect, 2, border_radius=12)
                
                # Símbolo de operación - Texto Grande
                text_color = BLACK if color in [YELLOW, GREEN] else WHITE
                op_surf = self.font_large.render(op, True, text_color)
                op_rect = op_surf.get_rect(center=btn_rect.center)
                self.screen.blit(op_surf, op_rect)
                
                # Marcador AZUL con la tecla (al lado derecho)
                marker_color = BLUE
                marker_radius = 15
                marker_x = x_pos + button_size + 15
                marker_y = y_pos + button_size // 2
                
                # Círculo del marcador
                pygame.draw.circle(self.screen, marker_color, (marker_x, marker_y), marker_radius)
                pygame.draw.circle(self.screen, WHITE, (marker_x, marker_y), marker_radius, 2)
                
                # Letra de la tecla
                key_surf = self.font_small.render(key, True, WHITE)
                key_rect = key_surf.get_rect(center=(marker_x, marker_y))
                self.screen.blit(key_surf, key_rect)
        
        # Barra de progreso del cooldown (si está activo)
        if self.answer_cooldown > 0:
            cooldown_max = 90  # Debe coincidir con el valor en process_answer
            cooldown_percentage = 1.0 - (self.answer_cooldown / cooldown_max)
            bar_width = 200
            bar_height = 4
            bar_x = SCREEN_WIDTH // 2 - bar_width // 2
            bar_y = problem_y_offset + 85
            
            # Fondo de la barra
            pygame.draw.rect(self.screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
            # Barra de progreso
            progress_width = int(bar_width * cooldown_percentage)
            if progress_width > 0:
                color = (
                    int(255 * (1 - cooldown_percentage)),
                    int(255 * cooldown_percentage),
                    0
                )
                pygame.draw.rect(self.screen, color, (bar_x, bar_y, progress_width, bar_height))
            # Borde
            pygame.draw.rect(self.screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 1)
        
        # Panel de estadísticas mejorado
        stats_y = SCREEN_HEIGHT - 150
        stats_bg = pygame.Surface((200, 140), pygame.SRCALPHA)
        stats_bg.fill((0, 0, 0, 200))
        self.screen.blit(stats_bg, (5, stats_y - 5))
        
        if self.modo_infinito:
            stats = [
                ("Oleada", str(self.infinite_mode.wave if self.infinite_mode else 0), PURPLE),
                ("Vidas", f"{self.player.lives}/5", GREEN),
                ("Enemigos", f"{len(self.enemies)}", RED),
                ("Puntaje", str(self.player.score), CYAN),
                ("Correctas", str(self.player.correct_answers), GREEN),
                ("Incorrectas", str(self.player.incorrect_answers), RED)
            ]
        else:
            stats = [
                ("Nivel", f"{self.level}/3", YELLOW),
                ("Vidas", f"{self.player.lives}/5", GREEN),
                ("Enemigos", f"{len(self.enemies)}", RED),
                ("Puntaje", str(self.player.score), CYAN),
                ("Correctas", str(self.player.correct_answers), GREEN),
                ("Incorrectas", str(self.player.incorrect_answers), RED)
            ]
        
        for i, (label, value, color) in enumerate(stats):
            label_text = self.font_tiny.render(f"{label}:", True, WHITE)
            value_text = self.font_small.render(value, True, color)
            self.screen.blit(label_text, (15, stats_y + i * 22))
            self.screen.blit(value_text, (120, stats_y + i * 22))
        
        # Vidas del jugador (corazones mejorados) - Estilo igual al COMBO
        heart_size = 24
        lives_panel_w = 180
        lives_panel_h = 40
        lives_panel = pygame.Surface((lives_panel_w, lives_panel_h), pygame.SRCALPHA)
        
        # Fondo con estilo igual al combo
        pygame.draw.rect(lives_panel, (20, 40, 60, 180), (0, 0, lives_panel_w, lives_panel_h), border_radius=8)
        pygame.draw.rect(lives_panel, CYAN, (0, 0, lives_panel_w, lives_panel_h), 2, border_radius=8)
        
        self.screen.blit(lives_panel, (SCREEN_WIDTH - 185, 5))
        
        # Etiqueta "VIDAS" al lado de los corazones
        lives_label = self.font_tiny.render("VIDAS", True, WHITE)
        self.screen.blit(lives_label, (SCREEN_WIDTH - 180, 12))
        
        for i in range(5):
            x = SCREEN_WIDTH - 125 + i * 26
            y = 25
            if i < self.player.lives:
                # Corazón lleno con gradiente
                # Sombra
                pygame.draw.circle(self.screen, DARK_RED, (x, y), heart_size // 2 + 1)
                pygame.draw.polygon(self.screen, DARK_RED, [
                    (x, y + heart_size // 4 + 1),
                    (x - heart_size // 2 - 1, y + 1),
                    (x, y - heart_size // 4 + 1),
                    (x + heart_size // 2 + 1, y + 1)
                ])
                # Corazón principal
                pygame.draw.circle(self.screen, RED, (x, y), heart_size // 2)
                pygame.draw.polygon(self.screen, RED, [
                    (x, y + heart_size // 4),
                    (x - heart_size // 2, y),
                    (x, y - heart_size // 4),
                    (x + heart_size // 2, y)
                ])
                # Brillo
                pygame.draw.circle(self.screen, PINK, (x - 2, y - 2), 4)
            else:
                # Corazón vacío (solo borde)
                pygame.draw.circle(self.screen, (100, 100, 100), (x, y), heart_size // 2, 2)
                pygame.draw.polygon(self.screen, (100, 100, 100), [
                    (x, y + heart_size // 4),
                    (x - heart_size // 2, y),
                    (x, y - heart_size // 4),
                    (x + heart_size // 2, y)
                ], 2)
        
        # Feedback de respuesta mejorado
        if self.feedback_timer > 0:
            # Efecto de pulso
            scale = 1.0 + (abs(15 - self.feedback_timer) / 15.0) * 0.3
            
            # Sombra del texto
            feedback_shadow = self.font_medium.render(
                self.feedback_text, True, BLACK
            )
            shadow_rect = feedback_shadow.get_rect(
                center=(SCREEN_WIDTH // 2 + 3, SCREEN_HEIGHT // 2 + 3)
            )
            self.screen.blit(feedback_shadow, shadow_rect)
            
            # Texto principal
            feedback_surface = self.font_medium.render(
                self.feedback_text, True, self.feedback_color
            )
            feedback_rect = feedback_surface.get_rect(
                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
            )
            self.screen.blit(feedback_surface, feedback_rect)
            
            # Efecto de glow
            if self.feedback_color == GREEN:
                glow_color = (0, 255, 0, 30)
            else:
                glow_color = (255, 0, 0, 30)
            
            glow_size = int(200 * scale)
            glow_surface = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, glow_color, (glow_size // 2, glow_size // 2), glow_size // 2)
            self.screen.blit(glow_surface, (SCREEN_WIDTH // 2 - glow_size // 2, SCREEN_HEIGHT // 2 - glow_size // 2))
    
    def draw_game_over(self):
        """Dibuja la pantalla de fin de juego mejorada"""
        # Overlay semitransparente
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(220)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Panel central
        panel_width = 500
        panel_height = 300
        panel_x = (SCREEN_WIDTH - panel_width) // 2
        panel_y = (SCREEN_HEIGHT - panel_height) // 2
        
        panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel.fill((20, 20, 40, 240))
        pygame.draw.rect(panel, WHITE, (0, 0, panel_width, panel_height), 3)
        self.screen.blit(panel, (panel_x, panel_y))
        
        if self.game_state == "win":
            # Efecto de victoria
            text = self.font_large.render("¡GANASTE!", True, GREEN)
            text_shadow = self.font_large.render("¡GANASTE!", True, BLACK)
            subtitle = self.font_medium.render("¡Felicitaciones!", True, YELLOW)
            score_text = self.font_medium.render(
                f"Puntaje Final: {self.player.score}", True, GOLD
            )
        else:
            # Efecto de derrota
            text = self.font_large.render("PERDISTE", True, RED)
            text_shadow = self.font_large.render("PERDISTE", True, BLACK)
            subtitle = self.font_medium.render("Mejor suerte la próxima", True, ORANGE)
            score_text = self.font_medium.render(
                f"Puntaje Final: {self.player.score}", True, YELLOW
            )
        
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80))
        self.screen.blit(text_shadow, (text_rect.x + 3, text_rect.y + 3))
        self.screen.blit(text, text_rect)
        
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
        self.screen.blit(subtitle, subtitle_rect)
        
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
        self.screen.blit(score_text, score_rect)
        
        # Estadísticas finales
        stats_final = [
            f"Respuestas Correctas: {self.player.correct_answers}",
            f"Respuestas Incorrectas: {self.player.incorrect_answers}"
        ]
        for i, stat in enumerate(stats_final):
            stat_text = self.font_small.render(stat, True, CYAN)
            stat_rect = stat_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60 + i * 25))
            self.screen.blit(stat_text, stat_rect)
        
        restart_text = self.font_medium.render(
            "Presiona R para reiniciar", True, WHITE
        )
        restart_shadow = self.font_medium.render(
            "Presiona R para reiniciar", True, BLACK
        )
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 130))
        self.screen.blit(restart_shadow, (restart_rect.x + 2, restart_rect.y + 2))
        self.screen.blit(restart_text, restart_rect)
        
        # Opción de volver al menú
        menu_text = self.font_medium.render(
            "Presiona ESC para Menú", True, WHITE
        )
        menu_shadow = self.font_medium.render(
            "Presiona ESC para Menú", True, BLACK
        )
        menu_rect = menu_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 170))
        self.screen.blit(menu_shadow, (menu_rect.x + 2, menu_rect.y + 2))
        self.screen.blit(menu_text, menu_rect)

    def draw_victory_screen(self):
        """Dibuja una pantalla de victoria dedicada y festiva"""
        # Fondo con efecto de celebración
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((10, 30, 60)) # Azul oscuro festivo
        self.screen.blit(overlay, (0, 0))
        
        # Título grande
        title = self.font_large.render("¡MISIÓN CUMPLIDA!", True, GOLD)
        title_shadow = self.font_large.render("¡MISIÓN CUMPLIDA!", True, BLACK)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 120))
        
        # Efecto de pulso en el título
        pulse = (math.sin(pygame.time.get_ticks() * 0.005) + 1) * 0.1 + 1.0
        scaled_w = int(title_rect.width * pulse)
        scaled_h = int(title_rect.height * pulse)
        
        # Subtítulo
        subtitle = self.font_medium.render("¡Has completado todos los niveles!", True, GREEN)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60))
        
        # Dibujar textos
        self.screen.blit(title_shadow, (title_rect.x + 4, title_rect.y + 4))
        self.screen.blit(title, title_rect)
        self.screen.blit(subtitle, subtitle_rect)
        
        # Puntaje final grande
        score_panel = pygame.Surface((400, 100), pygame.SRCALPHA)
        pygame.draw.rect(score_panel, (0, 0, 0, 100), (0, 0, 400, 100), border_radius=20)
        pygame.draw.rect(score_panel, GOLD, (0, 0, 400, 100), 3, border_radius=20)
        
        score_text = self.font_large.render(f"{self.player.score}", True, WHITE)
        score_label = self.font_medium.render("PUNTAJE FINAL", True, YELLOW)
        
        score_rect = score_text.get_rect(center=(200, 60))
        label_rect = score_label.get_rect(center=(200, 25))
        
        score_panel.blit(score_text, score_rect)
        score_panel.blit(score_label, label_rect)
        
        self.screen.blit(score_panel, (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2))
        
        # Instrucciones
        back_text = self.font_medium.render("Presiona R para reiniciar o ENTER/ESC para volver al Menú", True, CYAN)
        back_rect = back_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 150))
        
        # Parpadeo suave
        alpha = int(abs(math.sin(pygame.time.get_ticks() * 0.003)) * 255)
        back_text.set_alpha(alpha)
        
        self.screen.blit(back_text, back_rect)
    
    def _cache_all_backgrounds(self):
        """Prerenderiza los fondos de todos los niveles para mejor rendimiento"""
        level_configs = {
            1: (L1_BG_START, L1_BG_END, L1_STAR),
            2: (L2_BG_START, L2_BG_END, L2_STAR),
            3: (L3_BG_START, L3_BG_END, L3_STAR),
        }
        
        for level, (bg_start, bg_end, star_color) in level_configs.items():
            # Crear surface para este nivel
            bg_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            
            # Dibujar gradiente vertical (solo una vez)
            for y in range(SCREEN_HEIGHT):
                progress = y / SCREEN_HEIGHT
                r = int(bg_start[0] + (bg_end[0] - bg_start[0]) * progress)
                g = int(bg_start[1] + (bg_end[1] - bg_start[1]) * progress)
                b = int(bg_start[2] + (bg_end[2] - bg_start[2]) * progress)
                pygame.draw.line(bg_surface, (r, g, b), (0, y), (SCREEN_WIDTH, y))
            
            # Dibujar estrellas con colores del nivel
            for x, y, size, brightness in self.stars:
                color = (
                    min(255, int(star_color[0] * brightness / 255)),
                    min(255, int(star_color[1] * brightness / 255)),
                    min(255, int(star_color[2] * brightness / 255))
                )
                pygame.draw.circle(bg_surface, color, (x, y), size)
                if size >= 2:
                    pygame.draw.circle(bg_surface, WHITE, (x, y), 1)
            
            self.cached_backgrounds[level] = bg_surface
        
        print("✓ Fondos cacheados para optimización de rendimiento")
    
    def draw_background(self):
        """Dibuja el fondo usando cache prerenderizado (OPTIMIZADO)"""
        # Determinar qué nivel usar para el fondo
        level_for_bg = self.level
        if self.game_state == "menu":
            level_for_bg = 1
        
        # Usar fondo cacheado (mucho más rápido)
        if level_for_bg in self.cached_backgrounds:
            self.screen.blit(self.cached_backgrounds[level_for_bg], (0, 0))
        
        # Dibujar objetos espaciales (estos sí se mueven)
        for obj in self.space_objects:
            obj.draw(self.screen)

    def draw_menu(self):
        """Dibuja la pantalla de menú principal con diseño moderno y animación dinámica"""
        # Fondo oscuro espacial (ya dibujado en draw_background, pero reforzamos con overlay)
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(50)
        overlay.fill((0, 0, 20)) 
        self.screen.blit(overlay, (0, 0))
        
        # ... (código del menú continua después) ...

# ...

    def draw(self):
        """Dibuja todos los elementos del juego"""
        # Dibujar fondo
        self.draw_background()
        
        if self.game_state == "menu":
            self.draw_menu()
        elif self.game_state == "controls":
            self.draw_controls()
        elif self.game_state == "settings":
            self.draw_settings()
        elif self.game_state == "level_intro":
            self.draw_level_intro()
        elif self.game_state == "playing":
            # Aplicar screen shake
            shake_offset_x = 0
            shake_offset_y = 0
            if self.screen_shake > 0:
                shake_offset_x = random.randint(-int(self.screen_shake_intensity), int(self.screen_shake_intensity))
                shake_offset_y = random.randint(-int(self.screen_shake_intensity), int(self.screen_shake_intensity))
            
            # Crear superficie temporal para aplicar shake
            if shake_offset_x != 0 or shake_offset_y != 0:
                game_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                game_surface.blit(self.screen, (0, 0))
            
            # Dibujar elementos del juego
            self.player.draw(self.screen)
            
            # Dibujar enemigos
            for enemy in self.enemies:
                enemy.draw(self.screen)
            
            # Dibujar explosiones
            for explosion in self.explosions:
                explosion.draw(self.screen)
            
            # Dibujar proyectiles
            for projectile in self.player_projectiles:
                projectile.draw(self.screen)
            
            for projectile in self.enemy_projectiles:
                projectile.draw(self.screen)
            
            # Dibujar efectos de combo (encima de todo excepto UI)
            for effect in self.combo_effects:
                if hasattr(effect, 'draw'):
                    if isinstance(effect, ComboTextPopup):
                        effect.draw(self.screen, self.font_large)
                    else:
                        effect.draw(self.screen)
            
            # Screen flash (overlay blanco)
            if self.screen_flash > 0:
                flash_alpha = int(150 * (self.screen_flash / 15))
                flash_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                flash_surface.fill((255, 255, 200, flash_alpha))
                self.screen.blit(flash_surface, (0, 0))
            
            self.draw_ui()
            
            # Dibujar indicador de combo (encima de la UI)
            if self.combo_streak > 0:
                self.combo_indicator.draw(self.screen, self.font_tiny)
            
            # Dibujar mascota (encima de la UI)
            self.mascota.draw(self.screen)
        elif self.game_state == "paused":
            # Dibujar elementos del juego (fondo)
            self.player.draw(self.screen)
            for enemy in self.enemies:
                enemy.draw(self.screen)
            for explosion in self.explosions:
                explosion.draw(self.screen)
            for projectile in self.player_projectiles:
                projectile.draw(self.screen)
            for projectile in self.enemy_projectiles:
                projectile.draw(self.screen)
            
            # Dibujar menú de pausa
            self.draw_pause_menu()
        elif self.game_state == "victory":
            self.draw_victory_screen()
        else:
            # Dibujar pantalla de fin de juego
            self.player.draw(self.screen)
            for enemy in self.enemies:
                enemy.draw(self.screen)
            for explosion in self.explosions:
                explosion.draw(self.screen)
            self.draw_game_over()
        
        pygame.display.flip()
        """Dibuja el fondo según el nivel actual"""
        # Obtener dimensiones reales de la pantalla
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()
        
        if self.game_state == "menu":
            level_for_bg = 1
        elif self.game_state == "level_intro":
            level_for_bg = self.level
        elif self.game_state != "playing":
            level_for_bg = self.level
        else:
            level_for_bg = self.level
        
        # Fondo con gradiente espacial según el nivel
        for y in range(screen_height):
            progress = y / screen_height
            
            if level_for_bg == 1:
                r = int(L1_BG_START[0] + (L1_BG_END[0] - L1_BG_START[0]) * progress)
                g = int(L1_BG_START[1] + (L1_BG_END[1] - L1_BG_START[1]) * progress)
                b = int(L1_BG_START[2] + (L1_BG_END[2] - L1_BG_START[2]) * progress)
                star_color_mult = L1_STAR
            elif level_for_bg == 2:
                r = int(L2_BG_START[0] + (L2_BG_END[0] - L2_BG_START[0]) * progress)
                g = int(L2_BG_START[1] + (L2_BG_END[1] - L2_BG_START[1]) * progress)
                b = int(L2_BG_START[2] + (L2_BG_END[2] - L2_BG_START[2]) * progress)
                star_color_mult = L2_STAR
            else:
                r = int(L3_BG_START[0] + (L3_BG_END[0] - L3_BG_START[0]) * progress)
                g = int(L3_BG_START[1] + (L3_BG_END[1] - L3_BG_START[1]) * progress)
                b = int(L3_BG_START[2] + (L3_BG_END[2] - L3_BG_START[2]) * progress)
                star_color_mult = L3_STAR
            
            color = (r, g, b)
            pygame.draw.line(self.screen, color, (0, y), (screen_width, y))
        
        # Dibujar fondo estrellado
        for x, y, size, brightness in self.stars:
            base_color = star_color_mult
            color = (
                min(255, int(base_color[0] * brightness / 255)),
                min(255, int(base_color[1] * brightness / 255)),
                min(255, int(base_color[2] * brightness / 255))
            )
            pygame.draw.circle(self.screen, color, (x, y), size)
            if size >= 2:
                pygame.draw.circle(self.screen, WHITE, (x, y), 1)
        
        # Dibujar objetos espaciales (solo en playing)
        if self.game_state == "playing":
            for obj in self.space_objects:
                obj.draw(self.screen)
    
    def draw_menu(self):
        """Dibuja la pantalla de menú principal con diseño moderno y animación dinámica"""
        # Crear buffer para screen shake
        menu_buffer = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        menu_buffer.blit(self.screen, (0, 0))  # Copiar fondo actual
        
        # === CAPA 1: POLVO CÓSMICO (más lejano, parallax lento) ===
        for particle in self.menu_particles:
            if particle.type == 'dust':
                particle.draw(menu_buffer)
        
        # === CAPA 2: OBJETOS ESPACIALES (asteroides, planetas) ===
        for obj in self.space_objects:
            obj.draw(menu_buffer)
        
        # === CAPA 3: SÍMBOLOS MATEMÁTICOS FLOTANTES ===
        for symbol in self.floating_math_symbols:
            symbol.draw(menu_buffer, self.font_medium)
        
        # === CAPA 4: PROYECTILES DE LA BATALLA ===
        for projectile in self.menu_projectiles:
            projectile.draw(menu_buffer)
        
        # === CAPA 5: NAVES (Jugador y Enemigos) ===
        self.player.draw(menu_buffer)
        for enemy in self.enemies:
            enemy.draw(menu_buffer)
        
        # === CAPA 6: EXPLOSIONES (MUY PROMINENTES) ===
        for explosion in self.menu_explosions:
            explosion.draw(menu_buffer)
        
        # === CAPA 7: ESTRELLAS FUGACES Y CHISPAS (más cercanas, brillantes) ===
        for particle in self.menu_particles:
            if particle.type in ['star', 'spark']:
                particle.draw(menu_buffer)
        
        # === APLICAR SCREEN SHAKE ===
        shake_x = 0
        shake_y = 0
        if self.menu_screen_shake > 0:
            shake_x = random.randint(-int(self.menu_shake_intensity), int(self.menu_shake_intensity))
            shake_y = random.randint(-int(self.menu_shake_intensity), int(self.menu_shake_intensity))
        
        # Blitear el buffer con el shake offset
        self.screen.blit(menu_buffer, (shake_x, shake_y))
        
        # (Panel oscuro eliminado - los botones ya tienen su propio estilo glassmorphism)
        
        # Título principal con efecto moderno
        title_text = "OPERACIÓN RELÁMPAGO"
        
        # Sombra suave del título
        title_shadow = self.font_large.render(title_text, True, (0, 0, 0, 100))
        title_rect = title_shadow.get_rect(center=(SCREEN_WIDTH // 2 + 3, 103))
        self.screen.blit(title_shadow, title_rect)
        
        # Título principal con gradiente (simulado)
        title_surface = self.font_large.render(title_text, True, YELLOW)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(title_surface, title_rect)
        
        # Efecto de brillo en el título
        glow_surface = pygame.Surface((title_rect.width + 20, title_rect.height + 20), pygame.SRCALPHA)
        for i in range(10):
            alpha = int(30 * (1 - i / 10))
            pygame.draw.rect(glow_surface, (*YELLOW, alpha), 
                           (i, i, title_rect.width + 20 - i*2, title_rect.height + 20 - i*2), 1)
        self.screen.blit(glow_surface, (title_rect.x - 10, title_rect.y - 10))
        
        # Subtítulo elegante
        subtitle = self.font_medium.render("Juego Educativo de Matemáticas", True, CYAN)
        subtitle_shadow = self.font_medium.render("Juego Educativo de Matemáticas", True, (0, 0, 0, 150))
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 170))
        self.screen.blit(subtitle_shadow, (subtitle_rect.x + 1, subtitle_rect.y + 1))
        self.screen.blit(subtitle, subtitle_rect)
        
        # Dibujar botones rectangulares principales
        for button in self.menu_buttons:
            button.draw(self.screen)
        
        # Dibujar botones circulares (esquina inferior derecha)
        for btn in self.circular_buttons:
            btn.draw(self.screen)
        
        # Decoración elegante
        if self.menu_blink < 30:
            star_text = self.font_small.render("✦", True, GOLD)
            for i in range(3):
                x = SCREEN_WIDTH // 2 - 150 + i * 150
                y = 250
                self.screen.blit(star_text, (x, y))

        # Imágenes decorativas en los bordes
        img_size = 90  # Tamaño de la imagen
        frame_padding = 8  # Padding del marco
        title_y = 110  # Y del título
        
        if self.menu_left_img:
            # Posición: borde izquierdo de la pantalla
            img_x = 25
            img_y = title_y - img_size // 2
            
            # Marco con glassmorphism
            frame_w = img_size + frame_padding * 2
            frame_h = img_size + frame_padding * 2
            
            # Glow externo
            glow = pygame.Surface((frame_w + 16, frame_h + 16), pygame.SRCALPHA)
            for i in range(4):
                alpha = int(25 - i * 6)
                pygame.draw.rect(glow, (0, 180, 220, alpha),
                               (i*2, i*2, frame_w + 16 - i*4, frame_h + 16 - i*4),
                               border_radius=12 + i)
            self.screen.blit(glow, (img_x - frame_padding - 8, img_y - frame_padding - 8))
            
            # Panel glassmorphism
            frame = pygame.Surface((frame_w, frame_h), pygame.SRCALPHA)
            pygame.draw.rect(frame, (15, 30, 50, 180), (0, 0, frame_w, frame_h), border_radius=10)
            pygame.draw.rect(frame, (0, 180, 220), (0, 0, frame_w, frame_h), width=2, border_radius=10)
            self.screen.blit(frame, (img_x - frame_padding, img_y - frame_padding))
            
            # Imagen escalada
            scaled_img = pygame.transform.scale(self.menu_left_img, (img_size, img_size))
            self.screen.blit(scaled_img, (img_x, img_y))
            
        if self.menu_right_img:
            # Posición: borde derecho de la pantalla
            img_x = SCREEN_WIDTH - img_size - 25
            img_y = title_y - img_size // 2
            
            # Marco con glassmorphism
            frame_w = img_size + frame_padding * 2
            frame_h = img_size + frame_padding * 2
            
            # Glow externo
            glow = pygame.Surface((frame_w + 16, frame_h + 16), pygame.SRCALPHA)
            for i in range(4):
                alpha = int(25 - i * 6)
                pygame.draw.rect(glow, (0, 180, 220, alpha),
                               (i*2, i*2, frame_w + 16 - i*4, frame_h + 16 - i*4),
                               border_radius=12 + i)
            self.screen.blit(glow, (img_x - frame_padding - 8, img_y - frame_padding - 8))
            
            # Panel glassmorphism
            frame = pygame.Surface((frame_w, frame_h), pygame.SRCALPHA)
            pygame.draw.rect(frame, (15, 30, 50, 180), (0, 0, frame_w, frame_h), border_radius=10)
            pygame.draw.rect(frame, (0, 180, 220), (0, 0, frame_w, frame_h), width=2, border_radius=10)
            self.screen.blit(frame, (img_x - frame_padding, img_y - frame_padding))
            
            # Imagen escalada
            scaled_img = pygame.transform.scale(self.menu_right_img, (img_size, img_size))
            self.screen.blit(scaled_img, (img_x, img_y))
    
    def draw_controls(self):
        """Dibuja la pantalla de controles con diseño moderno glassmorphism espacial"""
        # === TÍTULO CON EFECTO NEÓN ===
        title_text = "CONTROLES"
        title_surface = self.font_large.render(title_text, True, CYAN)
        title_shadow = self.font_large.render(title_text, True, (0, 0, 0))
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 55))
        
        # Glow del título
        glow_surface = pygame.Surface((title_rect.width + 40, title_rect.height + 20), pygame.SRCALPHA)
        for i in range(8):
            alpha = int(25 - i * 3)
            pygame.draw.rect(glow_surface, (0, 200, 255, alpha),
                           (i*2, i*2, title_rect.width + 40 - i*4, title_rect.height + 20 - i*4),
                           border_radius=10)
        self.screen.blit(glow_surface, (title_rect.x - 20, title_rect.y - 10))
        self.screen.blit(title_shadow, (title_rect.x + 2, title_rect.y + 2))
        self.screen.blit(title_surface, title_rect)
        
        # === PANEL PRINCIPAL CON GLASSMORPHISM ===
        panel_width = 700
        panel_height = 520
        panel_x = (SCREEN_WIDTH - panel_width) // 2
        panel_y = 95
        
        # Glow externo del panel
        glow_panel = pygame.Surface((panel_width + 30, panel_height + 30), pygame.SRCALPHA)
        for i in range(4):
            alpha = int(30 - i * 7)
            pygame.draw.rect(glow_panel, (0, 180, 220, alpha),
                           (i*3, i*3, panel_width + 30 - i*6, panel_height + 30 - i*6),
                           border_radius=20 + i*2)
        self.screen.blit(glow_panel, (panel_x - 15, panel_y - 15))
        
        # Panel con glassmorphism
        panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(panel, (15, 30, 50, 200), (0, 0, panel_width, panel_height), border_radius=18)
        
        # Borde neón brillante
        pygame.draw.rect(panel, (0, 200, 255), (0, 0, panel_width, panel_height), width=3, border_radius=18)
        
        # Línea de brillo superior
        highlight = pygame.Surface((panel_width - 40, 2), pygame.SRCALPHA)
        highlight.fill((255, 255, 255, 50))
        panel.blit(highlight, (20, 8))
        
        self.screen.blit(panel, (panel_x, panel_y))
        
        # === SECCIÓN: CONTROLES DE JUEGO (TECLAS VISUALES) ===
        section_y = panel_y + 30
        
        # Header de sección
        header_text = "⌨ CONTROLES DE JUEGO"
        header_surface = self.font_medium.render(header_text, True, GOLD)
        header_rect = header_surface.get_rect(center=(SCREEN_WIDTH // 2, section_y))
        self.screen.blit(header_surface, header_rect)
        
        # Línea decorativa bajo header
        line_width = 280
        line_x = SCREEN_WIDTH // 2 - line_width // 2
        pygame.draw.line(self.screen, (255, 215, 0, 100), (line_x, section_y + 18), (line_x + line_width, section_y + 18), 2)
        
        # === TECLAS VISUALES ESTILO TECLADO ===
        keys_y = section_y + 45
        key_size = 55
        spacing = 155
        start_x = SCREEN_WIDTH // 2 - (spacing * 1.5)
        
        key_configs = [
            ('W', '+', 'Suma', (50, 255, 100)),            # Verde
            ('A', '−', 'Resta', (255, 100, 100)),          # Rojo
            ('S', '×', 'Multiplicación', (100, 200, 255)), # Azul
            ('D', '÷', 'División', (255, 200, 100))        # Naranja
        ]
        
        for i, (key, symbol, label, color) in enumerate(key_configs):
            x = int(start_x + i * spacing)
            
            # Sombra de la tecla
            shadow_rect = pygame.Rect(x + 3, keys_y + 3, key_size, key_size)
            pygame.draw.rect(self.screen, (0, 0, 0, 150), shadow_rect, border_radius=10)
            
            # Fondo de la tecla con gradiente
            key_surface = pygame.Surface((key_size, key_size), pygame.SRCALPHA)
            for j in range(key_size):
                progress = j / key_size
                r = int(30 + progress * 20)
                g = int(40 + progress * 25)
                b = int(60 + progress * 30)
                pygame.draw.line(key_surface, (r, g, b, 230), (0, j), (key_size, j))
            
            # Borde de la tecla con color de la operación
            pygame.draw.rect(key_surface, color, (0, 0, key_size, key_size), width=3, border_radius=10)
            
            # Efecto de brillo superior
            pygame.draw.line(key_surface, (255, 255, 255, 80), (10, 5), (key_size - 10, 5), 2)
            
            self.screen.blit(key_surface, (x, keys_y))
            
            # Letra de la tecla
            key_text = self.font_medium.render(key, True, WHITE)
            key_text_rect = key_text.get_rect(center=(x + key_size // 2, keys_y + key_size // 2 - 5))
            self.screen.blit(key_text, key_text_rect)
            
            # Símbolo de operación debajo
            symbol_text = self.font_medium.render(symbol, True, color)
            symbol_rect = symbol_text.get_rect(center=(x + key_size // 2, keys_y + key_size + 20))
            self.screen.blit(symbol_text, symbol_rect)
            
            # Etiqueta
            label_text = self.font_tiny.render(label, True, color)
            label_rect = label_text.get_rect(center=(x + key_size // 2, keys_y + key_size + 42))
            self.screen.blit(label_text, label_rect)
        
        # === SECCIÓN: NAVEGACIÓN ===
        nav_y = keys_y + key_size + 70
        
        nav_header = "🎮 NAVEGACIÓN"
        nav_surface = self.font_medium.render(nav_header, True, GOLD)
        nav_rect = nav_surface.get_rect(center=(SCREEN_WIDTH // 2, nav_y))
        self.screen.blit(nav_surface, nav_rect)
        
        # Línea decorativa
        pygame.draw.line(self.screen, (255, 215, 0, 100), (line_x, nav_y + 18), (line_x + line_width, nav_y + 18), 2)
        
        # Controles de navegación en mini-cards
        nav_items = [
            ("ESC", "Menú / Pausa", CYAN),
            ("R", "Reiniciar", YELLOW),
            ("F11", "Pantalla Completa", PURPLE)
        ]
        
        nav_card_y = nav_y + 35
        card_width = 180
        card_height = 50
        card_spacing = 200
        nav_start_x = SCREEN_WIDTH // 2 - card_spacing
        
        for i, (key, desc, color) in enumerate(nav_items):
            cx = nav_start_x + i * card_spacing
            
            # Mini card con glassmorphism
            card = pygame.Surface((card_width, card_height), pygame.SRCALPHA)
            pygame.draw.rect(card, (20, 35, 55, 180), (0, 0, card_width, card_height), border_radius=12)
            pygame.draw.rect(card, color, (0, 0, card_width, card_height), width=2, border_radius=12)
            self.screen.blit(card, (cx - card_width // 2, nav_card_y))
            
            # Tecla
            key_surf = self.font_small.render(key, True, color)
            key_r = key_surf.get_rect(center=(cx, nav_card_y + 18))
            self.screen.blit(key_surf, key_r)
            
            # Descripción
            desc_surf = self.font_tiny.render(desc, True, (180, 180, 180))
            desc_r = desc_surf.get_rect(center=(cx, nav_card_y + 38))
            self.screen.blit(desc_surf, desc_r)
        
        # === SECCIÓN: INSTRUCCIONES ===
        inst_y = nav_card_y + card_height + 35
        
        inst_header = "📋 INSTRUCCIONES"
        inst_surface = self.font_medium.render(inst_header, True, GOLD)
        inst_rect = inst_surface.get_rect(center=(SCREEN_WIDTH // 2, inst_y))
        self.screen.blit(inst_surface, inst_rect)
        
        pygame.draw.line(self.screen, (255, 215, 0, 100), (line_x, inst_y + 18), (line_x + line_width, inst_y + 18), 2)
        
        # Instrucciones con iconos - CENTRADAS
        instructions = [
            ("✓", "Respuesta correcta → ¡Disparas!", GREEN),
            ("✗", "Respuesta incorrecta → Te atacan", RED),
            ("⚡", "Derrota todos los enemigos", YELLOW)
        ]
        
        inst_item_y = inst_y + 35
        for icon, text, color in instructions:
            # Renderizar icono y texto
            icon_surf = self.font_small.render(icon, True, color)
            text_surf = self.font_small.render(text, True, WHITE)
            
            # Calcular ancho total para centrar
            total_width = icon_surf.get_width() + 10 + text_surf.get_width()
            start_x = SCREEN_WIDTH // 2 - total_width // 2
            
            # Dibujar icono
            self.screen.blit(icon_surf, (start_x, inst_item_y - icon_surf.get_height() // 2))
            
            # Dibujar texto
            self.screen.blit(text_surf, (start_x + icon_surf.get_width() + 10, inst_item_y - text_surf.get_height() // 2))
            
            inst_item_y += 28
        
        # === BOTÓN VOLVER ===
        for button in self.controls_buttons:
            button.draw(self.screen)
    
    def draw_settings(self):
        """Dibuja la pantalla de configuración de sonido con sliders modernos"""
        # Título elegante
        title_text = "CONFIGURACIÓN DE SONIDO"
        title_surface = self.font_large.render(title_text, True, PURPLE)
        title_shadow = self.font_large.render(title_text, True, (0, 0, 0, 150))
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 70))
        self.screen.blit(title_shadow, (title_rect.x + 2, title_rect.y + 2))
        self.screen.blit(title_surface, title_rect)
        
        # Panel de configuración con diseño moderno
        panel_width = 650
        panel_height = 380
        panel_x = (SCREEN_WIDTH - panel_width) // 2
        panel_y = 130
        
        # Panel con gradiente
        panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        for i in range(panel_height):
            progress = i / panel_height
            alpha = int(220 * (0.7 + progress * 0.3))
            r = int(30 * (1 - progress * 0.2))
            g = int(20 * (1 - progress * 0.2))
            b = int(40 * (1 - progress * 0.2))
            pygame.draw.line(panel, (r, g, b, alpha), (0, i), (panel_width, i))
        
        pygame.draw.rect(panel, (255, 255, 255, 150), (0, 0, panel_width, panel_height), 3)
        shadow = pygame.Surface((panel_width + 10, panel_height + 10), pygame.SRCALPHA)
        shadow.fill((0, 0, 0, 100))
        self.screen.blit(shadow, (panel_x - 5, panel_y - 5))
        self.screen.blit(panel, (panel_x, panel_y))
        
        # Volumen de música
        music_y = panel_y + 60
        music_label = self.font_medium.render("VOLUMEN DE MÚSICA", True, CYAN)
        music_label_rect = music_label.get_rect(center=(SCREEN_WIDTH // 2, music_y))
        self.screen.blit(music_label, music_label_rect)
        
        # Slider de música
        slider_y = music_y + 50
        self.music_slider.rect.y = slider_y
        self.music_slider.draw(self.screen)
        
        # Texto del volumen de música
        volume_text = self.font_small.render(f"{int(self.music_volume * 100)}%", True, WHITE)
        volume_rect = volume_text.get_rect(center=(SCREEN_WIDTH // 2, slider_y + 35))
        self.screen.blit(volume_text, volume_rect)
        
        # Instrucciones para música
        music_inst = self.font_tiny.render("Arrastra el control deslizante para ajustar", True, (200, 200, 200))
        inst_rect = music_inst.get_rect(center=(SCREEN_WIDTH // 2, slider_y + 55))
        self.screen.blit(music_inst, inst_rect)
        
        # Volumen de efectos de sonido
        sound_y = music_y + 180
        sound_label = self.font_medium.render("VOLUMEN DE EFECTOS", True, CYAN)
        sound_label_rect = sound_label.get_rect(center=(SCREEN_WIDTH // 2, sound_y))
        self.screen.blit(sound_label, sound_label_rect)
        
        # Slider de efectos
        sound_slider_y = sound_y + 50
        self.sound_slider.rect.y = sound_slider_y
        self.sound_slider.draw(self.screen)
        
        # Texto del volumen de efectos
        sound_volume_text = self.font_small.render(f"{int(self.sound_volume * 100)}%", True, WHITE)
        sound_volume_rect = sound_volume_text.get_rect(center=(SCREEN_WIDTH // 2, sound_slider_y + 35))
        self.screen.blit(sound_volume_text, sound_volume_rect)
        
        # Instrucciones para efectos
        sound_inst = self.font_tiny.render("Arrastra el control deslizante para ajustar", True, (200, 200, 200))
        sound_inst_rect = sound_inst.get_rect(center=(SCREEN_WIDTH // 2, sound_slider_y + 55))
        self.screen.blit(sound_inst, sound_inst_rect)
        
        # Dibujar botón volver
        for button in self.settings_buttons:
            button.draw(self.screen)
    
    def draw_level_intro(self):
        """Dibuja la introducción del nivel con pixel art"""
        
        # Si es modo infinito, mostrar pantalla especial
        if self.modo_infinito and self.infinite_mode:
            # Obtener información de la oleada actual
            wave_num = self.infinite_mode.wave
            difficulty = self.infinite_mode._get_difficulty_label()
            wave_config = self.infinite_mode.get_current_config()
            
            # Título principal con número de oleada
            if wave_num == 1:
                main_title = "MODO INFINITO"
            else:
                main_title = f"WAVE {wave_num}"
            
            # Efecto pixel art con múltiples capas
            for i in range(5):
                offset = i
                alpha = 255 - (i * 50)
                if alpha > 0:
                    color = (PURPLE[0], PURPLE[1], PURPLE[2])
                    if i > 0:
                        color = (max(0, color[0] - i*20), max(0, color[1] - i*20), max(0, color[2] - i*20))
                    title_surface = self.font_pixel.render(main_title, True, color)
                    title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2 + offset, 180 + offset))
                    self.screen.blit(title_surface, title_rect)
            
            # Título principal
            title_surface = self.font_pixel.render(main_title, True, PURPLE)
            title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 180))
            self.screen.blit(title_surface, title_rect)
            
            # Borde pixel art
            border_size = 4
            pygame.draw.rect(self.screen, PURPLE, 
                            (title_rect.x - border_size, title_rect.y - border_size,
                             title_rect.width + border_size * 2, title_rect.height + border_size * 2), 
                            border_size)
            
            # Mostrar dificultad y estadísticas
            diff_text = self.font_large.render(difficulty, True, CYAN)
            diff_rect = diff_text.get_rect(center=(SCREEN_WIDTH // 2, 260))
            self.screen.blit(diff_text, diff_rect)
            
            # Info de la oleada
            enemies_info = f"Enemigos: {wave_config['num_enemies']} | HP: {wave_config['enemy_hp']}"
            info_text = self.font_medium.render(enemies_info, True, PINK)
            info_rect = info_text.get_rect(center=(SCREEN_WIDTH // 2, 320))
            self.screen.blit(info_text, info_rect)
            
            # Tiempo predicho
            if self.tiempo_adaptativo:
                tiempo_info = f"Tiempo: {self.tiempo_adaptativo.tiempo_actual:.1f}s (adaptativo)"
                tiempo_text = self.font_small.render(tiempo_info, True, GOLD)
                tiempo_rect = tiempo_text.get_rect(center=(SCREEN_WIDTH // 2, 360))
                self.screen.blit(tiempo_text, tiempo_rect)
            
            # Instrucción adicional
            hint_text = self.font_tiny.render("¡Sobrevive el mayor tiempo posible!", True, (180, 180, 180))
            hint_rect = hint_text.get_rect(center=(SCREEN_WIDTH // 2, 400))
            self.screen.blit(hint_text, hint_rect)
        
        else:
            # Modo normal con niveles
            level_text = f"NIVEL {self.level}"
            
            # Crear efecto pixel art con múltiples capas
            for i in range(5):
                offset = i
                alpha = 255 - (i * 50)
                if alpha > 0:
                    color = (YELLOW[0], YELLOW[1], YELLOW[2])
                    if i > 0:
                        color = (color[0] - i*20, color[1] - i*20, color[2] - i*20)
                    level_surface = self.font_pixel.render(level_text, True, color)
                    level_rect = level_surface.get_rect(center=(SCREEN_WIDTH // 2 + offset, 200 + offset))
                    self.screen.blit(level_surface, level_rect)
            
            # Título principal
            level_surface = self.font_pixel.render(level_text, True, YELLOW)
            level_rect = level_surface.get_rect(center=(SCREEN_WIDTH // 2, 200))
            self.screen.blit(level_surface, level_rect)
            
            # Borde pixel art
            border_size = 4
            pygame.draw.rect(self.screen, YELLOW, 
                            (level_rect.x - border_size, level_rect.y - border_size,
                             level_rect.width + border_size * 2, level_rect.height + border_size * 2), 
                            border_size)
            
            # Descripción del nivel
            descriptions = {
                1: "Espacio Azul - Naves Básicas",
                2: "Nebulosa Púrpura - Naves Intermedias",
                3: "Espacio Rojo - Naves Avanzadas"
            }
            
            desc_text = self.font_medium.render(descriptions[self.level], True, CYAN)
            desc_rect = desc_text.get_rect(center=(SCREEN_WIDTH // 2, 280))
            self.screen.blit(desc_text, desc_rect)
        
        # Contador o texto de espera
        if self.level_intro_timer > 0:
            wait_text = self.font_small.render(
                f"Preparándose... {self.level_intro_timer // 60 + 1}", True, WHITE
            )
        else:
            wait_text = self.font_small.render("Presiona ESPACIO para comenzar", True, GREEN)
        wait_rect = wait_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100))
        self.screen.blit(wait_text, wait_rect)

    
    def draw_pause_menu(self):
        """Dibuja el menú de pausa durante el juego"""
        # Overlay semitransparente oscuro
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # Panel central con diseño moderno
        panel_width = 500
        panel_height = 450
        panel_x = (SCREEN_WIDTH - panel_width) // 2
        panel_y = (SCREEN_HEIGHT - panel_height) // 2
        
        # Panel con gradiente
        panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        for i in range(panel_height):
            progress = i / panel_height
            alpha = int(240 * (0.8 + progress * 0.2))
            r = int(15 * (1 - progress * 0.3))
            g = int(15 * (1 - progress * 0.3))
            b = int(25 * (1 - progress * 0.3))
            pygame.draw.line(panel, (r, g, b, alpha), (0, i), (panel_width, i))
        
        # Borde elegante
        pygame.draw.rect(panel, (255, 255, 255, 180), (0, 0, panel_width, panel_height), 4)
        
        # Sombra del panel
        shadow = pygame.Surface((panel_width + 15, panel_height + 15), pygame.SRCALPHA)
        shadow.fill((0, 0, 0, 120))
        self.screen.blit(shadow, (panel_x - 7, panel_y - 7))
        self.screen.blit(panel, (panel_x, panel_y))
        
        # Título del menú de pausa
        pause_title = self.font_large.render("JUEGO PAUSADO", True, YELLOW)
        pause_shadow = self.font_large.render("JUEGO PAUSADO", True, (0, 0, 0, 150))
        pause_rect = pause_title.get_rect(center=(SCREEN_WIDTH // 2, panel_y + 50))
        self.screen.blit(pause_shadow, (pause_rect.x + 2, pause_rect.y + 2))
        self.screen.blit(pause_title, pause_rect)
        
        # Línea decorativa
        line_width = 300
        line_x = SCREEN_WIDTH // 2 - line_width // 2
        pygame.draw.line(self.screen, (YELLOW[0]//2, YELLOW[1]//2, YELLOW[2]//2, 150),
                        (line_x, panel_y + 90), (line_x + line_width, panel_y + 90), 3)
        
        # Dibujar botones del menú de pausa
        for button in self.pause_buttons:
            button.draw(self.screen)
        
        # Instrucción
        hint_text = self.font_tiny.render("Presiona ESC para reanudar", True, (200, 200, 200))
        hint_rect = hint_text.get_rect(center=(SCREEN_WIDTH // 2, panel_y + panel_height - 30))
        self.screen.blit(hint_text, hint_rect)
    
    def draw(self):
        """Dibuja todos los elementos del juego"""
        # Dibujar fondo
        self.draw_background()
        
        if self.game_state == "menu":
            self.draw_menu()
        elif self.game_state == "controls":
            self.draw_controls()
        elif self.game_state == "settings":
            self.draw_settings()
        elif self.game_state == "level_intro":
            self.draw_level_intro()
        elif self.game_state == "playing":
            # Aplicar screen shake
            shake_offset_x = 0
            shake_offset_y = 0
            if self.screen_shake > 0:
                shake_offset_x = random.randint(-int(self.screen_shake_intensity), int(self.screen_shake_intensity))
                shake_offset_y = random.randint(-int(self.screen_shake_intensity), int(self.screen_shake_intensity))
            
            # Crear superficie temporal para aplicar shake
            if shake_offset_x != 0 or shake_offset_y != 0:
                game_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                game_surface.blit(self.screen, (0, 0))
            
            # Dibujar elementos del juego
            self.player.draw(self.screen)
            
            # Dibujar enemigos
            for enemy in self.enemies:
                enemy.draw(self.screen)
            
            # Dibujar explosiones
            for explosion in self.explosions:
                explosion.draw(self.screen)
            
            # Dibujar proyectiles
            for projectile in self.player_projectiles:
                projectile.draw(self.screen)
            
            for projectile in self.enemy_projectiles:
                projectile.draw(self.screen)
            
            # Dibujar efectos de combo (encima de todo excepto UI)
            for effect in self.combo_effects:
                if hasattr(effect, 'draw'):
                    if isinstance(effect, ComboTextPopup):
                        effect.draw(self.screen, self.font_large)
                    else:
                        effect.draw(self.screen)
            
            # Screen flash (overlay blanco)
            if self.screen_flash > 0:
                flash_alpha = int(150 * (self.screen_flash / 15))
                flash_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                flash_surface.fill((255, 255, 200, flash_alpha))
                self.screen.blit(flash_surface, (0, 0))
            
            self.draw_ui()
            
            # Dibujar indicador de combo (encima de la UI)
            if self.combo_streak > 0:
                self.combo_indicator.draw(self.screen, self.font_tiny)
            
            # Dibujar mascota (encima de la UI)
            self.mascota.draw(self.screen)
        elif self.game_state == "paused":
            # Dibujar elementos del juego (fondo)
            self.player.draw(self.screen)
            for enemy in self.enemies:
                enemy.draw(self.screen)
            for explosion in self.explosions:
                explosion.draw(self.screen)
            for projectile in self.player_projectiles:
                projectile.draw(self.screen)
            for projectile in self.enemy_projectiles:
                projectile.draw(self.screen)
            
            # Dibujar menú de pausa
            self.draw_pause_menu()
        elif self.game_state == "pre_victory":
            # Dibujar estado de pre-victoria (animación del robot celebrando)
            self.player.draw(self.screen)
            
            # Dibujar explosiones restantes
            for explosion in self.explosions:
                explosion.draw(self.screen)
            
            # Dibujar efectos de combo
            for effect in self.combo_effects:
                if hasattr(effect, 'draw'):
                    if isinstance(effect, ComboTextPopup):
                        effect.draw(self.screen, self.font_large)
                    else:
                        effect.draw(self.screen)
            
            # Dibujar animación de celebración
            if self.victory_celebration:
                self.victory_celebration.draw(self.screen)
        elif self.game_state == "victory":
            # Dibujar pantalla de victoria (completó nivel 3)
            self.player.draw(self.screen)
            for explosion in self.explosions:
                explosion.draw(self.screen)
            self.draw_victory_screen()
        else:
            # Dibujar pantalla de derrota (game over)
            self.player.draw(self.screen)
            for enemy in self.enemies:
                enemy.draw(self.screen)
            for explosion in self.explosions:
                explosion.draw(self.screen)
            self.draw_game_over()
        
        pygame.display.flip()
    
    def run(self):
        """Bucle principal del juego"""
        while self.running:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
            
            keys = pygame.key.get_pressed()
            self.handle_input(keys, events)
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()
