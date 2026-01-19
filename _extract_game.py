# Script to extract Game class and create game.py
import os

# Read original main.py
with open(r'main.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Extract Game class lines (2021-3893, but 0-indexed is 2020-3892)
game_lines = lines[2020:3893]

# Create the imports header
header = '''# -*- coding: utf-8 -*-
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
from effects import Explosion, MenuParticle, FloatingMathSymbol
from ui import Button, Slider
from systems import MathProblem, TiempoAdaptativo, SoundManager
from visuals import SpaceObject


'''

# Write game.py
with open(r'game.py', 'w', encoding='utf-8') as f:
    f.write(header)
    f.writelines(game_lines)

print('game.py created successfully!')
