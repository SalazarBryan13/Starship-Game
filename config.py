# -*- coding: utf-8 -*-
"""
Configuración y constantes del juego Nave Matemática
"""

import pygame

# Constantes del juego
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 600
FPS = 60

# Colores mejorados
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 50, 50)
DARK_RED = (180, 0, 0)
GREEN = (50, 255, 50)
DARK_GREEN = (0, 180, 0)
BLUE = (100, 150, 255)
DARK_BLUE = (50, 100, 200)
YELLOW = (255, 255, 100)
GOLD = (255, 215, 0)
ORANGE = (255, 165, 0)
PURPLE = (200, 100, 255)
CYAN = (100, 255, 255)
PINK = (255, 192, 203)
SILVER = (192, 192, 192)
DARK_PURPLE = (100, 50, 150)
STAR_COLOR = (200, 200, 255)

# Colores para diferentes niveles
# Colores para diferentes niveles
# Nivel 1 - Espacio Profundo (Casi Negro/Azul)
L1_BG_START = (0, 0, 5)       # Negro profundo
L1_BG_END = (5, 5, 20)        # Azul medianoche muy oscuro
L1_STAR = (150, 150, 180)     # Estrellas tenues

# Nivel 2 - Vacío Cósmico (Casi Negro/Púrpura)
L2_BG_START = (2, 0, 5)       # Negro con tinte índigo
L2_BG_END = (10, 5, 20)       # Púrpura cósmico muy oscuro
L2_STAR = (160, 140, 180)     # Estrellas violetas tenues

# Nivel 3 - Materia Oscura (Casi Negro/Rojo)
L3_BG_START = (5, 0, 0)       # Negro con tinte rojizo
L3_BG_END = (20, 5, 5)        # Rojo óxido muy oscuro
L3_STAR = (180, 140, 140)     # Estrellas rojizas tenues

# Configuración de niveles
LEVEL_CONFIG = {
    1: {"num_range": (1, 10), "enemy_hp": 3, "enemy_speed": 1},
    2: {"num_range": (1, 50), "enemy_hp": 5, "enemy_speed": 2},
    3: {"num_range": (1, 100), "enemy_hp": 8, "enemy_speed": 3}
}

# Mapeo de teclas a operaciones
KEY_TO_OPERATION = {
    pygame.K_w: "+",
    pygame.K_a: "-",
    pygame.K_s: "*",
    pygame.K_d: "/"
}

OPERATION_TO_KEY = {"+": "W", "-": "A", "*": "S", "/": "D"}

# Configuración de enemigos por nivel (cantidad de enemigos)
ENEMIES_PER_LEVEL = {
    1: 3,  # 3 enemigos en nivel 1
    2: 5,  # 5 enemigos en nivel 2
    3: 7   # 7 enemigos en nivel 3
}
