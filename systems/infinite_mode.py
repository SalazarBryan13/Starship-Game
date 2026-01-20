# -*- coding: utf-8 -*-
"""
Modo Infinito - Sistema de dificultad escalable
Gestiona las oleadas infinitas con dificultad progresiva
"""


class InfiniteMode:
    """Gestiona el modo infinito con dificultad escalable"""
    
    def __init__(self):
        self.wave = 0
        self.total_enemies_killed = 0
        
        # Configuración base
        self.base_enemies = 3
        self.max_enemies = 12
        self.base_hp = 3
        self.base_speed = 1
        
    def reset(self):
        """Reinicia el modo infinito"""
        self.wave = 0
        self.total_enemies_killed = 0
    
    def next_wave(self) -> dict:
        """
        Avanza a la siguiente oleada y retorna la configuración.
        
        Returns:
            dict con:
            - wave: número de oleada actual
            - num_enemies: cantidad de enemigos
            - enemy_hp: HP de cada enemigo
            - enemy_speed: velocidad de enemigos
            - num_range: rango de números para operaciones
            - visual_level: nivel visual para fondos/efectos (1-3)
        """
        self.wave += 1
        
        return {
            "wave": self.wave,
            "num_enemies": self._calc_enemies(),
            "enemy_hp": self._calc_hp(),
            "enemy_speed": self._calc_speed(),
            "num_range": self._calc_num_range(),
            "visual_level": self._calc_visual_level()
        }
    
    def get_current_config(self) -> dict:
        """Retorna la configuración de la oleada actual sin avanzar"""
        return {
            "wave": self.wave,
            "num_enemies": self._calc_enemies(),
            "enemy_hp": self._calc_hp(),
            "enemy_speed": self._calc_speed(),
            "num_range": self._calc_num_range(),
            "visual_level": self._calc_visual_level()
        }
    
    def _calc_enemies(self) -> int:
        """
        Calcula cantidad de enemigos para la oleada actual.
        Aumenta +1 cada 2 oleadas, máximo 12.
        Wave 1-2: 3, Wave 3-4: 4, Wave 5-6: 5, etc.
        """
        extra = (self.wave - 1) // 2
        return min(self.base_enemies + extra, self.max_enemies)
    
    def _calc_hp(self) -> int:
        """
        Calcula HP de enemigos para la oleada actual.
        Aumenta gradualmente: 3, 3, 4, 4, 5, 5, 6, 6...
        """
        extra = (self.wave - 1) // 2
        return self.base_hp + extra
    
    def _calc_speed(self) -> int:
        """
        Calcula velocidad de enemigos.
        Aumenta cada 4 oleadas: 1, 1, 1, 1, 2, 2, 2, 2, 3...
        """
        extra = (self.wave - 1) // 4
        return min(self.base_speed + extra, 4)  # Máx velocidad 4
    
    def _calc_num_range(self) -> tuple:
        """
        Calcula el rango de números para operaciones matemáticas.
        Aumenta progresivamente la dificultad.
        """
        if self.wave <= 2:
            return (1, 10)   # Fácil
        elif self.wave <= 5:
            return (1, 25)   # Medio-fácil
        elif self.wave <= 8:
            return (1, 50)   # Medio
        elif self.wave <= 12:
            return (1, 75)   # Medio-difícil
        else:
            return (1, 100)  # Difícil
    
    def _calc_visual_level(self) -> int:
        """
        Retorna el nivel visual (1-3) para ciclar entre estilos.
        Cambia cada oleada para variar la estética.
        """
        return ((self.wave - 1) % 3) + 1
    
    def add_kill(self, count: int = 1):
        """Registra enemigos eliminados"""
        self.total_enemies_killed += count
    
    def get_stats(self) -> dict:
        """Retorna estadísticas del modo infinito"""
        return {
            "wave": self.wave,
            "total_kills": self.total_enemies_killed,
            "current_difficulty": self._get_difficulty_label()
        }
    
    def _get_difficulty_label(self) -> str:
        """Retorna etiqueta de dificultad actual"""
        if self.wave <= 2:
            return "FÁCIL"
        elif self.wave <= 5:
            return "NORMAL"
        elif self.wave <= 8:
            return "DIFÍCIL"
        elif self.wave <= 12:
            return "EXPERTO"
        else:
            return "LEGENDARIO"
