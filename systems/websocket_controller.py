# -*- coding: utf-8 -*-
"""
WebSocket Controller - Se conecta al servidor WebSocket remoto y recibe señales
"""

import pygame
import threading
import asyncio

try:
    import websockets
except ImportError:
    websockets = None
    print("ADVERTENCIA: websockets no está instalado. Ejecuta: pip install websockets")


class WebSocketController:
    """Controlador WebSocket que se conecta al servidor remoto y recibe señales"""
    
    # Mapeo de señales a teclas pygame
    SIGNAL_TO_KEY = {
        # Operaciones matemáticas (WASD)
        "SUM": pygame.K_w,      # Suma (+)
        "SUB": pygame.K_a,      # Resta (-)
        "MUL": pygame.K_s,      # Multiplicación (*)
        "DIV": pygame.K_d,      # División (/)
        
        # Movimiento horizontal de la nave
        "LEFT": pygame.K_LEFT,
        "RIGHT": pygame.K_RIGHT,
        
        # Navegación del menú
        "UP": pygame.K_UP,
        "DOWN": pygame.K_DOWN,
        
        # Acciones especiales
        "PAUSE": pygame.K_ESCAPE,
        "RESET": pygame.K_r,
    }
    
    def __init__(self, server_url="ws://10.219.2.8:81/"):
        """Inicializa el controlador WebSocket como cliente"""
        self.server_url = server_url
        self.running = False
        self.thread = None
        self.loop = None
        self.connected = False
        
        # Estado de teclas presionadas (para simular key_pressed continuo)
        self.pressed_keys = set()
        self.pressed_lock = threading.Lock()
        
    def start(self):
        """Inicia la conexión WebSocket en un hilo separado"""
        if websockets is None:
            print("WebSocket Controller: No se puede iniciar sin la librería websockets")
            return False
            
        self.running = True
        self.thread = threading.Thread(target=self._run_client, daemon=True)
        self.thread.start()
        print(f"WebSocket Controller conectando a {self.server_url}")
        return True
    
    def stop(self):
        """Detiene la conexión WebSocket"""
        self.running = False
        if self.loop:
            self.loop.call_soon_threadsafe(self.loop.stop)
        if self.thread:
            self.thread.join(timeout=2.0)
        print("WebSocket Controller detenido")
    
    def _run_client(self):
        """Ejecuta el cliente WebSocket en su propio event loop"""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
        try:
            self.loop.run_until_complete(self._connect_and_listen())
        except Exception as e:
            print(f"Error en WebSocket client: {e}")
        finally:
            self.loop.close()
    
    async def _connect_and_listen(self):
        """Conecta al servidor WebSocket y escucha mensajes"""
        while self.running:
            try:
                async with websockets.connect(self.server_url) as websocket:
                    self.connected = True
                    print(f"✓ Conectado a WebSocket: {self.server_url}")
                    
                    async for message in websocket:
                        if not self.running:
                            break
                        self._process_signal(message.strip().upper())
                        
            except websockets.exceptions.ConnectionClosed:
                print("Conexión WebSocket cerrada, reconectando...")
                self.connected = False
            except Exception as e:
                print(f"Error WebSocket: {e}, reintentando en 2s...")
                self.connected = False
                await asyncio.sleep(2)
    
    def _process_signal(self, signal):
        """Procesa una señal recibida y la convierte en evento pygame"""
        print(f"Señal recibida: {signal}")
        
        # Manejar señal PLAY como click izquierdo
        if signal == "PLAY":
            self._post_mouse_click()
            return
        
        # Manejar señales de movimiento continuo
        if signal.endswith("_START"):
            base_signal = signal.replace("_START", "")
            if base_signal in self.SIGNAL_TO_KEY:
                with self.pressed_lock:
                    self.pressed_keys.add(base_signal)
                self._post_key_event(self.SIGNAL_TO_KEY[base_signal], pygame.KEYDOWN)
            return
        
        if signal.endswith("_STOP"):
            base_signal = signal.replace("_STOP", "")
            if base_signal in self.SIGNAL_TO_KEY:
                with self.pressed_lock:
                    self.pressed_keys.discard(base_signal)
                self._post_key_event(self.SIGNAL_TO_KEY[base_signal], pygame.KEYUP)
            return
        
        # Manejar señales normales (tecla presionada y liberada)
        if signal in self.SIGNAL_TO_KEY:
            key = self.SIGNAL_TO_KEY[signal]
            self._post_key_event(key, pygame.KEYDOWN)
            # Para teclas de una sola pulsación, también enviar KEYUP después
            self._post_key_event(key, pygame.KEYUP)
    
    def _post_key_event(self, key, event_type):
        """Publica un evento de tecla en la cola de pygame"""
        try:
            event = pygame.event.Event(event_type, key=key)
            pygame.event.post(event)
        except Exception as e:
            print(f"Error al publicar evento: {e}")
    
    def _post_mouse_click(self):
        """Publica un evento de click izquierdo del mouse"""
        try:
            # Obtener posición actual del mouse o usar centro de pantalla
            try:
                pos = pygame.mouse.get_pos()
            except:
                pos = (512, 300)  # Centro aproximado
            
            # Publicar evento de click
            event = pygame.event.Event(
                pygame.MOUSEBUTTONDOWN,
                button=1,
                pos=pos
            )
            pygame.event.post(event)
            
            # También publicar MOUSEBUTTONUP
            event_up = pygame.event.Event(
                pygame.MOUSEBUTTONUP,
                button=1,
                pos=pos
            )
            pygame.event.post(event_up)
        except Exception as e:
            print(f"Error al publicar click: {e}")
    
    def is_key_pressed(self, signal):
        """Verifica si una señal está actualmente presionada"""
        with self.pressed_lock:
            return signal in self.pressed_keys
    
    def get_pressed_keys(self):
        """Obtiene el conjunto de señales actualmente presionadas"""
        with self.pressed_lock:
            return self.pressed_keys.copy()


# Instancia global del controlador
_controller_instance = None

def get_controller():
    """Obtiene la instancia global del controlador"""
    global _controller_instance
    if _controller_instance is None:
        _controller_instance = WebSocketController()
    return _controller_instance

def start_controller(server_url="ws://10.219.2.8:81/"):
    """Inicia el controlador WebSocket global"""
    global _controller_instance
    _controller_instance = WebSocketController(server_url)
    return _controller_instance.start()

def stop_controller():
    """Detiene el controlador WebSocket global"""
    global _controller_instance
    if _controller_instance:
        _controller_instance.stop()
