#!/bin/bash
# Script de build para compilar el juego con Pygbag

set -e

echo "=== Instalando dependencias ==="
pip install --upgrade pip
pip install -r requirements.txt

echo "=== Instalando Pygbag ==="
pip install pygbag

echo "=== Creando directorio de build ==="
mkdir -p build/web

echo "=== Compilando el juego con Pygbag ==="
# Pygbag compila el juego a WebAssembly
python -m pygbag --build --template index.html main.py

echo "=== Verificando archivos generados ==="
if [ -d "build/web" ]; then
    echo "✓ Directorio build/web creado"
    ls -la build/web/ | head -20
else
    echo "⚠ Advertencia: build/web no encontrado, creando estructura básica..."
    mkdir -p build/web
fi

echo "=== Build completado ==="

