# -*- coding: utf-8 -*-
"""
Clase Slider - Control deslizante para volumen
"""

import pygame

from config import WHITE


class Slider:
    """Clase para sliders arrastrables de volumen"""
    
    def __init__(self, x, y, width, height, min_value=0.0, max_value=1.0, initial_value=0.7, color=(100, 150, 255)):
        self.rect = pygame.Rect(x, y, width, height)
        self.min_value = min_value
        self.max_value = max_value
        self.value = initial_value
        self.color = color
        self.is_dragging = False
        self.knob_radius = 12
        
    def update(self, mouse_pos, mouse_down, mouse_clicked):
        """Actualiza el slider según el mouse"""
        # Área clickeable más grande (incluye la barra completa)
        clickable_rect = pygame.Rect(
            self.rect.x - 5,
            self.rect.centery - self.knob_radius - 5,
            self.rect.width + 10,
            self.knob_radius * 2 + 10
        )
        
        knob_x = self.rect.x + int((self.value - self.min_value) / (self.max_value - self.min_value) * self.rect.width)
        knob_rect = pygame.Rect(knob_x - self.knob_radius, self.rect.centery - self.knob_radius,
                                self.knob_radius * 2, self.knob_radius * 2)
        
        # Si se hace click en el área clickeable (knob o barra)
        if mouse_clicked and clickable_rect.collidepoint(mouse_pos):
            self.is_dragging = True
            # Actualizar valor inmediatamente al hacer click
            relative_x = mouse_pos[0] - self.rect.x
            relative_x = max(0, min(self.rect.width, relative_x))
            self.value = self.min_value + (relative_x / self.rect.width) * (self.max_value - self.min_value)
        
        # Si se está arrastrando, actualizar valor continuamente
        if mouse_down and self.is_dragging:
            # Calcular nuevo valor basado en posición del mouse
            relative_x = mouse_pos[0] - self.rect.x
            relative_x = max(0, min(self.rect.width, relative_x))
            self.value = self.min_value + (relative_x / self.rect.width) * (self.max_value - self.min_value)
        
        if not mouse_down:
            self.is_dragging = False
    
    def draw(self, screen):
        """Dibuja el slider"""
        # Fondo de la barra con gradiente
        for i in range(self.rect.width):
            progress = i / self.rect.width
            r = int(self.color[0] * (1 - progress * 0.5))
            g = int(self.color[1] * (1 - progress * 0.5))
            b = int(self.color[2] * (1 - progress * 0.5))
            pygame.draw.line(screen, (r, g, b), 
                           (self.rect.x + i, self.rect.y),
                           (self.rect.x + i, self.rect.y + self.rect.height))
        
        # Barra de progreso
        progress_width = int((self.value - self.min_value) / (self.max_value - self.min_value) * self.rect.width)
        if progress_width > 0:
            # Gradiente en la barra de progreso
            for i in range(progress_width):
                progress = i / progress_width if progress_width > 0 else 0
                r = int(self.color[0] * (0.5 + progress * 0.5))
                g = int(self.color[1] * (0.5 + progress * 0.5))
                b = int(self.color[2] * (0.5 + progress * 0.5))
                pygame.draw.line(
                    screen,
                    (r, g, b),
                    (self.rect.x + i, self.rect.y),
                    (self.rect.x + i, self.rect.y + self.rect.height),
                )
        
        # Borde suave
        pygame.draw.rect(screen, (255, 255, 255, 100), self.rect, 2)
        
        # Knob (bolita) con efecto 3D
        knob_x = self.rect.x + int((self.value - self.min_value) / (self.max_value - self.min_value) * self.rect.width)
        knob_y = self.rect.centery
        
        # Sombra del knob
        pygame.draw.circle(screen, (0, 0, 0, 100), (knob_x, knob_y + 2), self.knob_radius)
        
        # Knob principal con gradiente
        for i in range(self.knob_radius * 2):
            progress = i / (self.knob_radius * 2)
            color_intensity = int(255 * (1 - progress * 0.3))
            color = (min(255, self.color[0] + color_intensity // 3),
                    min(255, self.color[1] + color_intensity // 3),
                    min(255, self.color[2] + color_intensity // 3))
            radius = self.knob_radius - int(progress * self.knob_radius * 0.3)
            if radius > 0:
                pygame.draw.circle(screen, color, (knob_x, knob_y), radius)
        
        # Brillo en el knob
        pygame.draw.circle(screen, (255, 255, 255, 150), (knob_x - 3, knob_y - 3), 4)
        
        # Borde del knob
        pygame.draw.circle(screen, WHITE, (knob_x, knob_y), self.knob_radius, 2)
