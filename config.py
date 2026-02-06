# -*- coding: utf-8 -*-
"""
Configuración y constantes del juego Nave Matemática
"""

import pygame
import os
import sys

# Constantes del juego
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 600
FPS = 60

# Detectar si estamos ejecutando en web (Pygbag)
# Pygbag establece ciertas variables de entorno y características
IS_WEB = (
    os.environ.get('PYGBAG', '').lower() == 'true' or
    'pygbag' in str(sys.modules) or
    hasattr(sys, '_getframe') and 'emscripten' in str(sys.platform)
)
# FPS reducido para web (mejor rendimiento)
# Balance: 25 FPS es aceptable y mejora significativamente el rendimiento
WEB_FPS = 25 if IS_WEB else 60

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

# Colores para diferentes niveles - CONTRASTAN con enemigos
# Nivel 1 - Espacio Profundo (Negro → Azul Marino) - Contrasta con enemigos AZULES/CYAN
L1_BG_START = (0, 0, 8)        # Negro casi puro con tinte azul
L1_BG_END = (8, 15, 40)        # Azul marino oscuro
L1_STAR = (200, 220, 255)      # Estrellas blanco-azuladas

# Nivel 2 - Nebulosa Teal (Teal profundo) - Contrasta con enemigos PÚRPURA/ROSA
L2_BG_START = (0, 25, 30)      # Teal profundo
L2_BG_END = (5, 50, 60)        # Cyan oscuro
L2_STAR = (150, 255, 235)      # Estrellas turquesa brillantes

# Nivel 3 - Corredor Violeta (Azul profundo → Violeta) - Contrasta con enemigos ROJOS/NARANJA
L3_BG_START = (20, 5, 35)      # Azul violáceo profundo
L3_BG_END = (40, 10, 65)       # Violeta oscuro
L3_STAR = (200, 170, 255)      # Estrellas violeta-blancas


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
