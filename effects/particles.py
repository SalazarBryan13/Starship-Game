# -*- coding: utf-8 -*-
"""
Clases de partículas para efectos visuales del menú
"""

import pygame
import random
import math

from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, CYAN, YELLOW, GOLD, 
    ORANGE, GREEN, PURPLE, PINK
)


class MenuParticle:
    """Partículas decorativas para el fondo del menú"""
    def __init__(self, particle_type='star'):
        self.type = particle_type  # 'star', 'dust', 'spark'
        self.reset()
        
    def reset(self):
        """Reinicia la partícula en una posición inicial"""
        if self.type == 'star':
            # Estrellas fugaces - empiezan desde la derecha
            self.x = SCREEN_WIDTH + random.randint(0, 100)
            self.y = random.randint(0, SCREEN_HEIGHT)
            self.speed_x = -random.uniform(8, 15)
            self.speed_y = random.uniform(2, 5)
            self.size = random.randint(2, 4)
            self.life = random.randint(40, 80)
            self.max_life = self.life
            self.color = random.choice([WHITE, CYAN, (200, 200, 255)])
            self.trail = []
        elif self.type == 'dust':
            # Polvo cósmico - movimiento lento parallax
            self.x = random.randint(0, SCREEN_WIDTH)
            self.y = random.randint(0, SCREEN_HEIGHT)
            self.speed_x = -random.uniform(0.2, 1.0)
            self.speed_y = random.uniform(-0.3, 0.3)
            self.size = random.randint(1, 3)
            self.life = random.randint(200, 400)
            self.max_life = self.life
            self.alpha = random.randint(30, 100)
            self.color = random.choice([(100, 100, 150), (80, 80, 120), (120, 100, 140)])
            self.trail = []
        elif self.type == 'spark':
            # Chispas de energía
            self.x = random.randint(0, SCREEN_WIDTH)
            self.y = random.randint(0, SCREEN_HEIGHT)
            self.speed_x = random.uniform(-3, 3)
            self.speed_y = random.uniform(-3, 3)
            self.size = random.randint(1, 2)
            self.life = random.randint(20, 40)
            self.max_life = self.life
            self.color = random.choice([YELLOW, GOLD, ORANGE, CYAN])
            self.trail = []
    
    def update(self):
        """Actualiza la posición de la partícula"""
        # Guardar posición para la estela
        if self.type == 'star':
            self.trail.append((self.x, self.y))
            if len(self.trail) > 8:
                self.trail.pop(0)
        
        self.x += self.speed_x
        self.y += self.speed_y
        self.life -= 1
        
        # Reiniciar si se sale de pantalla o muere
        if self.life <= 0 or self.x < -50 or self.x > SCREEN_WIDTH + 50:
            self.reset()
    
    def draw(self, screen):
        """Dibuja la partícula con efectos visuales"""
        alpha_factor = self.life / self.max_life
        
        if self.type == 'star':
            # Dibujar estela de la estrella fugaz
            for i, (tx, ty) in enumerate(self.trail):
                trail_alpha = int(150 * (i / len(self.trail)) * alpha_factor)
                trail_size = max(1, int(self.size * (i / len(self.trail))))
                trail_surface = pygame.Surface((trail_size * 2, trail_size * 2), pygame.SRCALPHA)
                pygame.draw.circle(trail_surface, (*self.color[:3], trail_alpha), 
                                 (trail_size, trail_size), trail_size)
                screen.blit(trail_surface, (int(tx) - trail_size, int(ty) - trail_size))
            
            # Dibujar estrella principal con brillo
            glow_size = self.size + 3
            glow_surface = pygame.Surface((glow_size * 4, glow_size * 4), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (*self.color[:3], int(80 * alpha_factor)), 
                             (glow_size * 2, glow_size * 2), glow_size * 2)
            pygame.draw.circle(glow_surface, (*self.color[:3], int(200 * alpha_factor)), 
                             (glow_size * 2, glow_size * 2), self.size)
            screen.blit(glow_surface, (int(self.x) - glow_size * 2, int(self.y) - glow_size * 2))
            
        elif self.type == 'dust':
            # Polvo con transparencia
            dust_surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(dust_surface, (*self.color[:3], int(self.alpha * alpha_factor)), 
                             (self.size, self.size), self.size)
            screen.blit(dust_surface, (int(self.x), int(self.y)))
            
        elif self.type == 'spark':
            # Chispa brillante
            spark_surface = pygame.Surface((self.size * 4, self.size * 4), pygame.SRCALPHA)
            pygame.draw.circle(spark_surface, (*self.color[:3], int(200 * alpha_factor)), 
                             (self.size * 2, self.size * 2), self.size)
            screen.blit(spark_surface, (int(self.x) - self.size * 2, int(self.y) - self.size * 2))


class FloatingMathSymbol:
    """Símbolos matemáticos flotantes para el menú"""
    def __init__(self):
        self.symbols = ['+', '-', '×', '÷', '=', '∞', '√', 'π']
        self.reset()
        
    def reset(self):
        """Reinicia el símbolo en una nueva posición"""
        self.symbol = random.choice(self.symbols)
        self.x = random.randint(50, SCREEN_WIDTH - 50)
        self.y = SCREEN_HEIGHT + 50
        self.speed_y = -random.uniform(0.5, 1.5)
        self.speed_x = random.uniform(-0.3, 0.3)
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-2, 2)
        self.size = random.randint(24, 48)
        self.life = random.randint(300, 500)
        self.max_life = self.life
        self.pulse_offset = random.uniform(0, math.pi * 2)
        self.color = random.choice([CYAN, YELLOW, GOLD, GREEN, PURPLE, PINK])
        
    def update(self):
        """Actualiza la posición del símbolo"""
        self.x += self.speed_x
        self.y += self.speed_y
        self.rotation += self.rotation_speed
        self.life -= 1
        
        # Movimiento ondulante
        self.x += math.sin(pygame.time.get_ticks() * 0.002 + self.pulse_offset) * 0.5
        
        if self.life <= 0 or self.y < -50:
            self.reset()
    
    def draw(self, screen, font):
        """Dibuja el símbolo con efectos de brillo"""
        alpha_factor = min(1.0, self.life / 100)  # Fade in/out
        if self.life > self.max_life - 50:
            alpha_factor = (self.max_life - self.life) / 50
        
        # Pulso de brillo
        pulse = (math.sin(pygame.time.get_ticks() * 0.005 + self.pulse_offset) + 1) / 2
        glow_intensity = int(100 + 100 * pulse)
        
        # Crear superficie con rotación
        try:
            symbol_font = pygame.font.Font(None, self.size)
            text_surface = symbol_font.render(self.symbol, True, self.color)
            
            # Rotar el símbolo
            rotated = pygame.transform.rotate(text_surface, self.rotation)
            
            # Aplicar transparencia
            rotated.set_alpha(int(200 * alpha_factor))
            
            # Dibujar brillo detrás
            glow_surface = pygame.Surface((rotated.get_width() + 20, rotated.get_height() + 20), pygame.SRCALPHA)
            glow_color = (*self.color[:3], int(glow_intensity * alpha_factor * 0.3))
            pygame.draw.circle(glow_surface, glow_color, 
                             (glow_surface.get_width() // 2, glow_surface.get_height() // 2),
                             max(rotated.get_width(), rotated.get_height()) // 2 + 5)
            screen.blit(glow_surface, (int(self.x) - glow_surface.get_width() // 2, 
                                       int(self.y) - glow_surface.get_height() // 2))
            
            # Dibujar símbolo
            rect = rotated.get_rect(center=(int(self.x), int(self.y)))
            screen.blit(rotated, rect)
        except:
            pass  # Ignorar errores de renderizado
