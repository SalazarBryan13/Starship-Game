# -*- coding: utf-8 -*-
"""
SpaceObject - Objetos decorativos del espacio
"""

import pygame
import random
import math

from config import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE


class SpaceObject:
    """Objetos decorativos del espacio (asteroides, planetas, nebulosas)"""
    
    def __init__(self, obj_type, x, y, level=1):
        self.type = obj_type  # 'asteroid', 'planet', 'nebula', 'comet'
        self.x = x
        self.y = y
        self.level = level
        self.rotation = 0
        self.rotation_speed = random.uniform(-2, 2)
        self.size = random.randint(20, 60) if obj_type == 'asteroid' else random.randint(40, 100)
        
        # Velocidad de movimiento
        if obj_type == 'comet':
            self.vx = random.uniform(-1, 1)
            self.vy = random.uniform(0.5, 2)
        else:
            self.vx = random.uniform(-0.5, 0.5)
            self.vy = random.uniform(0.2, 1)
    
    def update(self):
        """Actualiza la posición del objeto"""
        self.x += self.vx
        self.y += self.vy
        self.rotation += self.rotation_speed
        
        # Reposicionar si sale de pantalla
        if self.y > SCREEN_HEIGHT + 50:
            self.y = -50
            self.x = random.randint(0, SCREEN_WIDTH)
        if self.x < -50:
            self.x = SCREEN_WIDTH + 50
        elif self.x > SCREEN_WIDTH + 50:
            self.x = -50
    
    def draw(self, screen):
        """Dibuja el objeto según su tipo y nivel"""
        if self.type == 'asteroid':
            self._draw_asteroid(screen)
        elif self.type == 'planet':
            self._draw_planet(screen)
        elif self.type == 'nebula':
            self._draw_nebula(screen)
        elif self.type == 'comet':
            self._draw_comet(screen)
    
    def _draw_asteroid(self, screen):
        """Dibuja un asteroide"""
        # Color según nivel
        if self.level == 1:
            color = (100, 100, 120)
        elif self.level == 2:
            color = (120, 80, 120)
        else:
            color = (120, 60, 60)
        
        # Dibujar asteroide irregular
        points = []
        num_points = 8
        for i in range(num_points):
            angle = (2 * math.pi / num_points) * i + math.radians(self.rotation)
            radius_variation = self.size // 2 + random.randint(-5, 5)
            px = self.x + math.cos(angle) * radius_variation
            py = self.y + math.sin(angle) * radius_variation
            points.append((px, py))
        
        pygame.draw.polygon(screen, color, points)
        pygame.draw.polygon(screen, (color[0] + 30, color[1] + 30, color[2] + 30), points, 2)
        
        # Cráteres
        for _ in range(2):
            crater_x = self.x + random.randint(-self.size//3, self.size//3)
            crater_y = self.y + random.randint(-self.size//3, self.size//3)
            pygame.draw.circle(screen, (color[0] - 20, color[1] - 20, color[2] - 20), 
                             (int(crater_x), int(crater_y)), 3)
    
    def _draw_planet(self, screen):
        """Dibuja un planeta"""
        # Color según nivel
        if self.level == 1:
            base_color = (50, 100, 200)
            band_color = (30, 80, 180)
        elif self.level == 2:
            base_color = (150, 50, 150)
            band_color = (120, 30, 120)
        else:
            base_color = (200, 50, 50)
            band_color = (180, 30, 30)
        
        # Planeta principal
        pygame.draw.circle(screen, base_color, (int(self.x), int(self.y)), self.size)
        
        # Bandas del planeta
        for i in range(3):
            band_y = self.y - self.size + (i * self.size // 2)
            if -self.size < band_y - self.y < self.size:
                band_width = int(math.sqrt(self.size**2 - (band_y - self.y)**2) * 2)
                pygame.draw.ellipse(screen, band_color, 
                                  (self.x - band_width // 2, band_y - 2, band_width, 4))
        
        # Brillo
        pygame.draw.circle(screen, (base_color[0] + 50, base_color[1] + 50, base_color[2] + 50),
                         (int(self.x - self.size // 3), int(self.y - self.size // 3)), 
                         self.size // 4)
    
    def _draw_nebula(self, screen):
        """Dibuja una nebulosa"""
        # Color según nivel
        if self.level == 1:
            colors = [(50, 100, 200, 80), (100, 150, 255, 60)]
        elif self.level == 2:
            colors = [(150, 50, 200, 80), (200, 100, 255, 60)]
        else:
            colors = [(200, 50, 50, 80), (255, 100, 100, 60)]
        
        # Dibujar múltiples círculos superpuestos para efecto nebulosa
        for i, (r, g, b, alpha) in enumerate(colors):
            nebula_surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            offset = i * 10
            pygame.draw.ellipse(nebula_surface, (r, g, b, alpha),
                             (offset, offset, self.size * 2 - offset * 2, self.size * 2 - offset * 2))
            screen.blit(nebula_surface, (self.x - self.size, self.y - self.size))
    
    def _draw_comet(self, screen):
        """Dibuja un cometa"""
        # Cola del cometa
        tail_length = self.size * 2
        tail_points = [
            (self.x, self.y),
            (self.x - tail_length * 0.8, self.y - tail_length),
            (self.x - tail_length * 0.6, self.y - tail_length * 0.7),
            (self.x - tail_length * 0.4, self.y - tail_length * 0.4)
        ]
        
        # Color según nivel
        if self.level == 1:
            tail_color = (150, 200, 255)
        elif self.level == 2:
            tail_color = (200, 150, 255)
        else:
            tail_color = (255, 150, 150)
        
        # Dibujar cola con gradiente
        for i in range(len(tail_points) - 1):
            alpha = int(150 * (1 - i / len(tail_points)))
            tail_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            pygame.draw.line(tail_surface, (*tail_color, alpha), 
                           tail_points[i], tail_points[i + 1], 3)
            screen.blit(tail_surface, (0, 0))
        
        # Núcleo del cometa
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.size // 3)
        pygame.draw.circle(screen, tail_color, (int(self.x), int(self.y)), self.size // 4)
