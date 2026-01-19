# -*- coding: utf-8 -*-
"""
Clase Explosion - Efectos visuales de explosión
"""

import pygame
import random
import math


class Explosion:
    """Clase para efectos de explosión cuando se destruyen naves"""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.particles = []
        self.life = 30  # Duración de la explosión en frames
        self.max_life = 30
        
        # Crear partículas de explosión
        for _ in range(20):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 8)
            size = random.randint(2, 5)
            color_choice = random.choice([
                (255, 200, 0),  # Amarillo
                (255, 100, 0),  # Naranja
                (255, 50, 0),   # Rojo
                (255, 255, 200) # Blanco amarillento
            ])
            self.particles.append({
                'x': x,
                'y': y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'size': size,
                'color': color_choice,
                'life': self.max_life
            })
    
    def update(self):
        """Actualiza las partículas de la explosión"""
        self.life -= 1
        
        for particle in self.particles:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['vx'] *= 0.95  # Fricción
            particle['vy'] *= 0.95
            particle['life'] -= 1
    
    def draw(self, screen):
        """Dibuja la explosión"""
        if self.life <= 0:
            return
        
        # Dibujar partículas
        for particle in self.particles:
            if particle['life'] > 0:
                alpha = int(255 * (particle['life'] / self.max_life))
                size = int(particle['size'] * (particle['life'] / self.max_life))
                if size > 0:
                    color = particle['color']
                    # Crear superficie con alpha
                    particle_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                    pygame.draw.circle(particle_surface, (*color, alpha), (size, size), size)
                    screen.blit(particle_surface, (particle['x'] - size, particle['y'] - size))
        
        # Efecto de onda expansiva
        if self.life > 15:
            wave_radius = (self.max_life - self.life) * 3
            wave_alpha = int(100 * (self.life / self.max_life))
            wave_surface = pygame.Surface((wave_radius * 2, wave_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(wave_surface, (255, 200, 0, wave_alpha), 
                             (wave_radius, wave_radius), wave_radius, 2)
            screen.blit(wave_surface, (self.x - wave_radius, self.y - wave_radius))
    
    def is_dead(self):
        """Verifica si la explosión terminó"""
        return self.life <= 0
