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
        
        # === OPTIMIZACIÓN: Precalcular puntos de asteroide ===
        if obj_type == 'asteroid':
            self._precalculate_asteroid_shape()
    
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
    
    def _precalculate_asteroid_shape(self):
        """Precalcula los puntos irregulares del asteroide (solo una vez)"""
        self._asteroid_radii = []
        num_points = 8
        for i in range(num_points):
            # Radio con variación aleatoria fija
            radius = self.size // 2 + random.randint(-5, 5)
            self._asteroid_radii.append(radius)
        
        # Precalcular posiciones de cráteres (relativas al centro)
        self._crater_offsets = []
        for _ in range(2):
            offset_x = random.randint(-self.size//3, self.size//3)
            offset_y = random.randint(-self.size//3, self.size//3)
            self._crater_offsets.append((offset_x, offset_y))
    
    def _draw_asteroid(self, screen):
        """Dibuja un asteroide (OPTIMIZADO - usa puntos precalculados)"""
        # Color según nivel - tonos que contrastan con el fondo
        if self.level == 1:
            color = (120, 130, 150)  # Gris azulado para fondo oscuro
        elif self.level == 2:
            color = (90, 140, 130)   # Gris verdoso para fondo teal
        else:
            color = (150, 120, 160)  # Gris violáceo para fondo violeta
        
        # Dibujar asteroide usando radios precalculados
        points = []
        num_points = 8
        for i in range(num_points):
            angle = (2 * math.pi / num_points) * i + math.radians(self.rotation)
            radius = self._asteroid_radii[i]
            px = self.x + math.cos(angle) * radius
            py = self.y + math.sin(angle) * radius
            points.append((px, py))
        
        pygame.draw.polygon(screen, color, points)
        pygame.draw.polygon(screen, (color[0] + 30, color[1] + 30, color[2] + 30), points, 2)
        
        # Cráteres con posiciones precalculadas
        crater_color = (max(0, color[0] - 20), max(0, color[1] - 20), max(0, color[2] - 20))
        for offset_x, offset_y in self._crater_offsets:
            pygame.draw.circle(screen, crater_color, 
                             (int(self.x + offset_x), int(self.y + offset_y)), 3)
    
    def _draw_planet(self, screen):
        """Dibuja un planeta"""
        # Color según nivel - colores vibrantes que contrastan con fondo
        if self.level == 1:
            base_color = (180, 140, 100)  # Marrón dorado (contrasta con azul marino)
            band_color = (150, 110, 70)
        elif self.level == 2:
            base_color = (200, 100, 80)   # Naranja coral (contrasta con teal)
            band_color = (170, 70, 50)
        else:
            base_color = (100, 200, 150)  # Verde esmeralda (contrasta con violeta)
            band_color = (70, 170, 120)
        
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
        # Color según nivel - tonos suaves que complementan sin confundir
        if self.level == 1:
            colors = [(180, 130, 80, 50), (220, 160, 100, 35)]   # Nebulosa dorada
        elif self.level == 2:
            colors = [(220, 120, 80, 50), (255, 150, 100, 35)]   # Nebulosa coral
        else:
            colors = [(80, 200, 150, 50), (120, 230, 180, 35)]   # Nebulosa esmeralda
        
        # Dibujar múltiples círculos superpuestos para efecto nebulosa
        for i, (r, g, b, alpha) in enumerate(colors):
            nebula_surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            offset = i * 10
            pygame.draw.ellipse(nebula_surface, (r, g, b, alpha),
                             (offset, offset, self.size * 2 - offset * 2, self.size * 2 - offset * 2))
            screen.blit(nebula_surface, (self.x - self.size, self.y - self.size))
    
    def _draw_comet(self, screen):
        """Dibuja un cometa (OPTIMIZADO - sin Surfaces de pantalla completa)"""
        # Cola del cometa
        tail_length = self.size * 2
        tail_points = [
            (self.x, self.y),
            (self.x - tail_length * 0.8, self.y - tail_length),
            (self.x - tail_length * 0.6, self.y - tail_length * 0.7),
            (self.x - tail_length * 0.4, self.y - tail_length * 0.4)
        ]
        
        # Color según nivel - colas brillantes que contrastan
        if self.level == 1:
            tail_color = (255, 220, 150)  # Dorado brillante
        elif self.level == 2:
            tail_color = (255, 180, 120)  # Naranja claro
        else:
            tail_color = (150, 255, 200)  # Verde menta brillante
        
        # OPTIMIZADO: Dibujar cola directamente en screen (sin crear Surfaces gigantes)
        for i in range(len(tail_points) - 1):
            # Usar grosor variable para simular desvanecimiento
            thickness = max(1, 4 - i)
            pygame.draw.line(screen, tail_color, 
                           tail_points[i], tail_points[i + 1], thickness)
        
        # Núcleo del cometa con glow simple
        pygame.draw.circle(screen, tail_color, (int(self.x), int(self.y)), self.size // 3 + 2)
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.size // 3)
        pygame.draw.circle(screen, tail_color, (int(self.x), int(self.y)), self.size // 4)
