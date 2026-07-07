#!/bin/bash
set -euo pipefail

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'

echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════╗"
echo "║     ARNES HACKER v2.0                        ║"
echo "╚══════════════════════════════════════════════╝"
echo -e "${NC}"

# Activar entorno virtual
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [ ! -d "venv" ]; then
    echo -e "${YELLOW}[!]${NC} Entorno virtual no encontrado."
    echo -e "${YELLOW}[!]${NC} Ejecuta primero: ./install.sh"
    exit 1
fi
source venv/bin/activate

# Verificar Ollama
echo -e "${YELLOW}[+]${NC} Verificando Ollama..."
if ! command -v ollama &>/dev/null; then
    echo -e "${RED}[!]${NC} Ollama no instalado. Ejecuta: ./install.sh"
    exit 1
fi

if ! curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
    echo -e "${YELLOW}[+]${NC} Iniciando Ollama..."
    ollama serve >/dev/null 2>&1 &
    sleep 3
fi
echo -e "${GREEN}[+]${NC} Ollama listo"

# Mostrar modelo actual
MODEL=$(grep OLLAMA_MODEL .env 2>/dev/null | cut -d= -f2 || echo "default")
echo -e "${GREEN}[+]${NC} Modelo: $MODEL"

# Iniciar servidor web
echo -e "${GREEN}[+]${NC} Servidor web: http://localhost:8080"
echo -e "${GREEN}[+]${NC} Presiona Ctrl+C para detener"
echo ""
python -m server.main
