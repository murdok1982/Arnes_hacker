#!/bin/bash
set -euo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'

echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════╗"
echo "║     ARNES HACKER v2.0 - Instalador           ║"
echo "╚══════════════════════════════════════════════╝"
echo -e "${NC}"

# Verificar OS
echo -e "${YELLOW}[+]${NC} Verificando sistema operativo..."
if [ ! -f /etc/os-release ]; then
    echo -e "${RED}[!]${NC} Este instalador requiere Linux (Kali/Parrot/Debian/Ubuntu)"
    exit 1
fi
. /etc/os-release
echo -e "${GREEN}[+]${NC} Sistema: $PRETTY_NAME"

# Verificar Python 3.11+
echo -e "${YELLOW}[+]${NC} Verificando Python..."
if ! command -v python3 &>/dev/null; then
    echo -e "${RED}[!]${NC} Python 3 no encontrado. Instalando..."
    sudo apt-get update -qq && sudo apt-get install -y -qq python3 python3-pip python3-venv
fi
PYVER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo -e "${GREEN}[+]${NC} Python $PYVER detectado"

# Verificar/Instalar git
if ! command -v git &>/dev/null; then
    echo -e "${YELLOW}[+]${NC} Instalando git..."
    sudo apt-get install -y -qq git
fi

# Verificar/Instalar Ollama
if ! command -v ollama &>/dev/null; then
    echo -e "${YELLOW}[+]${NC} Instalando Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh
    echo -e "${GREEN}[+]${NC} Ollama instalado. Iniciando servidor..."
    ollama serve >/dev/null 2>&1 &
    sleep 2
else
    echo -e "${GREEN}[+]${NC} Ollama ya instalado"
    if ! curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
        echo -e "${YELLOW}[+]${NC} Iniciando Ollama..."
        ollama serve >/dev/null 2>&1 &
        sleep 2
    fi
fi

# Detectar hardware y sugerir modelo
echo -e "${YELLOW}[+]${NC} Detectando hardware..."
GPU_MEM=0
if command -v nvidia-smi &>/dev/null; then
    GPU_MEM=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits 2>/dev/null | head -1 | tr -d ' ')
    if [ -n "$GPU_MEM" ]; then GPU_MEM=$((GPU_MEM/1024)); fi
    echo -e "${GREEN}[+]${NC} GPU NVIDIA detectada: ${GPU_MEM}GB VRAM"
elif command -v rocm-smi &>/dev/null; then
    echo -e "${GREEN}[+]${NC} GPU AMD ROCm detectada"
    GPU_MEM=$(rocm-smi --showmeminfo vram 2>/dev/null | grep "VRAM Total" | grep -oP '\d+' | head -1)
    if [ -n "$GPU_MEM" ]; then GPU_MEM=$((GPU_MEM/1024)); fi
fi

TOTAL_RAM=$(free -g | awk '/^Mem:/{print $2}')
echo -e "${GREEN}[+]${NC} RAM total: ${TOTAL_RAM}GB"

# Elegir modelo
SUGGESTED="qwen2.5-coder:7b"
if [ "$GPU_MEM" -ge 24 ]; then SUGGESTED="qwen2.5-coder:32b"
elif [ "$GPU_MEM" -ge 16 ]; then SUGGESTED="qwen2.5-coder:14b"
elif [ "$GPU_MEM" -ge 8 ]; then SUGGESTED="qwen2.5-coder:14b"
elif [ "$GPU_MEM" -ge 4 ]; then SUGGESTED="qwen2.5-coder:7b"
elif [ "$TOTAL_RAM" -ge 32 ]; then SUGGESTED="qwen2.5-coder:7b"
elif [ "$TOTAL_RAM" -ge 16 ]; then SUGGESTED="qwen2.5-coder:7b-q4_K_M"
else SUGGESTED="qwen2.5-coder:7b-q4_K_M"
fi

echo ""
echo -e "${CYAN}Modelo recomendado para tu hardware: ${SUGGESTED}${NC}"
read -p "Presiona Enter para aceptar o escribe otro modelo (ej: deepseek-coder:6.7b): " MODEL_INPUT
MODEL=${MODEL_INPUT:-$SUGGESTED}
echo -e "${GREEN}[+]${NC} Modelo seleccionado: $MODEL"

# Descargar modelo
echo -e "${YELLOW}[+]${NC} Descargando modelo $MODEL (esto puede tomar varios minutos)..."
ollama pull "$MODEL"
echo -e "${GREEN}[+]${NC} Modelo $MODEL listo"

# Crear entorno virtual e instalar dependencias Python
echo -e "${YELLOW}[+]${NC} Creando entorno virtual Python..."
if [ -d "venv" ]; then rm -rf venv; fi
python3 -m venv venv
source venv/bin/activate
echo -e "${GREEN}[+]${NC} Entorno virtual creado"

echo -e "${YELLOW}[+]${NC} Instalando dependencias Python..."
pip install -q -r requirements.txt
echo -e "${GREEN}[+]${NC} Dependencias instaladas"

# Crear directorios necesarios
mkdir -p memory output

# Verificar herramientas de hacking esenciales
echo -e "${YELLOW}[+]${NC} Verificando herramientas de hacking..."
MISSING=""
for tool in nmap sqlmap msfconsole hydra gobuster nikto whatweb dnsrecon searchsploit masscan john hashcat theharvester proxychains ncat socat macchanger; do
    if command -v $tool &>/dev/null; then
        echo -e "  ${GREEN}[+]${NC} $tool"
    else
        echo -e "  ${YELLOW}[!]${NC} $tool (NO INSTALADO)"
        MISSING="$MISSING $tool"
    fi
done

if [ -n "$MISSING" ]; then
    echo ""
    echo -e "${YELLOW}[!]${NC} Algunas herramientas no estan instaladas."
    read -p "   Instalar todas con apt? (s/n): " INSTALL_TOOLS
    if [ "$INSTALL_TOOLS" = "s" ]; then
        echo -e "${YELLOW}[+]${NC} Instalando herramientas faltantes..."
        sudo apt-get update -qq
        sudo apt-get install -y -qq $MISSING 2>/dev/null || echo -e "${RED}[!]${NC} Algunas herramientas no estan disponibles en apt"
    fi
fi

# Configurar .env si no existe
if [ ! -f ".env" ]; then
    cp .env.example .env 2>/dev/null || true
    if [ -f ".env" ]; then
        sed -i "s/OLLAMA_MODEL=.*/OLLAMA_MODEL=$MODEL/" .env
        echo -e "${GREEN}[+]${NC} Archivo .env creado"
    fi
fi

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║     ARNES HACKER v2.0                        ║${NC}"
echo -e "${GREEN}║     Instalacion completada                    ║${NC}"
echo -e "${GREEN}║                                              ║${NC}"
echo -e "${GREEN}║     Para iniciar:                             ║${NC}"
echo -e "${GREEN}║       source venv/bin/activate                ║${NC}"
echo -e "${GREEN}║       python -m server.main                   ║${NC}"
echo -e "${GREEN}║                                              ║${NC}"
echo -e "${GREEN}║     O simplemente:                            ║${NC}"
echo -e "${GREEN}║       ./start.sh                              ║${NC}"
echo -e "${GREEN}║                                              ║${NC}"
echo -e "${GREEN}║     Abre http://localhost:8080                 ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════╝${NC}"
