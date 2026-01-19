# -*- coding: utf-8 -*-
"""
MascotaAnimada - Robot espacial amigable con sistema de logros
Robot más grande e interactivo con recompensas visuales dinámicas
"""

import pygame
import random
import math

from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, CYAN, GREEN, YELLOW, WHITE, PINK, GOLD, PURPLE
)


class CelebrationParticle:
    """Partícula de celebración (estrella, confeti)"""
    
    def __init__(self, x, y, intensity=1.0):
        self.x = x
        self.y = y
        self.vx = random.uniform(-4, 4) * intensity
        self.vy = random.uniform(-8, -3) * intensity
        self.gravity = 0.12
        self.lifetime = random.randint(50, 100)
        self.max_lifetime = self.lifetime
        self.size = random.randint(4, 12)
        self.color = random.choice([
            CYAN, GREEN, YELLOW, PINK, GOLD, WHITE, PURPLE,
            (255, 100, 100), (100, 255, 100), (100, 100, 255),
            (255, 200, 50), (50, 255, 200)
        ])
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-15, 15)
        self.type = random.choice(['star', 'circle', 'square', 'diamond'])
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.lifetime -= 1
        self.rotation += self.rotation_speed
    
    def draw(self, screen):
        if self.lifetime <= 0:
            return
        
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        size = int(self.size * (0.5 + 0.5 * self.lifetime / self.max_lifetime))
        
        if size < 1:
            return
        
        if self.type == 'star':
            self._draw_star(screen, size)
        elif self.type == 'diamond':
            self._draw_diamond(screen, size)
        elif self.type == 'circle':
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), size)
        else:
            surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.rect(surf, (*self.color, alpha), (size // 2, size // 2, size, size))
            rotated = pygame.transform.rotate(surf, self.rotation)
            rect = rotated.get_rect(center=(int(self.x), int(self.y)))
            screen.blit(rotated, rect)
    
    def _draw_star(self, screen, size):
        points = []
        for i in range(10):
            angle = math.radians(self.rotation + i * 36)
            r = size if i % 2 == 0 else size // 2
            px = self.x + math.cos(angle) * r
            py = self.y + math.sin(angle) * r
            points.append((px, py))
        if len(points) >= 3:
            pygame.draw.polygon(screen, self.color, points)
    
    def _draw_diamond(self, screen, size):
        points = [
            (self.x, self.y - size),
            (self.x + size, self.y),
            (self.x, self.y + size),
            (self.x - size, self.y)
        ]
        pygame.draw.polygon(screen, self.color, points)
    
    def is_dead(self):
        return self.lifetime <= 0


class AchievementPopup:
    """Logro visual que aparece en pantalla"""
    
    def __init__(self, text, bonus_points, x, y):
        self.text = text
        self.bonus_points = bonus_points
        self.x = x
        self.y = y
        self.start_y = y
        self.lifetime = 180  # 3 segundos
        self.max_lifetime = self.lifetime
        self.scale = 0.0
        self.target_scale = 1.0
        
        # Fuentes
        try:
            self.font = pygame.font.Font(None, 36)
            self.font_bonus = pygame.font.Font(None, 28)
        except:
            self.font = pygame.font.SysFont('arial', 28)
            self.font_bonus = pygame.font.SysFont('arial', 22)
    
    def update(self):
        self.lifetime -= 1
        
        # Animación de entrada (escala)
        if self.lifetime > self.max_lifetime - 20:
            progress = (self.max_lifetime - self.lifetime) / 20
            self.scale = self.target_scale * (1 - (1 - progress) ** 3)
        elif self.lifetime < 30:
            # Animación de salida
            self.scale = self.lifetime / 30
            self.y -= 2  # Subir mientras desaparece
        else:
            self.scale = 1.0
            # Ligera flotación
            self.y = self.start_y + math.sin(pygame.time.get_ticks() * 0.01) * 3
    
    def draw(self, screen):
        if self.scale <= 0:
            return
        
        # Fondo del logro
        width = 280
        height = 80
        
        popup_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Gradiente de fondo
        for i in range(height):
            progress = i / height
            r = int(60 * (1 - progress * 0.3))
            g = int(20 * (1 - progress * 0.3))
            b = int(100 * (1 - progress * 0.3))
            alpha = int(220 * self.scale)
            pygame.draw.line(popup_surface, (r, g, b, alpha), (0, i), (width, i))
        
        # Borde dorado brillante
        pygame.draw.rect(popup_surface, (*GOLD, int(255 * self.scale)), 
                        (0, 0, width, height), 3, border_radius=15)
        
        # Icono de estrella
        star_x, star_y = 35, height // 2
        for i in range(5):
            angle = math.radians(-90 + i * 72)
            inner_angle = math.radians(-90 + i * 72 + 36)
            outer_r = 18
            inner_r = 8
            if i == 0:
                points = []
            px = star_x + math.cos(angle) * outer_r
            py = star_y + math.sin(angle) * outer_r
            points.append((px, py))
            px = star_x + math.cos(inner_angle) * inner_r
            py = star_y + math.sin(inner_angle) * inner_r
            points.append((px, py))
        pygame.draw.polygon(popup_surface, GOLD, points)
        pygame.draw.polygon(popup_surface, WHITE, points, 2)
        
        # Texto del logro
        text_surface = self.font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(midleft=(60, height // 2 - 10))
        popup_surface.blit(text_surface, text_rect)
        
        # Bonus de puntos
        bonus_text = f"+{self.bonus_points} PUNTOS"
        bonus_surface = self.font_bonus.render(bonus_text, True, GOLD)
        bonus_rect = bonus_surface.get_rect(midleft=(60, height // 2 + 15))
        popup_surface.blit(bonus_surface, bonus_rect)
        
        # Escalar
        if self.scale != 1.0:
            new_width = int(width * self.scale)
            new_height = int(height * self.scale)
            if new_width > 0 and new_height > 0:
                popup_surface = pygame.transform.scale(popup_surface, (new_width, new_height))
        
        # Posicionar en pantalla
        rect = popup_surface.get_rect(center=(self.x, self.y))
        screen.blit(popup_surface, rect)
    
    def is_dead(self):
        return self.lifetime <= 0


class MascotaAnimada:
    """
    Robot espacial animado GRANDE con sistema de logros y recompensas.
    Cada 2 respuestas correctas consecutivas da un logro visual + bonus.
    """
    
    MENSAJES_CELEBRACION = [
        "¡GENIAL!", "¡EXCELENTE!", "¡SIGUE ASÍ!", "¡INCREÍBLE!",
        "¡MATEMÁTICO!", "¡BRILLANTE!", "¡FANTÁSTICO!", "¡PERFECTO!",
        "¡ASOMBROSO!", "¡BIEN HECHO!", "¡CRACK!", "¡LEYENDA!"
    ]
    
    LOGROS = [
        ("¡RACHA x2!", 25),
        ("¡IMPARABLE x4!", 50),
        ("¡GENIO x6!", 100),
        ("¡MAESTRO x8!", 150),
        ("¡LEGENDARIO x10!", 250),
    ]
    
    STATE_IDLE = 'idle'
    STATE_CELEBRATE = 'celebrate'
    STATE_MEGA_CELEBRATE = 'mega_celebrate'
    
    def __init__(self, x=None, y=None):
        # Posición (esquina inferior derecha) - ROBOT MÁS GRANDE
        self.x = x if x is not None else SCREEN_WIDTH - 140
        self.y = y if y is not None else SCREEN_HEIGHT - 220
        
        # Dimensiones AUMENTADAS (1.5x más grande)
        self.width = 90
        self.height = 105
        
        # Sistema de racha
        self.streak = 0  # Respuestas correctas consecutivas
        self.total_bonus = 0  # Puntos bonus acumulados
        
        # Estado
        self.state = self.STATE_IDLE
        self.state_timer = 0
        
        # Animación
        self.float_offset = 0
        self.float_speed = 0.08
        self.blink_timer = 0
        self.is_blinking = False
        self.celebrate_jump = 0
        self.celebrate_arms = 0
        self.celebrate_duration = 90
        self.mega_celebrate_duration = 150
        
        # Efectos visuales
        self.particles = []
        self.achievements = []  # Lista de popups de logros
        self.glow_intensity = 0
        
        # Mensaje
        self.current_message = ""
        self.message_timer = 0
        self.message_index = 0
        
        # Colores (más vibrantes)
        self.body_color = (35, 70, 110)
        self.body_highlight = (60, 120, 170)
        self.eye_color = CYAN
        self.antenna_color = (220, 220, 220)
        self.accent_color = (0, 220, 255)
        
        # Fuentes más grandes
        try:
            self.font = pygame.font.Font(None, 32)
            self.font_small = pygame.font.Font(None, 24)
            self.font_streak = pygame.font.Font(None, 28)
        except:
            self.font = pygame.font.SysFont('arial', 26)
            self.font_small = pygame.font.SysFont('arial', 18)
            self.font_streak = pygame.font.SysFont('arial', 22)
    
    def celebrar(self):
        """Activa celebración y verifica logros"""
        self.streak += 1
        bonus = 0
        
        # Verificar si alcanzó un logro (cada 2 correctas)
        if self.streak >= 2 and self.streak % 2 == 0:
            # Determinar nivel de logro
            logro_index = min((self.streak // 2) - 1, len(self.LOGROS) - 1)
            logro_texto, logro_bonus = self.LOGROS[logro_index]
            bonus = logro_bonus
            self.total_bonus += bonus
            
            # Crear popup de logro en el centro de la pantalla
            achievement = AchievementPopup(
                logro_texto, logro_bonus,
                SCREEN_WIDTH // 2,
                SCREEN_HEIGHT // 3
            )
            self.achievements.append(achievement)
            
            # Mega celebración
            self.state = self.STATE_MEGA_CELEBRATE
            self.state_timer = self.mega_celebrate_duration
            self.glow_intensity = 1.0
            
            # Mega explosión de partículas
            for _ in range(40):
                particle = CelebrationParticle(
                    self.x + self.width // 2,
                    self.y + self.height // 3,
                    intensity=1.5
                )
                self.particles.append(particle)
            
            # Partículas desde el centro de la pantalla
            for _ in range(30):
                particle = CelebrationParticle(
                    SCREEN_WIDTH // 2 + random.randint(-50, 50),
                    SCREEN_HEIGHT // 3,
                    intensity=2.0
                )
                self.particles.append(particle)
        else:
            # Celebración normal
            self.state = self.STATE_CELEBRATE
            self.state_timer = self.celebrate_duration
            
            for _ in range(20):
                particle = CelebrationParticle(
                    self.x + self.width // 2,
                    self.y + self.height // 3
                )
                self.particles.append(particle)
        
        self.celebrate_jump = 0
        self.celebrate_arms = 0
        
        # Mensaje
        new_index = self.message_index
        while new_index == self.message_index and len(self.MENSAJES_CELEBRACION) > 1:
            new_index = random.randint(0, len(self.MENSAJES_CELEBRACION) - 1)
        self.message_index = new_index
        self.current_message = self.MENSAJES_CELEBRACION[self.message_index]
        self.message_timer = 120
        
        return bonus  # Retorna puntos bonus para añadir al score
    
    def reset_streak(self):
        """Reinicia la racha (cuando falla una respuesta)"""
        self.streak = 0
    
    def update(self):
        """Actualiza animaciones"""
        if self.state == self.STATE_IDLE:
            self._update_idle()
        elif self.state == self.STATE_CELEBRATE:
            self._update_celebrate()
        elif self.state == self.STATE_MEGA_CELEBRATE:
            self._update_mega_celebrate()
        
        # Glow decay
        if self.glow_intensity > 0:
            self.glow_intensity *= 0.98
        
        if self.message_timer > 0:
            self.message_timer -= 1
        
        # Actualizar partículas
        for particle in self.particles[:]:
            particle.update()
            if particle.is_dead():
                self.particles.remove(particle)
        
        # Actualizar logros
        for achievement in self.achievements[:]:
            achievement.update()
            if achievement.is_dead():
                self.achievements.remove(achievement)
    
    def _update_idle(self):
        self.float_offset = math.sin(pygame.time.get_ticks() * self.float_speed * 0.01) * 6
        
        self.blink_timer += 1
        if self.blink_timer > 180:
            if random.random() < 0.02:
                self.is_blinking = True
                self.blink_timer = 0
        
        if self.is_blinking:
            self.blink_timer += 1
            if self.blink_timer > 8:
                self.is_blinking = False
                self.blink_timer = 0
    
    def _update_celebrate(self):
        self.state_timer -= 1
        progress = 1 - (self.state_timer / self.celebrate_duration)
        
        self.celebrate_jump = -40 * math.sin(progress * math.pi)
        self.celebrate_arms = 35 * math.sin(progress * math.pi * 4)
        
        if random.random() < 0.35:
            particle = CelebrationParticle(
                self.x + self.width // 2 + random.randint(-30, 30),
                self.y + self.celebrate_jump + random.randint(-15, 15)
            )
            self.particles.append(particle)
        
        if self.state_timer <= 0:
            self.state = self.STATE_IDLE
            self.celebrate_jump = 0
            self.celebrate_arms = 0
    
    def _update_mega_celebrate(self):
        self.state_timer -= 1
        progress = 1 - (self.state_timer / self.mega_celebrate_duration)
        
        # Salto más alto y movimiento más intenso
        self.celebrate_jump = -60 * math.sin(progress * math.pi * 1.5)
        self.celebrate_arms = 45 * math.sin(progress * math.pi * 6)
        
        # Más partículas
        if random.random() < 0.5:
            particle = CelebrationParticle(
                self.x + self.width // 2 + random.randint(-40, 40),
                self.y + self.celebrate_jump + random.randint(-20, 20),
                intensity=1.3
            )
            self.particles.append(particle)
        
        if self.state_timer <= 0:
            self.state = self.STATE_IDLE
            self.celebrate_jump = 0
            self.celebrate_arms = 0
    
    def draw(self, screen):
        """Dibuja robot, partículas, logros y racha"""
        draw_x = self.x
        draw_y = self.y + self.float_offset + self.celebrate_jump
        
        # Partículas (detrás)
        for particle in self.particles:
            particle.draw(screen)
        
        # Glow del robot (cuando hay logro)
        if self.glow_intensity > 0.1:
            glow_size = int(self.width * 1.5)
            glow_surface = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
            glow_alpha = int(100 * self.glow_intensity)
            pygame.draw.circle(glow_surface, (*GOLD, glow_alpha),
                             (glow_size, glow_size), glow_size)
            screen.blit(glow_surface, 
                       (draw_x + self.width // 2 - glow_size,
                        draw_y + self.height // 2 - glow_size))
        
        # Sombra
        self._draw_shadow(screen, draw_x, draw_y)
        
        # Robot
        self._draw_robot(screen, draw_x, draw_y)
        
        # Indicador de racha
        if self.streak > 0:
            self._draw_streak_indicator(screen, draw_x, draw_y)
        
        # Mensaje
        if self.message_timer > 0:
            self._draw_message(screen, draw_x, draw_y)
        
        # Logros (encima de todo)
        for achievement in self.achievements:
            achievement.draw(screen)
    
    def _draw_shadow(self, screen, x, y):
        shadow_surface = pygame.Surface((self.width + 15, 20), pygame.SRCALPHA)
        shadow_scale = 1.0 - abs(self.celebrate_jump) / 100
        shadow_width = int((self.width + 15) * shadow_scale)
        shadow_height = int(12 * shadow_scale)
        pygame.draw.ellipse(shadow_surface, (0, 0, 0, 70), 
                           ((self.width + 15 - shadow_width) // 2, 5,
                            shadow_width, shadow_height))
        screen.blit(shadow_surface, (x - 7, self.y + self.height + 8))
    
    def _draw_robot(self, screen, x, y):
        """Robot MÁS GRANDE"""
        center_x = x + self.width // 2
        scale = 1.5  # Factor de escala
        
        # ANTENA
        antenna_x = center_x
        antenna_base_y = y + 8
        antenna_top_y = y - 22
        
        pygame.draw.line(screen, self.antenna_color, 
                        (antenna_x, antenna_base_y), 
                        (antenna_x, antenna_top_y), 4)
        
        glow_size = 9 + int(3 * math.sin(pygame.time.get_ticks() * 0.01))
        pygame.draw.circle(screen, self.accent_color, (antenna_x, antenna_top_y), glow_size)
        pygame.draw.circle(screen, WHITE, (antenna_x, antenna_top_y), glow_size - 3)
        
        # CABEZA
        head_rect = pygame.Rect(x + 8, y, self.width - 16, 52)
        pygame.draw.rect(screen, (20, 40, 60), 
                        (head_rect.x + 3, head_rect.y + 3, head_rect.width, head_rect.height),
                        border_radius=15)
        pygame.draw.rect(screen, self.body_color, head_rect, border_radius=15)
        pygame.draw.rect(screen, self.body_highlight, head_rect, 3, border_radius=15)
        
        # OJOS
        eye_y = y + 22
        left_eye_x = center_x - 18
        right_eye_x = center_x + 18
        eye_size = 12
        
        if not self.is_blinking:
            pygame.draw.circle(screen, (*self.eye_color, 100), (left_eye_x, eye_y), eye_size + 3)
            pygame.draw.circle(screen, (*self.eye_color, 100), (right_eye_x, eye_y), eye_size + 3)
            pygame.draw.circle(screen, self.eye_color, (left_eye_x, eye_y), eye_size)
            pygame.draw.circle(screen, self.eye_color, (right_eye_x, eye_y), eye_size)
            pygame.draw.circle(screen, WHITE, (left_eye_x - 3, eye_y - 3), 4)
            pygame.draw.circle(screen, WHITE, (right_eye_x - 3, eye_y - 3), 4)
            
            if self.state in [self.STATE_CELEBRATE, self.STATE_MEGA_CELEBRATE]:
                pygame.draw.arc(screen, WHITE, 
                               (left_eye_x - eye_size, eye_y - eye_size, 
                                eye_size * 2, eye_size * 2), 0, math.pi, 4)
                pygame.draw.arc(screen, WHITE, 
                               (right_eye_x - eye_size, eye_y - eye_size, 
                                eye_size * 2, eye_size * 2), 0, math.pi, 4)
        else:
            pygame.draw.line(screen, self.eye_color, 
                            (left_eye_x - 8, eye_y), (left_eye_x + 8, eye_y), 4)
            pygame.draw.line(screen, self.eye_color, 
                            (right_eye_x - 8, eye_y), (right_eye_x + 8, eye_y), 4)
        
        # BOCA
        mouth_y = y + 42
        if self.state in [self.STATE_CELEBRATE, self.STATE_MEGA_CELEBRATE]:
            pygame.draw.arc(screen, self.accent_color,
                           (center_x - 15, mouth_y - 8, 30, 18), math.pi, math.pi * 2, 3)
        else:
            pygame.draw.arc(screen, self.accent_color,
                           (center_x - 9, mouth_y - 5, 18, 12), math.pi, math.pi * 2, 3)
        
        # CUERPO
        body_rect = pygame.Rect(x + 15, y + 52, self.width - 30, 45)
        pygame.draw.rect(screen, self.body_color, body_rect, border_radius=8)
        pygame.draw.rect(screen, self.body_highlight, body_rect, 3, border_radius=8)
        
        # Panel central
        panel_y = y + 62
        panel_glow = abs(math.sin(pygame.time.get_ticks() * 0.005)) * 0.5 + 0.5
        panel_color = (int(self.accent_color[0] * panel_glow),
                      int(self.accent_color[1] * panel_glow),
                      int(self.accent_color[2] * panel_glow))
        pygame.draw.rect(screen, panel_color, (center_x - 12, panel_y, 24, 12), border_radius=3)
        
        # BRAZOS
        arm_y = y + 60
        arm_length = 22
        
        if self.state in [self.STATE_CELEBRATE, self.STATE_MEGA_CELEBRATE]:
            left_angle = math.radians(-45 + self.celebrate_arms)
            right_angle = math.radians(-135 - self.celebrate_arms)
        else:
            left_angle = math.radians(30)
            right_angle = math.radians(150)
        
        left_arm_end_x = x + 8 + math.cos(left_angle) * arm_length
        left_arm_end_y = arm_y + math.sin(left_angle) * arm_length
        pygame.draw.line(screen, self.body_highlight, (x + 15, arm_y), 
                        (left_arm_end_x, left_arm_end_y), 7)
        pygame.draw.circle(screen, self.accent_color, 
                          (int(left_arm_end_x), int(left_arm_end_y)), 6)
        
        right_arm_end_x = x + self.width - 8 + math.cos(right_angle) * arm_length
        right_arm_end_y = arm_y + math.sin(right_angle) * arm_length
        pygame.draw.line(screen, self.body_highlight, (x + self.width - 15, arm_y), 
                        (right_arm_end_x, right_arm_end_y), 7)
        pygame.draw.circle(screen, self.accent_color, 
                          (int(right_arm_end_x), int(right_arm_end_y)), 6)
        
        # PIERNAS
        base_y = y + 93
        pygame.draw.rect(screen, self.body_highlight, (center_x - 22, base_y, 15, 15), border_radius=4)
        pygame.draw.rect(screen, self.body_highlight, (center_x + 7, base_y, 15, 15), border_radius=4)
    
    def _draw_streak_indicator(self, screen, x, y):
        """Muestra indicador de racha encima del robot"""
        indicator_y = y - 60
        center_x = x + self.width // 2
        
        # Fondo
        bg_width = 80
        bg_height = 30
        bg_surface = pygame.Surface((bg_width, bg_height), pygame.SRCALPHA)
        pygame.draw.rect(bg_surface, (20, 60, 100, 200), (0, 0, bg_width, bg_height), border_radius=8)
        
        # Borde según racha
        if self.streak >= 6:
            border_color = GOLD
        elif self.streak >= 4:
            border_color = PURPLE
        else:
            border_color = CYAN
        pygame.draw.rect(bg_surface, border_color, (0, 0, bg_width, bg_height), 2, border_radius=8)
        
        screen.blit(bg_surface, (center_x - bg_width // 2, indicator_y))
        
        # Texto
        streak_text = f"🔥 x{self.streak}"
        text_surface = self.font_streak.render(streak_text, True, WHITE)
        text_rect = text_surface.get_rect(center=(center_x, indicator_y + bg_height // 2))
        screen.blit(text_surface, text_rect)
    
    def _draw_message(self, screen, x, y):
        if not self.current_message:
            return
        
        msg_x = x + self.width // 2
        msg_y = y - 100 + self.celebrate_jump
        
        if self.message_timer > 100:
            scale = 1.0 + 0.3 * ((120 - self.message_timer) / 20)
        elif self.message_timer < 20:
            scale = self.message_timer / 20
        else:
            scale = 1.0
        
        text_surface = self.font.render(self.current_message, True, GOLD)
        
        if scale != 1.0:
            new_width = int(text_surface.get_width() * scale)
            new_height = int(text_surface.get_height() * scale)
            if new_width > 0 and new_height > 0:
                text_surface = pygame.transform.scale(text_surface, (new_width, new_height))
        
        bubble_width = text_surface.get_width() + 24
        bubble_height = text_surface.get_height() + 14
        bubble_rect = pygame.Rect(msg_x - bubble_width // 2, msg_y - bubble_height // 2,
                                  bubble_width, bubble_height)
        
        bubble_surface = pygame.Surface((bubble_width, bubble_height), pygame.SRCALPHA)
        pygame.draw.rect(bubble_surface, (20, 40, 60, 220), 
                        (0, 0, bubble_width, bubble_height), border_radius=12)
        pygame.draw.rect(bubble_surface, GOLD, 
                        (0, 0, bubble_width, bubble_height), 3, border_radius=12)
        screen.blit(bubble_surface, bubble_rect)
        
        triangle_points = [
            (msg_x - 10, msg_y + bubble_height // 2),
            (msg_x + 10, msg_y + bubble_height // 2),
            (msg_x, msg_y + bubble_height // 2 + 12)
        ]
        pygame.draw.polygon(screen, (20, 40, 60), triangle_points)
        
        text_shadow = self.font.render(self.current_message, True, (0, 0, 0))
        if scale != 1.0 and new_width > 0 and new_height > 0:
            text_shadow = pygame.transform.scale(text_shadow, (new_width, new_height))
        
        text_rect = text_surface.get_rect(center=(msg_x, msg_y))
        screen.blit(text_shadow, (text_rect.x + 2, text_rect.y + 2))
        screen.blit(text_surface, text_rect)
