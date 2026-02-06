@echo off
REM Script de build para Windows (alternativa)

echo === Instalando dependencias ===
pip install --upgrade pip
pip install -r requirements.txt

echo === Instalando Pygbag ===
pip install pygbag

echo === Creando directorio de build ===
if not exist "build\web" mkdir build\web

echo === Compilando el juego con Pygbag ===
python -m pygbag --build --template index.html main.py

echo === Build completado ===

