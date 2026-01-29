# -*- coding: utf-8 -*-
"""
SoundManager - Gestor de sonidos del juego
"""

import pygame
import os
from utils.resource import resource_path

# Importar librerías opcionales
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

try:
    from scipy import signal
    from scipy.io import wavfile
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False


class SoundManager:
    """Gestor de sonidos profesionales del juego usando scipy y numpy"""
    
    def __init__(self):
        self.sounds = {}
        self.music_playing = False
        self.sample_rate = 44100  # Calidad CD
        self.current_music = None
        self.current_level = 1
        self.music_channel = None
        self.hit_sound_index = 0  # Para alternar entre los dos sonidos de hit
        self.final_sound_channel = None  # Canal para el sonido final (para poder detenerlo)
        self._create_professional_sounds()
        # No iniciar música automáticamente, se iniciará cuando comience el juego
    
    def _apply_envelope(self, sig, attack=0.01, decay=0.1, sustain=0.7, release=0.2):
        """Aplica envolvente ADSR al sonido"""
        if not HAS_SCIPY or not HAS_NUMPY:
            return sig
            
        total_duration = len(sig) / self.sample_rate
        frames = len(sig)
        envelope = np.ones(frames)
        
        attack_frames = int(attack * self.sample_rate)
        decay_frames = int(decay * self.sample_rate)
        release_frames = int(release * self.sample_rate)
        sustain_frames = frames - attack_frames - decay_frames - release_frames
        
        # Attack
        if attack_frames > 0:
            envelope[:attack_frames] = np.linspace(0, 1, attack_frames)
        
        # Decay
        if decay_frames > 0:
            start_idx = attack_frames
            envelope[start_idx:start_idx+decay_frames] = np.linspace(1, sustain, decay_frames)
        
        # Sustain
        if sustain_frames > 0:
            start_idx = attack_frames + decay_frames
            envelope[start_idx:start_idx+sustain_frames] = sustain
        
        # Release
        if release_frames > 0:
            start_idx = frames - release_frames
            envelope[start_idx:] = np.linspace(sustain, 0, release_frames)
        
        return sig * envelope
    
    def _generate_laser_shot(self, duration=0.1):
        """Genera sonido de disparo estilo arcade retro"""
        if not HAS_NUMPY:
            return None
            
        frames = int(duration * self.sample_rate)
        t = np.linspace(0, duration, frames)
        max_sample = 2**(16 - 1) - 1
        
        # Frecuencia que desciende rápidamente (efecto "pew")
        freq_start = 1200
        freq_end = 400
        freq = freq_start * (1 - t / duration) + freq_end * (t / duration)
        
        # Onda cuadrada simulada
        sig = np.sign(np.sin(2 * np.pi * freq * t)) * 0.6
        sig += 0.3 * np.sign(np.sin(2 * np.pi * freq * 2 * t))
        
        # Click inicial
        click = np.exp(-t * 100) * np.sin(2 * np.pi * 3000 * t) * 0.2
        sig = sig + click
        
        # Envolvente rápida
        envelope = np.exp(-t * 25)
        sig *= envelope
        
        sig = np.clip(sig, -1, 1) * 0.8
        sound_array = np.zeros((frames, 2), dtype=np.int16)
        sound_array[:, 0] = (sig * max_sample).astype(np.int16)
        sound_array[:, 1] = sound_array[:, 0]
        
        return pygame.sndarray.make_sound(sound_array)
    
    def _generate_explosion(self, duration=0.5):
        """Genera sonido de explosión estilo arcade retro"""
        if not HAS_NUMPY:
            return None
            
        frames = int(duration * self.sample_rate)
        t = np.linspace(0, duration, frames)
        max_sample = 2**(16 - 1) - 1
        
        # Ruido blanco filtrado (explosión)
        noise = np.random.normal(0, 0.8, frames)
        if HAS_SCIPY:
            # Filtro paso bajo que desciende
            cutoff = 0.4 * (1 - 0.8 * t / duration) + 0.1
            cutoff = np.clip(cutoff, 0.01, 0.99)
            try:
                b, a = signal.butter(4, min(0.9, max(0.1, cutoff[0])), 'low')
                noise = signal.filtfilt(b, a, noise)
            except:
                pass  # If filter fails, use unfiltered noise
        
        # Tono bajo descendente (boom)
        boom_freq = 100 * (1 - 0.7 * t / duration) + 30
        boom = np.sin(2 * np.pi * boom_freq * t) * 0.4
        boom += 0.2 * np.sin(2 * np.pi * boom_freq * 2 * t)
        
        # Mezclar
        audio_sig = 0.6 * noise + 0.4 * boom
        
        # Envolvente exponencial
        envelope = np.exp(-t * 8)
        audio_sig *= envelope
        
        audio_sig = np.clip(audio_sig, -1, 1) * 0.85
        sound_array = np.zeros((frames, 2), dtype=np.int16)
        sound_array[:, 0] = (audio_sig * max_sample).astype(np.int16)
        sound_array[:, 1] = sound_array[:, 0]
        
        return pygame.sndarray.make_sound(sound_array)
    
    def _generate_hit(self, duration=0.15):
        """Genera sonido de impacto explosivo y grave"""
        if not HAS_NUMPY:
            return None
            
        frames = int(duration * self.sample_rate)
        t = np.linspace(0, duration, frames)
        max_sample = 2**(16 - 1) - 1
        
        # Frecuencia base muy grave para sonido explosivo
        freq_base = 80
        freq_harmonic1 = 160
        freq_harmonic2 = 240
        
        sig = np.sin(2 * np.pi * freq_base * t) * 1.0
        sig += 0.6 * np.sin(2 * np.pi * freq_harmonic1 * t)
        sig += 0.3 * np.sin(2 * np.pi * freq_harmonic2 * t)
        
        # Agregar ruido filtrado
        if HAS_SCIPY:
            noise = np.random.normal(0, 0.3, frames)
            try:
                b, a = signal.butter(4, 0.2, 'low')
                noise_filtered = signal.filtfilt(b, a, noise)
                sig += noise_filtered * 0.4
            except:
                pass
        
        # Envolvente explosiva
        attack_time = 0.005
        attack_frames = int(attack_time * self.sample_rate)
        if attack_frames > 0:
            attack_envelope = np.linspace(0, 1, attack_frames)
            decay_envelope = np.exp(-(t[attack_frames:] - attack_time) * 8)
            envelope = np.concatenate([attack_envelope, decay_envelope])
        else:
            envelope = np.exp(-t * 8)
        
        sig *= envelope
        
        sig = np.clip(sig, -1, 1) * 1.0
        sound_array = np.zeros((frames, 2), dtype=np.int16)
        sound_array[:, 0] = (sig * max_sample).astype(np.int16)
        sound_array[:, 1] = sound_array[:, 0]
        
        return pygame.sndarray.make_sound(sound_array)
    
    def _generate_success_chime(self, duration=0.3):
        """Genera sonido de éxito estilo arcade (melodía ascendente)"""
        if not HAS_NUMPY:
            return None
            
        frames = int(duration * self.sample_rate)
        t = np.linspace(0, duration, frames)
        max_sample = 2**(16 - 1) - 1
        
        note1_duration = duration / 3
        note2_duration = duration / 3
        note3_duration = duration / 3
        
        sig = np.zeros(frames)
        
        # Nota 1: Do
        note1_frames = int(note1_duration * self.sample_rate)
        if note1_frames > 0:
            t1 = np.linspace(0, note1_duration, note1_frames)
            freq1 = 523.25
            sig[:note1_frames] = np.sin(2 * np.pi * freq1 * t1) * 0.5
        
        # Nota 2: Mi
        note2_start = note1_frames
        note2_frames = int(note2_duration * self.sample_rate)
        if note2_frames > 0 and note2_start + note2_frames <= frames:
            t2 = np.linspace(0, note2_duration, note2_frames)
            freq2 = 659.25
            sig[note2_start:note2_start+note2_frames] = np.sin(2 * np.pi * freq2 * t2) * 0.5
        
        # Nota 3: Sol
        note3_start = note1_frames + note2_frames
        note3_frames = frames - note3_start
        if note3_frames > 0:
            t3 = np.linspace(0, note3_duration, note3_frames)
            freq3 = 783.99
            sig[note3_start:] = np.sin(2 * np.pi * freq3 * t3) * 0.5
        
        envelope = np.exp(-t * 3)
        sig *= envelope
        
        sig = np.clip(sig, -1, 1) * 0.7
        sound_array = np.zeros((frames, 2), dtype=np.int16)
        sound_array[:, 0] = (sig * max_sample).astype(np.int16)
        sound_array[:, 1] = sound_array[:, 0]
        
        return pygame.sndarray.make_sound(sound_array)
    
    def _generate_error_buzz(self, duration=0.25):
        """Genera sonido de error estilo arcade (buzz descendente)"""
        if not HAS_NUMPY:
            return None
            
        frames = int(duration * self.sample_rate)
        t = np.linspace(0, duration, frames)
        max_sample = 2**(16 - 1) - 1
        
        freq_start = 500
        freq_end = 200
        freq = freq_start * (1 - t / duration) + freq_end * (t / duration)
        
        sig = np.sign(np.sin(2 * np.pi * freq * t)) * 0.5
        sig += 0.3 * np.sign(np.sin(2 * np.pi * freq * 1.2 * t))
        
        envelope = np.exp(-t * 4)
        sig *= envelope
        
        sig = np.clip(sig, -1, 1) * 0.6
        sound_array = np.zeros((frames, 2), dtype=np.int16)
        sound_array[:, 0] = (sig * max_sample).astype(np.int16)
        sound_array[:, 1] = sound_array[:, 0]
        
        return pygame.sndarray.make_sound(sound_array)
    
    def _generate_damage_sound(self, duration=0.2):
        """Genera sonido de daño estilo arcade retro"""
        if not HAS_NUMPY:
            return None
            
        frames = int(duration * self.sample_rate)
        t = np.linspace(0, duration, frames)
        max_sample = 2**(16 - 1) - 1
        
        freq_start = 800
        freq_end = 300
        freq = freq_start * (1 - t / duration) + freq_end * (t / duration)
        
        vibrato = 0.1 * np.sin(2 * np.pi * 20 * t)
        freq_modulated = freq * (1 + vibrato)
        
        sig = np.sin(2 * np.pi * freq_modulated * t) * 0.6
        sig += 0.3 * np.sin(2 * np.pi * freq_modulated * 2 * t)
        
        envelope = np.exp(-t * 5)
        sig *= envelope
        
        sig = np.clip(sig, -1, 1) * 0.75
        sound_array = np.zeros((frames, 2), dtype=np.int16)
        sound_array[:, 0] = (sig * max_sample).astype(np.int16)
        sound_array[:, 1] = sound_array[:, 0]
        
        return pygame.sndarray.make_sound(sound_array)
    
    def _create_professional_sounds(self):
        """Crea sonidos profesionales usando scipy o carga archivos si existen"""
        try:
            # Inicializar diccionario de sonidos
            sound_keys = ['shoot', 'explosion', 'hit', 'correct', 'wrong', 'damage']
            for key in sound_keys:
                self.sounds[key] = None

            # Intentar cargar sonidos personalizados desde la carpeta sounds
            sounds_dir = resource_path('sounds')
            
            # Cargar laser_combo si existe (sonido especial para combo)
            combo_path = os.path.join(sounds_dir, 'laser_combo.wav')
            if os.path.exists(combo_path):
                try:
                    self.sounds['laser_combo'] = pygame.mixer.Sound(combo_path)
                    print(f"✓ Sonido de combo cargado: {combo_path}")
                except Exception as e:
                    print(f"Error cargando laser_combo: {e}")
                    self.sounds['laser_combo'] = None
            else:
                self.sounds['laser_combo'] = None

            # Cargar final.wav (sonido de victoria final)
            final_path = os.path.join(sounds_dir, 'final.wav')
            if os.path.exists(final_path):
                try:
                    self.sounds['final'] = pygame.mixer.Sound(final_path)
                    print(f"✓ Sonido final cargado: {final_path}")
                except Exception as e:
                    print(f"Error cargando final.wav: {e}")
                    self.sounds['final'] = None
            else:
                self.sounds['final'] = None

            if HAS_NUMPY:
                # Generar sonidos sintetizados si no se cargaron archivos (o para complementar)
                self.sounds['shoot'] = self._generate_laser_shot()
                self.sounds['explosion'] = self._generate_explosion()
                self.sounds['hit'] = self._generate_hit()
                self.sounds['correct'] = self._generate_success_chime()
                self.sounds['wrong'] = self._generate_error_buzz()
                self.sounds['damage'] = self._generate_damage_sound()
            else:
                print("Numpy no disponible, sonidos generados deshabilitados")
                
        except Exception as e:
            print(f"Error creando sonidos profesionales: {e}")
    
    def _start_background_music(self, level=1, volume=0.5):
        """Inicia música de fondo desde archivo Battleship.ogg"""
        try:
            # Si ya está sonando la música de nivel (Battleship), no reiniciar (a menos que cambie algo drástico)
            # Nota: Todos los niveles usan Battleship.ogg por ahora
            if self.music_playing and pygame.mixer.music.get_busy() and getattr(self, 'current_track_name', '') == 'battleship':
                return
            
            pygame.mixer.music.stop()
            
            music_path = resource_path("sounds", "Battleship.ogg")
            if not os.path.exists(music_path):
                print(f"Error: No se encontró el archivo {music_path}")
                self.music_playing = False
                return
            
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(-1)
            self.music_playing = True
            self.current_track_name = 'battleship'
            self.current_level = level
            print(f"Música de ambiente iniciada para nivel {level}")
        except Exception as e:
            print(f"Error cargando música de fondo: {e}")
            self.music_playing = False
    
    def stop_background_music(self):
        """Detiene la música de fondo"""
        try:
            pygame.mixer.music.stop()
            self.music_playing = False
        except Exception as e:
            print(f"Error deteniendo música de fondo: {e}")
    
    def change_level_music(self, level, volume=0.5):
        """Cambia la música de ambiente según el nivel"""
        self._start_background_music(level, volume)

    def play_menu_music(self, volume=0.5, start=0.5):
        """Reproduce música del menú"""
        # Si ya está sonando la música del menú, no reiniciar
        if self.music_playing and pygame.mixer.music.get_busy() and getattr(self, 'current_track_name', '') == 'menu':
            return

        try:
            # Detener cualquier música que esté sonando antes de reproducir la del menú
            pygame.mixer.music.stop()
            
            music_path = resource_path("sounds", "Brave Pilots (Menu Screen).ogg")
            if not os.path.exists(music_path):
                print(f"Error: No se encontró {music_path}")
                return
            
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(-1, start=start) # Loop infinito
            self.music_playing = True
            self.current_track_name = 'menu'
            print(f"Música de menú iniciada (start={start}s)")
        except Exception as e:
            print(f"Error cargando música de menú: {e}")
    
    def play_sound(self, sound_name, volume=0.5, game_sound_volume=1.0, loops=0):
        """Reproduce un sonido con volumen ajustable
        
        Args:
            sound_name: Nombre del sonido a reproducir
            volume: Volumen base (0.0 a 1.0)
            game_sound_volume: Volumen del juego (0.0 a 1.0)
            loops: Número de loops (-1 para loop infinito, 0 para reproducir una vez)
        """
        try:
            if sound_name in self.sounds and self.sounds[sound_name] is not None:
                if sound_name == 'hit':
                    final_volume = min(1.0, volume * game_sound_volume * 1.5)
                else:
                    final_volume = volume * game_sound_volume
                
                self.sounds[sound_name].set_volume(final_volume)
                channel = self.sounds[sound_name].play(loops=loops)
                
                # Guardar el canal si es el sonido final para poder detenerlo después
                if sound_name == 'final':
                    self.final_sound_channel = channel
                
                return channel
        except Exception as e:
            pass
        return None
    
    def stop_final_sound(self):
        """Detiene el sonido final si está reproduciéndose"""
        try:
            if self.final_sound_channel is not None:
                self.final_sound_channel.stop()
                self.final_sound_channel = None
        except Exception as e:
            pass
