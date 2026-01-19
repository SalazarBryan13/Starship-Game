# -*- coding: utf-8 -*-
"""
Clase Player - Nave del jugador
"""

import pygame
import random
import math

from config import (
    CYAN, BLUE, DARK_BLUE, YELLOW, WHITE, GOLD, SILVER,
    GREEN, RED, ORANGE, SCREEN_WIDTH, SCREEN_HEIGHT
)


class Player:
    """Clase para el jugador"""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 60
        self.height = 40
        self.lives = 5
        self.score = 0
        self.correct_answers = 0
        self.incorrect_answers = 0
        self.shoot_cooldown = 0
        self.engine_glow = 0  # Para animación de motores
        self.damage_flash = 0  # Contador para efecto de daño visual
        self.damage_particles = []  # Partículas de daño
        
        # Sistema de movimiento
        self.vx = 0  # Velocidad horizontal
        self.speed = 5  # Velocidad máxima de movimiento
        self.acceleration = 0.8  # Aceleración
        self.friction = 0.9  # Fricción para desaceleración suave
    
    def draw(self, screen):
        """Dibuja la nave del jugador con gráficos mejorados"""
        center_x = self.x + self.width // 2
        center_y = self.y + self.height // 2
        
        # Efecto visual de daño (parpadeo rojo)
        damage_alpha = 0
        if self.damage_flash > 0:
            # Parpadeo más intenso al inicio
            damage_alpha = int(180 * (self.damage_flash / 30))
            damage_overlay = pygame.Surface((self.width + 10, self.height + 10), pygame.SRCALPHA)
            damage_overlay.fill((255, 0, 0, damage_alpha))
            screen.blit(damage_overlay, (self.x - 5, self.y - 5))
        
        # Dibujar partículas de daño
        for particle in self.damage_particles:
            alpha = int(255 * (particle['life'] / 20))
            size = max(2, int(4 * (particle['life'] / 20)))
            particle_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, (*particle['color'], alpha), (size, size), size)
            screen.blit(particle_surface, (particle['x'] - size, particle['y'] - size))
        
        # Efecto de motores (glow animado)
        self.engine_glow = (self.engine_glow + 2) % 20
        glow_intensity = abs(10 - self.engine_glow) / 10
        
        # Motores traseros con efecto glow
        engine_color = (int(100 * glow_intensity), int(200 * glow_intensity), int(255 * glow_intensity))
        pygame.draw.circle(screen, engine_color, (center_x - 15, self.y + self.height + 5), 5)
        pygame.draw.circle(screen, engine_color, (center_x + 15, self.y + self.height + 5), 5)
        
        # Alas inferiores (mejoradas)
        left_wing = [
            (self.x - 5, self.y + self.height - 10),
            (self.x - 20, self.y + self.height + 20),
            (self.x + 5, self.y + self.height + 5)
        ]
        right_wing = [
            (self.x + self.width + 5, self.y + self.height - 10),
            (self.x + self.width + 20, self.y + self.height + 20),
            (self.x + self.width - 5, self.y + self.height + 5)
        ]
        pygame.draw.polygon(screen, CYAN, left_wing)
        pygame.draw.polygon(screen, CYAN, right_wing)
        pygame.draw.polygon(screen, BLUE, left_wing, 2)
        pygame.draw.polygon(screen, BLUE, right_wing, 2)
        
        # Cuerpo principal con gradiente simulado
        # Capa base
        pygame.draw.ellipse(screen, DARK_BLUE, (self.x, self.y, self.width, self.height))
        # Capa superior (brillo)
        pygame.draw.ellipse(screen, BLUE, (self.x + 5, self.y + 5, self.width - 10, self.height - 10))
        # Borde
        pygame.draw.ellipse(screen, CYAN, (self.x, self.y, self.width, self.height), 2)
        
        # Detalles del cuerpo (líneas de diseño)
        pygame.draw.line(screen, DARK_BLUE, (self.x + 10, self.y + 15), (self.x + self.width - 10, self.y + 15), 2)
        pygame.draw.line(screen, DARK_BLUE, (self.x + 10, self.y + 25), (self.x + self.width - 10, self.y + 25), 2)
        
        # Cabina con efecto de vidrio
        cabin_center = (center_x, self.y + 12)
        # Sombra de la cabina
        pygame.draw.circle(screen, DARK_BLUE, cabin_center, 12)
        # Cabina principal
        pygame.draw.circle(screen, YELLOW, cabin_center, 11)
        # Brillo de la cabina
        pygame.draw.circle(screen, WHITE, (center_x - 3, self.y + 9), 4)
        # Borde de la cabina
        pygame.draw.circle(screen, GOLD, cabin_center, 11, 2)
        
        # Cañones laterales
        pygame.draw.rect(screen, SILVER, (self.x - 3, self.y + 18, 6, 8))
        pygame.draw.rect(screen, SILVER, (self.x + self.width - 3, self.y + 18, 6, 8))
    
    def shoot(self):
        """Crea un disparo del jugador"""
        from entities.projectile import Projectile
        if self.shoot_cooldown <= 0:
            self.shoot_cooldown = 10
            return Projectile(self.x + self.width // 2, self.y, -8, GREEN, True)
        return None
    
    def take_damage(self):
        """El jugador recibe daño"""
        self.lives -= 1
        self.damage_flash = 30  # Activar efecto visual de daño (0.5 segundos a 60 FPS)
        
        # Crear partículas de daño
        center_x = self.x + self.width // 2
        center_y = self.y + self.height // 2
        for _ in range(10):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 6)
            self.damage_particles.append({
                'x': center_x,
                'y': center_y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'life': 20,
                'color': random.choice([RED, ORANGE, YELLOW])
            })
    
    def update(self):
        """Actualiza el estado del jugador"""
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        
        # Actualizar efecto de daño visual
        if self.damage_flash > 0:
            self.damage_flash -= 1
        
        # Actualizar partículas de daño
        for particle in self.damage_particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['vx'] *= 0.95
            particle['vy'] *= 0.95
            particle['life'] -= 1
            if particle['life'] <= 0:
                self.damage_particles.remove(particle)
        
        # La animación del motor se actualiza en draw()
    
    def move_left(self):
        """Acelera hacia la izquierda"""
        self.vx -= self.acceleration
        if self.vx < -self.speed:
            self.vx = -self.speed
    
    def move_right(self):
        """Acelera hacia la derecha"""
        self.vx += self.acceleration
        if self.vx > self.speed:
            self.vx = self.speed
    
    def apply_movement(self):
        """Aplica el movimiento y la fricción"""
        # Aplicar velocidad a posición
        self.x += self.vx
        
        # Aplicar fricción
        self.vx *= self.friction
        
        # Detener si la velocidad es muy baja
        if abs(self.vx) < 0.1:
            self.vx = 0
        
        # Mantener dentro de los límites de la pantalla
        if self.x < 0:
            self.x = 0
            self.vx = 0
        elif self.x > SCREEN_WIDTH - self.width:
            self.x = SCREEN_WIDTH - self.width
            self.vx = 0
