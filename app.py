# -*- coding: utf-8 -*-
"""
Servidor Flask para desplegar el juego en Render
Sirve el juego compilado con Pygbag
"""

import os
from flask import Flask, send_from_directory, send_file, abort

app = Flask(__name__)

# Directorio donde se compilará el juego con Pygbag
BUILD_DIR = os.path.join(os.path.dirname(__file__), 'build', 'web')

# Crear el directorio si no existe
os.makedirs(BUILD_DIR, exist_ok=True)

@app.route('/')
def index():
    """Página principal que carga el juego"""
    # Buscar index.html en diferentes ubicaciones posibles
    possible_paths = [
        os.path.join(BUILD_DIR, 'index.html'),
        os.path.join(BUILD_DIR, 'main.html'),
        os.path.join(os.path.dirname(__file__), 'build', 'index.html'),
        os.path.join(os.path.dirname(__file__), 'index.html'),
        os.path.join(os.path.dirname(__file__), 'main.html'),
    ]
    
    for index_path in possible_paths:
        if os.path.exists(index_path):
            return send_file(index_path)
    
    # Si no se encuentra, mostrar mensaje de error
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Operación Relámpago - Juego Educativo</title>
        <meta charset="utf-8">
        <style>
            body {
                font-family: Arial, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            .container {
                text-align: center;
                padding: 2rem;
                background: rgba(0,0,0,0.3);
                border-radius: 10px;
                max-width: 600px;
            }
            .error {
                color: #ff6b6b;
                margin-top: 1rem;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Operación Relámpago</h1>
            <p>El juego se está compilando. Por favor, espera unos momentos...</p>
            <p class="error">Si este mensaje persiste, verifica que el build se haya completado correctamente.</p>
            <p style="font-size: 0.9em; margin-top: 2rem;">Revisa los logs de build en Render para más información.</p>
        </div>
    </body>
    </html>
    """, 503

@app.route('/<path:path>')
def serve_static(path):
    """Sirve archivos estáticos del juego compilado"""
    file_path = os.path.join(BUILD_DIR, path)
    
    # Verificar que el archivo existe y está dentro del directorio de build
    if os.path.exists(file_path) and os.path.commonpath([BUILD_DIR, file_path]) == BUILD_DIR:
        return send_from_directory(BUILD_DIR, path)
    else:
        abort(404)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

