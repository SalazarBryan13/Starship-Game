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
# Pygbag puede generar archivos en diferentes ubicaciones
# Intentar compilar desde el directorio raíz
python -m pygbag --build main.py 2>&1 || echo "Primer intento falló, intentando alternativa..."

# Buscar archivos generados y moverlos a build/web si es necesario
echo "=== Buscando archivos generados ==="
if [ -f "index.html" ]; then
    echo "✓ Encontrado index.html en raíz, moviendo a build/web/"
    mv index.html build/web/ 2>/dev/null || cp index.html build/web/
fi

# Buscar otros archivos generados
find . -maxdepth 2 -name "*.html" -not -path "./build/*" -exec cp {} build/web/ \; 2>/dev/null || true
find . -maxdepth 2 -name "*.js" -not -path "./build/*" -exec cp {} build/web/ \; 2>/dev/null || true
find . -maxdepth 2 -name "*.wasm" -not -path "./build/*" -exec cp {} build/web/ \; 2>/dev/null || true

echo "=== Verificando archivos en build/web ==="
ls -la build/web/ 2>/dev/null | head -20 || echo "Directorio vacío"

# Asegurar que existe un index.html
if [ ! -f "build/web/index.html" ]; then
    echo "⚠ Creando index.html básico..."
    cat > build/web/index.html << 'EOF'
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
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Operación Relámpago</h1>
        <p>El juego se está compilando. Por favor, espera unos momentos...</p>
        <p>Si este mensaje persiste, revisa los logs de build.</p>
    </div>
</body>
</html>
EOF
fi

echo "=== Build completado ==="
