# -*- coding: utf-8 -*-
"""
Operación Relámpago - Juego Educativo de Matemáticas
Punto de entrada principal
"""

import pygame
import os
import sys

# Asegurar que el directorio del script esté en el path
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

# Inicializar Pygame
pygame.init()
# Configuración mejorada del mixer para mejor calidad de sonido
pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=1024)
pygame.mixer.init()

# Importar la clase Game desde el módulo game
from game import Game


if __name__ == "__main__":
    game = Game()
    game.run()
