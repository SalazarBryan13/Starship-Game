# -*- coding: utf-8 -*-
"""
Clase Button - Botones con estilo moderno espacial
"""

import pygame
import math

from config import WHITE


class Button:
    """Clase para botones con estilo moderno y elegante"""
    
    def __init__(self, x, y, width, height, text, font, color=(100, 150, 255), hover_color=(150, 200, 255), 
                 text_color=WHITE, icon=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.icon = icon  # 'play', 'infinity', 'controls', 'settings', 'exit', 'back', 'resume', 'menu'
        self.is_hovered = False
        self.animation_progress = 0.0
        
    def update(self, mouse_pos):
        """Actualiza el estado del botón (hover)"""
        was_hovered = self.is_hovered
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        
        if self.is_hovered and not was_hovered:
            self.animation_progress = 0.0
        elif self.is_hovered:
            self.animation_progress = min(1.0, self.animation_progress + 0.1)
        else:
            self.animation_progress = max(0.0, self.animation_progress - 0.1)
    
    def _draw_icon(self, screen, x, y, size=30):
        """Dibuja el icono correspondiente con estilo cian espacial"""
        # Color cian brillante para iconos
        color = (0, 220, 255) if self.is_hovered else (0, 180, 220)
        center_y = y + size // 2
        center_x = x + size // 2
        
        if self.icon == 'play' or self.icon == 'resume':
            # Triángulo apuntando a la derecha
            points = [
                (x + 5, y),
                (x + 5, y + size),
                (x + size, y + size // 2)
            ]
            pygame.draw.polygon(screen, color, points)
            
        elif self.icon == 'infinity':
            # Símbolo de infinito (dos círculos)
            radius = size // 3
            pygame.draw.circle(screen, color, (x + radius, center_y), radius, 3)
            pygame.draw.circle(screen, color, (x + size - radius, center_y), radius, 3)
            
        elif self.icon == 'controls':
            # Gamepad simple con estilo neón
            rect = pygame.Rect(x, y + 5, size, size - 10)
            pygame.draw.rect(screen, color, rect, width=2, border_radius=5)
            # Botones internos
            pygame.draw.circle(screen, color, (x + 8, center_y), 3)
            pygame.draw.circle(screen, color, (x + size - 8, center_y - 3), 2)
            pygame.draw.circle(screen, color, (x + size - 12, center_y + 3), 2)
            
        elif self.icon == 'settings':
            # Engranaje simplificado
            pygame.draw.circle(screen, color, (center_x, center_y), size // 2 - 2, 2)
            pygame.draw.circle(screen, color, (center_x, center_y), size // 4)
            # Dientes (4 líneas cruzadas)
            for i in range(4):
                angle = i * 45
                rad = math.radians(angle)
                start_x = center_x + math.cos(rad) * (size//2 - 5)
                start_y = center_y + math.sin(rad) * (size//2 - 5)
                end_x = center_x + math.cos(rad) * (size//2 + 2)
                end_y = center_y + math.sin(rad) * (size//2 + 2)
                pygame.draw.line(screen, color, (start_x, start_y), (end_x, end_y), 3)

        elif self.icon == 'exit':
            # Botón de encendido/salir
            pygame.draw.circle(screen, color, (center_x, center_y), size // 2 - 2, 2)
            # Línea vertical
            pygame.draw.line(screen, (20, 40, 60), (center_x, y), (center_x, y + 8), 6)
            pygame.draw.line(screen, color, (center_x, y), (center_x, center_y), 2)
            
        elif self.icon == 'back' or self.icon == 'menu':
            # Flecha izquierda
            points = [
                (x + size - 5, y + 5),
                (x + size - 5, y + size - 5),
                (x + 5, y + size // 2)
            ]
            pygame.draw.polygon(screen, color, points)

    def draw(self, screen):
        """Dibuja el botón con estilo moderno espacial - glassmorphism"""
        # Color base: cian espacial con transparencia
        base_color = (20, 40, 60)  # Azul oscuro espacial
        border_color = (0, 200, 255) if self.is_hovered else (0, 150, 200)  # Cian brillante
        glow_color = (0, 255, 255, 100) if self.is_hovered else (0, 200, 255, 50)
        
        # Calcular animación
        hover_mult = 1.0 + 0.1 * self.animation_progress
        
        # === GLOW EXTERNO (efecto neón) ===
        if self.is_hovered:
            glow_surface = pygame.Surface((self.rect.width + 20, self.rect.height + 20), pygame.SRCALPHA)
            for i in range(3):
                glow_alpha = int(40 - i * 12)
                pygame.draw.rect(glow_surface, (*border_color, glow_alpha),
                               (i * 2, i * 2, self.rect.width + 20 - i * 4, self.rect.height + 20 - i * 4),
                               border_radius=18 + i * 2)
            screen.blit(glow_surface, (self.rect.x - 10, self.rect.y - 10))
        
        # === FONDO DEL BOTÓN ===
        button_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        
        # Fondo semi-transparente con glassmorphism
        bg_alpha = 180 if self.is_hovered else 150
        pygame.draw.rect(button_surface, (*base_color, bg_alpha),
                        (0, 0, self.rect.width, self.rect.height),
                        border_radius=15)
        
        # Borde neón brillante
        border_width = 3 if self.is_hovered else 2
        pygame.draw.rect(button_surface, border_color,
                        (0, 0, self.rect.width, self.rect.height),
                        width=border_width, border_radius=15)
        
        # Línea de brillo superior (efecto 3D sutil)
        highlight_surface = pygame.Surface((self.rect.width - 20, 2), pygame.SRCALPHA)
        highlight_surface.fill((255, 255, 255, 60))
        button_surface.blit(highlight_surface, (10, 5))
        
        # Efecto hover: brillo interno
        if self.is_hovered:
            inner_glow = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            pygame.draw.rect(inner_glow, (0, 255, 255, 30),
                           (0, 0, self.rect.width, self.rect.height),
                           border_radius=15)
            button_surface.blit(inner_glow, (0, 0))
        
        screen.blit(button_surface, self.rect)
        
        # === CONTENIDO: ICONO + TEXTO ===
        text_surface = self.font.render(self.text, True, WHITE)
        text_w = text_surface.get_width()
        text_h = text_surface.get_height()
        
        icon_size = 30
        spacing = 15
        
        if self.icon:
            total_width = text_w + icon_size + spacing
            start_x = self.rect.centerx - total_width // 2
            
            # Dibujar icono con color cian
            self._draw_icon(screen, start_x, self.rect.centery - icon_size // 2, icon_size)
            
            text_x = start_x + icon_size + spacing
        else:
            text_x = self.rect.centerx - text_w // 2
            
        text_y = self.rect.centery - text_h // 2
        
        # Sombra sutil del texto
        text_shadow = self.font.render(self.text, True, (0, 0, 0))
        screen.blit(text_shadow, (text_x + 1, text_y + 1))
        # Texto principal blanco brillante
        screen.blit(text_surface, (text_x, text_y))
    
    def is_clicked(self, mouse_pos, mouse_clicked):
        """Verifica si el botón fue clickeado"""
        return self.rect.collidepoint(mouse_pos) and mouse_clicked
