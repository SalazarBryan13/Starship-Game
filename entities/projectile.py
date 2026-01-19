# -*- coding: utf-8 -*-
"""
Clase Projectile - Proyectiles del juego
"""

import pygame
import math

from config import (
    CYAN, WHITE, DARK_RED, ORANGE, YELLOW, SCREEN_HEIGHT
)


class Projectile:
    """Clase para los proyectiles"""
    
    def __init__(self, x, y, speed, color, is_player_shot, target_enemy=None, target_player=None):
        self.x = x
        self.y = y
        self.speed = speed
        self.color = color
        self.is_player_shot = is_player_shot
        self.radius = 6
        self.particles = []
        self.trail_length = 8 if is_player_shot else 5
        self.glow_intensity = 15
        self.target_enemy = target_enemy  # Enemigo objetivo (para proyectiles del jugador)
        self.target_player = target_player  # Jugador objetivo (para proyectiles enemigos)
        
        # Calcular velocidad inicial
        if not is_player_shot and target_player:
            # Calcular dirección inicial hacia el jugador (solo una vez)
            target_x = target_player.x + target_player.width // 2
            target_y = target_player.y + target_player.height // 2
            dx = target_x - x
            dy = target_y - y
            distance = math.sqrt(dx * dx + dy * dy)
            
            if distance > 0:
                self.vx = (dx / distance) * abs(speed)
                self.vy = (dy / distance) * abs(speed)
            else:
                self.vx = 0
                self.vy = abs(speed)
        else:
            self.vx = 0
            self.vy = -speed if is_player_shot else speed  # Velocidad por defecto (arriba/abajo)
    
    def draw(self, screen):
        """Dibuja el proyectil con efectos visuales mejorados"""
        # Estela de partículas mejorada
        for i, (px, py, life) in enumerate(self.particles):
            alpha_ratio = life / self.trail_length
            size = max(2, int(self.radius * alpha_ratio * 0.8))
            
            # Color más brillante para la estela
            if self.is_player_shot:
                trail_color = (
                    min(255, self.color[0] + int(100 * alpha_ratio)),
                    min(255, self.color[1] + int(50 * alpha_ratio)),
                    self.color[2]
                )
            else:
                trail_color = (
                    min(255, self.color[0] + int(50 * alpha_ratio)),
                    self.color[1],
                    self.color[2]
                )
            
            pygame.draw.circle(screen, trail_color, (int(px), int(py)), size)
        
        # Glow exterior del proyectil
        glow_radius = self.radius + 3
        glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        for i in range(3):
            alpha = 50 - i * 15
            pygame.draw.circle(
                glow_surface, 
                (*self.color, alpha), 
                (glow_radius, glow_radius), 
                glow_radius - i
            )
        screen.blit(glow_surface, (self.x - glow_radius, self.y - glow_radius))
        
        # Núcleo del proyectil (brillante)
        if self.is_player_shot:
            # Proyectil del jugador - forma de energía
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
            pygame.draw.circle(screen, CYAN, (int(self.x), int(self.y)), self.radius - 2)
            pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radius - 4)
            # Rayos de energía
            for angle in [0, 90, 180, 270]:
                rad = math.radians(angle)
                end_x = self.x + math.cos(rad) * self.radius
                end_y = self.y + math.sin(rad) * self.radius
                pygame.draw.line(screen, WHITE, (self.x, self.y), (end_x, end_y), 2)
        else:
            # Proyectil del enemigo - forma de fuego
            pygame.draw.circle(screen, DARK_RED, (int(self.x), int(self.y)), self.radius)
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius - 1)
            pygame.draw.circle(screen, ORANGE, (int(self.x), int(self.y)), self.radius - 3)
            # Llamas
            for offset in [-2, 0, 2]:
                flame_points = [
                    (self.x + offset, self.y - self.radius),
                    (self.x + offset - 2, self.y - self.radius - 3),
                    (self.x + offset + 2, self.y - self.radius - 3)
                ]
                pygame.draw.polygon(screen, YELLOW, flame_points)
    
    def update(self):
        """Actualiza la posición del proyectil"""
        # Si es un proyectil del jugador con objetivo, dirigirlo hacia el enemigo
        if self.is_player_shot and self.target_enemy:
            # Verificar si el enemigo objetivo sigue vivo
            if hasattr(self.target_enemy, 'hp') and self.target_enemy.hp > 0:
                # Calcular dirección hacia el enemigo
                target_x = self.target_enemy.x + self.target_enemy.width // 2
                target_y = self.target_enemy.y + self.target_enemy.height // 2
                
                dx = target_x - self.x
                dy = target_y - self.y
                distance = math.sqrt(dx * dx + dy * dy)
                
                if distance > 0:
                    # Normalizar y aplicar velocidad (velocidad constante)
                    speed = abs(self.speed)
                    self.vx = (dx / distance) * speed
                    self.vy = (dy / distance) * speed
                else:
                    # Si está muy cerca, mantener dirección actual
                    if self.vx == 0 and self.vy == 0:
                        self.vy = -abs(self.speed)
            
            # Actualizar posición
            self.x += self.vx
            self.y += self.vy
            # Actualizar posición
            self.x += self.vx
            self.y += self.vy
        
        # Lógica de movimiento para proyectiles enemigos (lineal) o sin objetivo
        else:
            # Movimiento basado en velocidad constante (calculada al inicio)
            self.x += self.vx
            self.y += self.vy
        
        # Agregar partículas de estela
        if len(self.particles) < self.trail_length:
            self.particles.append((self.x, self.y, self.trail_length))
        
        # Actualizar partículas (mantener las últimas N)
        self.particles = [(px, py, life - 1) for px, py, life in self.particles if life > 0]
    
    def is_off_screen(self):
        """Verifica si el proyectil está fuera de la pantalla"""
        return self.y < -10 or self.y > SCREEN_HEIGHT + 10
    
    def get_rect(self):
        """Retorna el rectángulo de colisión"""
        return pygame.Rect(self.x - self.radius, self.y - self.radius, 
                          self.radius * 2, self.radius * 2)
