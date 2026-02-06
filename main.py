# -*- coding: utf-8 -*-
"""
Operación Relámpago - Juego Educativo de Matemáticas
Punto de entrada principal

Compatible con Pygbag para ejecución en navegador web.
"""

import pygame
import asyncio
import os
import sys

# Asegurar que el directorio del script esté en el path
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

# Detectar si estamos en web
IS_WEB = os.environ.get('PYGBAG', '').lower() == 'true'

# Inicializar Pygame
pygame.init()
# Configuración del mixer optimizada para web
if IS_WEB:
    # Configuración reducida para mejor rendimiento en web
    pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512)
else:
    # Configuración mejorada para desktop
    pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=1024)
pygame.mixer.init()

# Importar la clase Game desde el módulo game
from game import Game


async def main():
    """Función principal asíncrona para compatibilidad con Pygbag"""
    game = Game()
    await game.run()


if __name__ == "__main__":
    asyncio.run(main())
