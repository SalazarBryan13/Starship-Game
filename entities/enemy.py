# -*- coding: utf-8 -*-
"""
Clase Enemy - Naves enemigas con diseños por nivel
"""

import pygame

from config import (
    BLACK, WHITE, RED, DARK_RED, GREEN, YELLOW, BLUE, DARK_BLUE,
    CYAN, PURPLE, DARK_PURPLE, PINK, ORANGE, SILVER, SCREEN_WIDTH
)


class Enemy:
    """Clase para el enemigo con diferentes diseños según el nivel"""
    
    # === OPTIMIZACIÓN: Cache de fuente a nivel de clase ===
    _hp_font = None
    
    @classmethod
    def _get_hp_font(cls):
        """Obtiene la fuente cacheada para HP (crea solo una vez)"""
        if cls._hp_font is None:
            cls._hp_font = pygame.font.Font(None, 16)
        return cls._hp_font
    
    def __init__(self, x, y, hp, speed, level=1):
        self.x = x
        self.y = y
        self.width = 60
        self.height = 40
        self.hp = hp
        self.max_hp = hp
        self.speed = speed
        self.shoot_cooldown = 0
        self.direction = 1  # 1 derecha, -1 izquierda
        self.move_counter = 0
        self.level = level
    
    def draw(self, screen):
        """Dibuja el enemigo con diseño diferente según el nivel"""
        if self.level == 1:
            self._draw_level1(screen)
        elif self.level == 2:
            self._draw_level2(screen)
        else:  # Nivel 3
            self._draw_level3(screen)
    
    def _draw_level1(self, screen):
        """Dibuja enemigo del nivel 1 - Diseño básico azul/cyan"""
        center_x = self.x + self.width // 2
        
        # Barra de vida (común para todos los niveles)
        bar_width = self.width + 10
        bar_height = 8
        bar_x = self.x - 5
        bar_y = self.y - 18
        hp_percentage = self.hp / self.max_hp
        hp_width = int(bar_width * hp_percentage)
        
        pygame.draw.rect(screen, BLACK, (bar_x - 1, bar_y - 1, bar_width + 2, bar_height + 2))
        pygame.draw.rect(screen, DARK_BLUE, (bar_x, bar_y, bar_width, bar_height))
        
        if hp_width > 0:
            if hp_percentage > 0.6:
                hp_color = GREEN
            elif hp_percentage > 0.3:
                hp_color = YELLOW
            else:
                hp_color = RED
            pygame.draw.rect(screen, hp_color, (bar_x, bar_y, hp_width, bar_height))
            if hp_width > 2:
                pygame.draw.rect(screen, WHITE, (bar_x, bar_y, hp_width, 3))
        
        pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 2)
        
        hp_text = self._get_hp_font().render(f"{self.hp}/{self.max_hp}", True, WHITE)
        hp_text_rect = hp_text.get_rect(center=(center_x, self.y - 28))
        screen.blit(hp_text, hp_text_rect)
        
        # Diseño Nivel 1: Nave básica azul/cyan
        # Alas redondeadas
        pygame.draw.ellipse(screen, DARK_BLUE, (self.x - 8, self.y - 5, 20, 30))
        pygame.draw.ellipse(screen, DARK_BLUE, (self.x + self.width - 12, self.y - 5, 20, 30))
        
        # Cuerpo principal redondeado
        pygame.draw.ellipse(screen, BLUE, (self.x, self.y, self.width, self.height))
        pygame.draw.ellipse(screen, CYAN, (self.x + 5, self.y + 5, self.width - 10, self.height - 10))
        pygame.draw.ellipse(screen, BLUE, (self.x, self.y, self.width, self.height), 2)
        
        # Ventana central azul brillante
        window_center = (center_x, self.y + self.height // 2)
        pygame.draw.circle(screen, DARK_BLUE, window_center, 10)
        pygame.draw.circle(screen, CYAN, window_center, 9)
        pygame.draw.circle(screen, WHITE, (center_x - 2, self.y + self.height // 2 - 2), 4)
        pygame.draw.circle(screen, BLUE, window_center, 9, 2)
        
        # Cañones simples
        pygame.draw.rect(screen, SILVER, (self.x + 10, self.y + self.height, 4, 6))
        pygame.draw.rect(screen, SILVER, (self.x + self.width - 14, self.y + self.height, 4, 6))
    
    def _draw_level2(self, screen):
        """Dibuja enemigo del nivel 2 - Diseño intermedio púrpura/rosa"""
        center_x = self.x + self.width // 2
        
        # Barra de vida
        bar_width = self.width + 10
        bar_height = 8
        bar_x = self.x - 5
        bar_y = self.y - 18
        hp_percentage = self.hp / self.max_hp
        hp_width = int(bar_width * hp_percentage)
        
        pygame.draw.rect(screen, BLACK, (bar_x - 1, bar_y - 1, bar_width + 2, bar_height + 2))
        pygame.draw.rect(screen, DARK_PURPLE, (bar_x, bar_y, bar_width, bar_height))
        
        if hp_width > 0:
            if hp_percentage > 0.6:
                hp_color = GREEN
            elif hp_percentage > 0.3:
                hp_color = YELLOW
            else:
                hp_color = RED
            pygame.draw.rect(screen, hp_color, (bar_x, bar_y, hp_width, bar_height))
            if hp_width > 2:
                pygame.draw.rect(screen, WHITE, (bar_x, bar_y, hp_width, 3))
        
        pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 2)
        
        hp_text = self._get_hp_font().render(f"{self.hp}/{self.max_hp}", True, WHITE)
        hp_text_rect = hp_text.get_rect(center=(center_x, self.y - 28))
        screen.blit(hp_text, hp_text_rect)
        
        # Diseño Nivel 2: Nave angular púrpura
        # Alas superiores puntiagudas
        top_wing_left = [
            (self.x - 5, self.y + 8),
            (self.x - 20, self.y - 18),
            (self.x + 8, self.y)
        ]
        top_wing_right = [
            (self.x + self.width + 5, self.y + 8),
            (self.x + self.width + 20, self.y - 18),
            (self.x + self.width - 8, self.y)
        ]
        pygame.draw.polygon(screen, DARK_PURPLE, top_wing_left)
        pygame.draw.polygon(screen, DARK_PURPLE, top_wing_right)
        pygame.draw.polygon(screen, PURPLE, top_wing_left, 2)
        pygame.draw.polygon(screen, PURPLE, top_wing_right, 2)
        
        # Cuerpo hexagonal
        pygame.draw.polygon(screen, DARK_PURPLE, [
            (center_x, self.y),
            (self.x, self.y + self.height // 3),
            (self.x, self.y + 2 * self.height // 3),
            (center_x, self.y + self.height),
            (self.x + self.width, self.y + 2 * self.height // 3),
            (self.x + self.width, self.y + self.height // 3)
        ])
        pygame.draw.polygon(screen, PURPLE, [
            (center_x, self.y + 5),
            (self.x + 8, self.y + self.height // 3 + 5),
            (self.x + 8, self.y + 2 * self.height // 3 - 5),
            (center_x, self.y + self.height - 5),
            (self.x + self.width - 8, self.y + 2 * self.height // 3 - 5),
            (self.x + self.width - 8, self.y + self.height // 3 + 5)
        ])
        pygame.draw.polygon(screen, PINK, [
            (center_x, self.y),
            (self.x, self.y + self.height // 3),
            (self.x, self.y + 2 * self.height // 3),
            (center_x, self.y + self.height),
            (self.x + self.width, self.y + 2 * self.height // 3),
            (self.x + self.width, self.y + self.height // 3)
        ], 3)
        
        # Ventana central con cristal púrpura
        window_center = (center_x, self.y + self.height // 2)
        pygame.draw.circle(screen, DARK_PURPLE, window_center, 12)
        pygame.draw.circle(screen, PURPLE, window_center, 11)
        pygame.draw.circle(screen, PINK, (center_x + 2, self.y + self.height // 2 - 2), 5)
        pygame.draw.circle(screen, WHITE, window_center, 11, 2)
        
        # Detalles decorativos - cristales
        pygame.draw.polygon(screen, PINK, [
            (self.x + 12, self.y + 12), (self.x + 18, self.y + 12),
            (self.x + 15, self.y + 18)
        ])
        pygame.draw.polygon(screen, PINK, [
            (self.x + self.width - 12, self.y + 12), (self.x + self.width - 18, self.y + 12),
            (self.x + self.width - 15, self.y + 18)
        ])
        
        # Cañones dobles
        pygame.draw.rect(screen, SILVER, (self.x + 6, self.y + self.height, 5, 10))
        pygame.draw.rect(screen, SILVER, (self.x + 11, self.y + self.height, 5, 10))
        pygame.draw.rect(screen, SILVER, (self.x + self.width - 16, self.y + self.height, 5, 10))
        pygame.draw.rect(screen, SILVER, (self.x + self.width - 11, self.y + self.height, 5, 10))
    
    def _draw_level3(self, screen):
        """Dibuja enemigo del nivel 3 - Diseño avanzado rojo/naranja amenazante"""
        center_x = self.x + self.width // 2
        
        # Barra de vida
        bar_width = self.width + 10
        bar_height = 8
        bar_x = self.x - 5
        bar_y = self.y - 18
        hp_percentage = self.hp / self.max_hp
        hp_width = int(bar_width * hp_percentage)
        
        pygame.draw.rect(screen, BLACK, (bar_x - 1, bar_y - 1, bar_width + 2, bar_height + 2))
        pygame.draw.rect(screen, DARK_RED, (bar_x, bar_y, bar_width, bar_height))
        
        if hp_width > 0:
            if hp_percentage > 0.6:
                hp_color = GREEN
            elif hp_percentage > 0.3:
                hp_color = YELLOW
            else:
                hp_color = RED
            pygame.draw.rect(screen, hp_color, (bar_x, bar_y, hp_width, bar_height))
            if hp_width > 2:
                pygame.draw.rect(screen, WHITE, (bar_x, bar_y, hp_width, 3))
        
        pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 2)
        
        hp_text = self._get_hp_font().render(f"{self.hp}/{self.max_hp}", True, WHITE)
        hp_text_rect = hp_text.get_rect(center=(center_x, self.y - 28))
        screen.blit(hp_text, hp_text_rect)
        
        # Diseño Nivel 3: Nave avanzada roja agresiva
        # Alas grandes y amenazantes
        top_wing_left = [
            (self.x - 8, self.y + 5),
            (self.x - 25, self.y - 25),
            (self.x + 10, self.y - 5)
        ]
        top_wing_right = [
            (self.x + self.width + 8, self.y + 5),
            (self.x + self.width + 25, self.y - 25),
            (self.x + self.width - 10, self.y - 5)
        ]
        pygame.draw.polygon(screen, DARK_RED, top_wing_left)
        pygame.draw.polygon(screen, DARK_RED, top_wing_right)
        pygame.draw.polygon(screen, RED, top_wing_left, 3)
        pygame.draw.polygon(screen, RED, top_wing_right, 3)
        
        # Alas inferiores
        bottom_wing_left = [
            (self.x - 5, self.y + self.height - 5),
            (self.x - 15, self.y + self.height + 10),
            (self.x + 8, self.y + self.height)
        ]
        bottom_wing_right = [
            (self.x + self.width + 5, self.y + self.height - 5),
            (self.x + self.width + 15, self.y + self.height + 10),
            (self.x + self.width - 8, self.y + self.height)
        ]
        pygame.draw.polygon(screen, DARK_RED, bottom_wing_left)
        pygame.draw.polygon(screen, DARK_RED, bottom_wing_right)
        pygame.draw.polygon(screen, ORANGE, bottom_wing_left, 2)
        pygame.draw.polygon(screen, ORANGE, bottom_wing_right, 2)
        
        # Cuerpo principal angular y agresivo
        pygame.draw.polygon(screen, DARK_RED, [
            (center_x, self.y),
            (self.x - 3, self.y + self.height // 4),
            (self.x, self.y + self.height // 2),
            (self.x - 3, self.y + 3 * self.height // 4),
            (center_x, self.y + self.height),
            (self.x + self.width + 3, self.y + 3 * self.height // 4),
            (self.x + self.width, self.y + self.height // 2),
            (self.x + self.width + 3, self.y + self.height // 4)
        ])
        pygame.draw.polygon(screen, RED, [
            (center_x, self.y + 3),
            (self.x + 2, self.y + self.height // 4 + 3),
            (self.x + 5, self.y + self.height // 2),
            (self.x + 2, self.y + 3 * self.height // 4 - 3),
            (center_x, self.y + self.height - 3),
            (self.x + self.width - 2, self.y + 3 * self.height // 4 - 3),
            (self.x + self.width - 5, self.y + self.height // 2),
            (self.x + self.width - 2, self.y + self.height // 4 + 3)
        ])
        pygame.draw.polygon(screen, ORANGE, [
            (center_x, self.y),
            (self.x - 3, self.y + self.height // 4),
            (self.x, self.y + self.height // 2),
            (self.x - 3, self.y + 3 * self.height // 4),
            (center_x, self.y + self.height),
            (self.x + self.width + 3, self.y + 3 * self.height // 4),
            (self.x + self.width, self.y + self.height // 2),
            (self.x + self.width + 3, self.y + self.height // 4)
        ], 3)
        
        # Ventana central amenazante roja
        window_center = (center_x, self.y + self.height // 2)
        pygame.draw.circle(screen, DARK_RED, window_center, 13)
        pygame.draw.circle(screen, RED, window_center, 12)
        pygame.draw.circle(screen, ORANGE, window_center, 10)
        pygame.draw.circle(screen, YELLOW, (center_x - 1, self.y + self.height // 2 - 1), 5)
        pygame.draw.circle(screen, RED, window_center, 12, 3)
        
        # Detalles agresivos - púas
        pygame.draw.polygon(screen, ORANGE, [
            (self.x + 8, self.y + 10), (self.x + 14, self.y + 10),
            (self.x + 11, self.y + 16)
        ])
        pygame.draw.polygon(screen, ORANGE, [
            (self.x + self.width - 8, self.y + 10), (self.x + self.width - 14, self.y + 10),
            (self.x + self.width - 11, self.y + 16)
        ])
        pygame.draw.polygon(screen, ORANGE, [
            (self.x + 8, self.y + self.height - 10), (self.x + 14, self.y + self.height - 10),
            (self.x + 11, self.y + self.height - 16)
        ])
        pygame.draw.polygon(screen, ORANGE, [
            (self.x + self.width - 8, self.y + self.height - 10),
            (self.x + self.width - 14, self.y + self.height - 10),
            (self.x + self.width - 11, self.y + self.height - 16)
        ])
        
        # Cañones triples grandes
        pygame.draw.rect(screen, SILVER, (self.x + 4, self.y + self.height, 4, 12))
        pygame.draw.rect(screen, SILVER, (self.x + 9, self.y + self.height, 4, 12))
        pygame.draw.rect(screen, SILVER, (self.x + 14, self.y + self.height, 4, 12))
        pygame.draw.rect(screen, SILVER, (self.x + self.width - 18, self.y + self.height, 4, 12))
        pygame.draw.rect(screen, SILVER, (self.x + self.width - 13, self.y + self.height, 4, 12))
        pygame.draw.rect(screen, SILVER, (self.x + self.width - 8, self.y + self.height, 4, 12))
    
    def move(self):
        """Mueve el enemigo de lado a lado"""
        self.move_counter += 1
        if self.move_counter >= 30:
            self.direction *= -1
            self.move_counter = 0
        self.x += self.speed * self.direction
        
        # Limitar movimiento dentro de la pantalla
        if self.x <= 0:
            self.x = 0
            self.direction = 1
        elif self.x + self.width >= SCREEN_WIDTH:
            self.x = SCREEN_WIDTH - self.width
            self.direction = -1
    
    def shoot(self):
        """Crea un disparo del enemigo"""
        from entities.projectile import Projectile
        if self.shoot_cooldown <= 0:
            self.shoot_cooldown = 60
            return Projectile(self.x + self.width // 2, self.y + self.height, 8, RED, False)
        return None
    
    def take_damage(self, amount=1):
        """El enemigo recibe daño"""
        self.hp -= amount
    
    def update(self):
        """Actualiza el estado del enemigo"""
        self.move()
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
    
    def is_dead(self):
        """Verifica si el enemigo está muerto"""
        return self.hp <= 0
