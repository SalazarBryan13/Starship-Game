# -*- coding: utf-8 -*-
"""
Efectos visuales para el sistema de combos
"""

import pygame
import random
import math

from config import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, CYAN, YELLOW, GOLD, PURPLE


class ComboIndicator:
    """Indicador visual del progreso del combo (1-5)"""
    
    def __init__(self):
        self.combo_count = 0
        self.max_combo = 5
        self.pulse_timer = 0
        self.x = SCREEN_WIDTH - 120
        self.y = 150
        
    def update(self, combo_count):
        """Actualiza el estado del indicador"""
        self.combo_count = combo_count
        self.pulse_timer += 1
        
    def draw(self, screen, font):
        """Dibuja el indicador de combo"""
        if self.combo_count == 0:
            return
            
        # Pulso para dar vida al indicador
        pulse = (math.sin(self.pulse_timer * 0.15) + 1) / 2
        
        # Panel de fondo
        panel_w = 100
        panel_h = 35
        panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        
        # Color del panel basado en progreso
        progress = self.combo_count / self.max_combo
        if progress >= 1:
            bg_color = (255, 215, 0, 180)  # Dorado cuando está lleno
            border_color = GOLD
        else:
            bg_color = (20, 40, 60, 180)
            border_color = CYAN
            
        pygame.draw.rect(panel, bg_color, (0, 0, panel_w, panel_h), border_radius=8)
        pygame.draw.rect(panel, border_color, (0, 0, panel_w, panel_h), 2, border_radius=8)
        
        screen.blit(panel, (self.x, self.y))
        
        # Texto "COMBO"
        combo_text = font.render("COMBO", True, WHITE)
        screen.blit(combo_text, (self.x + 10, self.y + 5))
        
        # Indicadores de progreso (5 círculos)
        circle_y = self.y + 25
        circle_start_x = self.x + 12
        circle_spacing = 18
        
        for i in range(self.max_combo):
            cx = circle_start_x + i * circle_spacing
            if i < self.combo_count:
                # Círculo lleno con glow
                glow_size = 6 + int(pulse * 2) if i == self.combo_count - 1 else 6
                pygame.draw.circle(screen, GOLD, (cx, circle_y), glow_size)
                pygame.draw.circle(screen, WHITE, (cx, circle_y), 4)
            else:
                # Círculo vacío
                pygame.draw.circle(screen, (60, 80, 100), (cx, circle_y), 5, 1)


class ComboShockwave:
    """Onda expansiva circular para el combo attack"""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 20
        self.max_radius = 400
        self.speed = 15
        self.life = 1.0
        self.color = GOLD
        
    def update(self):
        """Actualiza la onda expansiva"""
        self.radius += self.speed
        self.life = 1.0 - (self.radius / self.max_radius)
        
    def draw(self, screen):
        """Dibuja la onda expansiva con múltiples anillos"""
        if self.life <= 0:
            return
            
        alpha = int(200 * self.life)
        
        # Anillo principal
        wave_surface = pygame.Surface((self.max_radius * 2, self.max_radius * 2), pygame.SRCALPHA)
        center = self.max_radius
        
        # Múltiples anillos para efecto más rico
        for i in range(3):
            ring_radius = max(1, int(self.radius - i * 8))
            ring_alpha = max(0, alpha - i * 40)
            thickness = 4 - i
            if ring_radius > 0 and ring_alpha > 0:
                pygame.draw.circle(wave_surface, (*self.color[:3], ring_alpha), 
                                 (center, center), ring_radius, max(1, thickness))
        
        # Brillo interior
        inner_alpha = int(50 * self.life)
        if inner_alpha > 0:
            inner_surface = pygame.Surface((int(self.radius * 2), int(self.radius * 2)), pygame.SRCALPHA)
            pygame.draw.circle(inner_surface, (*YELLOW[:3], inner_alpha), 
                             (int(self.radius), int(self.radius)), int(self.radius))
            screen.blit(inner_surface, (self.x - self.radius, self.y - self.radius))
        
        screen.blit(wave_surface, (self.x - center, self.y - center))
        
    def is_dead(self):
        return self.radius >= self.max_radius


class LightningBolt:
    """Rayo de energía brillante desde el jugador a un enemigo - efecto más visible y duradero"""
    
    def __init__(self, start_x, start_y, end_x, end_y):
        self.start_x = start_x
        self.start_y = start_y
        self.end_x = end_x
        self.end_y = end_y
        self.life = 60  # Duración más larga (1 segundo)
        self.max_life = 60
        self.pulse_timer = 0
        self.beam_width = 0  # Ancho inicial del rayo
        self.max_beam_width = 20
        
    def update(self):
        """Actualiza el rayo de energía"""
        self.life -= 1
        self.pulse_timer += 1
        
        # Animación del ancho del rayo (crece rápido, se mantiene, luego decrece)
        progress = self.life / self.max_life
        if progress > 0.85:
            # Fase de crecimiento rápido
            self.beam_width = self.max_beam_width * ((1.0 - progress) / 0.15)
        elif progress > 0.2:
            # Fase de mantenimiento con pulso
            pulse = (math.sin(self.pulse_timer * 0.4) + 1) / 2
            self.beam_width = self.max_beam_width * (0.8 + 0.2 * pulse)
        else:
            # Fase de desvanecimiento
            self.beam_width = self.max_beam_width * (progress / 0.2)
        
    def draw(self, screen):
        """Dibuja el rayo de energía con efecto de flujo brillante"""
        if self.life <= 0 or self.beam_width <= 0:
            return
        
        alpha = min(255, int(255 * (self.life / self.max_life) * 1.5))
        pulse = (math.sin(self.pulse_timer * 0.5) + 1) / 2
        
        # Crear superficie para el rayo
        beam_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        
        # Calcular ángulo y longitud del rayo
        dx = self.end_x - self.start_x
        dy = self.end_y - self.start_y
        length = math.sqrt(dx*dx + dy*dy)
        
        if length == 0:
            return
            
        # Vector normalizado
        nx = dx / length
        ny = dy / length
        
        # Vector perpendicular para el grosor
        px = -ny
        py = nx
        
        # Dibujar múltiples capas del rayo para efecto de glow
        layers = [
            (self.beam_width * 1.5, (255, 200, 50, alpha // 6)),      # Glow externo amarillo
            (self.beam_width * 1.2, (255, 220, 100, alpha // 4)),     # Glow medio
            (self.beam_width * 0.9, (255, 240, 150, alpha // 2)),     # Glow interno
            (self.beam_width * 0.6, (255, 255, 200, int(alpha * 0.8))),  # Core brillante
            (self.beam_width * 0.3, (255, 255, 255, alpha)),          # Núcleo blanco
        ]
        
        for width, color in layers:
            if width > 0:
                hw = width / 2
                points = [
                    (self.start_x + px * hw, self.start_y + py * hw),
                    (self.start_x - px * hw, self.start_y - py * hw),
                    (self.end_x - px * hw, self.end_y - py * hw),
                    (self.end_x + px * hw, self.end_y + py * hw),
                ]
                pygame.draw.polygon(beam_surface, color, points)
        
        # Añadir partículas a lo largo del rayo
        num_particles = 8
        for i in range(num_particles):
            t = (i + self.pulse_timer * 0.1) % 1.0
            particle_x = self.start_x + dx * t + random.randint(-5, 5)
            particle_y = self.start_y + dy * t + random.randint(-5, 5)
            particle_size = random.randint(2, 5)
            particle_alpha = int(alpha * (1 - abs(t - 0.5) * 2))
            if particle_alpha > 0:
                pygame.draw.circle(beam_surface, (255, 255, 255, particle_alpha), 
                                 (int(particle_x), int(particle_y)), particle_size)
        
        # Brillo en el punto de impacto (más grande y brillante)
        impact_pulse = (math.sin(self.pulse_timer * 0.8) + 1) / 2
        impact_size = int(15 + 10 * impact_pulse)
        
        # Múltiples capas de brillo en el impacto
        for i in range(4):
            size = impact_size + (3 - i) * 8
            impact_alpha = max(0, alpha // (i + 1))
            pygame.draw.circle(beam_surface, (255, 255, 200, impact_alpha), 
                             (int(self.end_x), int(self.end_y)), size)
        
        # Brillo en el origen
        pygame.draw.circle(beam_surface, (255, 255, 150, alpha // 2), 
                          (int(self.start_x), int(self.start_y)), int(12 + 5 * pulse))
        
        screen.blit(beam_surface, (0, 0))
        
    def is_dead(self):
        return self.life <= 0


class ComboTextPopup:
    """Texto animado 'COMBO!' que aparece al activar el combo"""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.life = 90  # 1.5 segundos
        self.max_life = 90
        self.scale = 0.0
        self.target_scale = 1.5
        self.shake_x = 0
        self.shake_y = 0
        
    def update(self):
        """Actualiza la animación del texto"""
        self.life -= 1
        
        # Animación de escala (pop-in)
        if self.life > self.max_life - 15:
            # Fase de entrada rápida
            self.scale = min(self.target_scale * 1.3, self.scale + 0.2)
        elif self.life > self.max_life - 25:
            # Rebote
            self.scale = max(self.target_scale, self.scale - 0.05)
        else:
            # Estabilizar
            self.scale = self.target_scale
            
        # Shake durante los primeros frames
        if self.life > self.max_life - 20:
            self.shake_x = random.randint(-5, 5)
            self.shake_y = random.randint(-3, 3)
        else:
            self.shake_x = 0
            self.shake_y = 0
            
        # Subir lentamente
        if self.life < self.max_life - 30:
            self.y -= 0.5
        
    def draw(self, screen, font_large):
        """Dibuja el texto del combo con efectos"""
        if self.life <= 0:
            return
            
        # Calcular alpha
        if self.life < 30:
            alpha = int(255 * (self.life / 30))
        else:
            alpha = 255
            
        # Color con pulso
        pulse = (math.sin(self.life * 0.3) + 1) / 2
        r = int(255)
        g = int(200 + 55 * pulse)
        b = int(50 + 100 * pulse)
        
        # Texto principal
        try:
            # Crear fuente escalada
            font_size = int(48 * self.scale)
            combo_font = pygame.font.Font(None, font_size)
            
            # Texto con sombra
            text = "⚡ COMBO x5! ⚡"
            
            # Sombra
            shadow_surface = combo_font.render(text, True, (0, 0, 0))
            shadow_surface.set_alpha(alpha // 2)
            shadow_rect = shadow_surface.get_rect(center=(self.x + 3 + self.shake_x, 
                                                          self.y + 3 + self.shake_y))
            screen.blit(shadow_surface, shadow_rect)
            
            # Glow
            glow_surface = combo_font.render(text, True, (255, 150, 0))
            glow_surface.set_alpha(alpha // 2)
            for offset in [(2, 0), (-2, 0), (0, 2), (0, -2)]:
                glow_rect = glow_surface.get_rect(center=(self.x + offset[0] + self.shake_x, 
                                                          self.y + offset[1] + self.shake_y))
                screen.blit(glow_surface, glow_rect)
            
            # Texto principal
            text_surface = combo_font.render(text, True, (r, g, b))
            text_surface.set_alpha(alpha)
            text_rect = text_surface.get_rect(center=(self.x + self.shake_x, 
                                                       self.y + self.shake_y))
            screen.blit(text_surface, text_rect)
            
        except:
            pass
        
    def is_dead(self):
        return self.life <= 0


class ComboParticleBurst:
    """Explosión de partículas al activar el combo"""
    
    def __init__(self, x, y):
        self.particles = []
        self.x = x
        self.y = y
        
        # Crear partículas en todas direcciones
        for _ in range(40):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(5, 15)
            size = random.randint(3, 8)
            color = random.choice([GOLD, YELLOW, CYAN, WHITE, (255, 200, 100)])
            life = random.randint(30, 60)
            
            self.particles.append({
                'x': x,
                'y': y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'size': size,
                'color': color,
                'life': life,
                'max_life': life
            })
            
    def update(self):
        """Actualiza las partículas"""
        for p in self.particles:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['vx'] *= 0.95  # Fricción
            p['vy'] *= 0.95
            p['vy'] += 0.2   # Gravedad suave
            p['life'] -= 1
            
    def draw(self, screen):
        """Dibuja las partículas con glow"""
        for p in self.particles:
            if p['life'] > 0:
                alpha = int(255 * (p['life'] / p['max_life']))
                size = int(p['size'] * (p['life'] / p['max_life']))
                
                if size > 0:
                    # Glow
                    glow_surface = pygame.Surface((size * 4, size * 4), pygame.SRCALPHA)
                    pygame.draw.circle(glow_surface, (*p['color'][:3], alpha // 3), 
                                     (size * 2, size * 2), size * 2)
                    pygame.draw.circle(glow_surface, (*p['color'][:3], alpha), 
                                     (size * 2, size * 2), size)
                    screen.blit(glow_surface, (p['x'] - size * 2, p['y'] - size * 2))
                    
    def is_dead(self):
        return all(p['life'] <= 0 for p in self.particles)
