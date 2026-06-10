#!/bin/bash

# ARNES FSOCIETY - Script de Instalacion
# Sistema de Ciberguerra Estatal

set -e

echo "=========================================="
echo "  ARNES FSOCIETY - Instalacion"
echo "=========================================="
echo ""

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 no encontrado"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "[+] Python version: $PYTHON_VERSION"

# Verificar Ollama
if ! command -v ollama &> /dev/null; then
    echo "[WARNING] Ollama no encontrado. Instalar desde: https://ollama.com"
else
    echo "[+] Ollama encontrado"
fi

# Verificar Docker
if ! command -v docker &> /dev/null; then
    echo "[WARNING] Docker no encontrado. Instalar desde: https://docker.com"
else
    echo "[+] Docker encontrado"
fi

# Crear entorno virtual
echo ""
echo "[+] Creando entorno virtual..."
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
echo "[+] Instalando dependencias..."
pip install --upgrade pip
pip install -e .

# Verificar modelo fsociety
echo ""
echo "[+] Verificando modelo fsociety..."
if ollama list | grep -q "fsociety"; then
    echo "[+] Modelo fsociety encontrado"
else
    echo "[WARNING] Modelo fsociety no encontrado en Ollama"
    echo "    Ejecutar: ollama pull fsociety"
fi

# Construir imagen Docker del sandbox
echo ""
echo "[+] Construyendo imagen Docker del sandbox..."
if command -v docker &> /dev/null; then
    docker build -t fsociety-sandbox ./sandbox
    echo "[+] Imagen fsociety-sandbox construida"
else
    echo "[WARNING] Docker no disponible, omitiendo construccion de sandbox"
fi

# Crear directorios
echo "[+] Creando directorios..."
mkdir -p output
mkdir -p memory
mkdir -p logs

# Copiar .env.example a .env si no existe
if [ ! -f .env ]; then
    cp .env.example .env
    echo "[+] Archivo .env creado desde .env.example"
fi

echo ""
echo "=========================================="
echo "  INSTALACION COMPLETADA"
echo "=========================================="
echo ""
echo "Proximos pasos:"
echo "  1. Activar entorno virtual: source venv/bin/activate"
echo "  2. Configurar .env con tus valores"
echo "  3. Iniciar Ollama: ollama serve"
echo "  4. Ejecutar: python main.py --list-agents"
echo "  5. Ejecutar mision: python main.py --mission 'Tu mision aqui' --sandbox"
echo ""
echo "Documentacion: Ver README.md"
echo ""
