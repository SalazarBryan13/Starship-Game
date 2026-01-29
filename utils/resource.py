import os
import sys


def resource_path(*relative_parts: str) -> str:
    """
    Devuelve una ruta absoluta a un recurso (assets) compatible con PyInstaller.

    - En desarrollo: relativa al directorio del proyecto (donde está `main.py`).
    - En PyInstaller (onefile/onedir): relativa a `sys._MEIPASS`.
    """
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        base = sys._MEIPASS  # type: ignore[attr-defined]
    else:
        # Proyecto: `utils/` cuelga del root del juego
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, *relative_parts)


def app_dir() -> str:
    """
    Directorio “real” de la app para escribir archivos (ej. resultados.json).
    En PyInstaller: carpeta del .exe. En desarrollo: carpeta del proyecto.
    """
    if getattr(sys, "frozen", False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def writable_path(filename: str) -> str:
    """Ruta donde podemos escribir archivos del juego."""
    return os.path.join(app_dir(), filename)



