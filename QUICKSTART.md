# ARNES FSOCIETY - Guia de Inicio Rapido

## Instalacion en 5 minutos

### 1. Verificar requisitos

```bash
# Python 3.11+
python --version

# Ollama
ollama --version

# Docker
docker --version
```

### 2. Instalar dependencias

```bash
cd "D:\Arnes para windows potente\arnes-fsociety"

# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -e .

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

### 3. Verificar modelo fsociety

```bash
ollama list
# Debe mostrar: fsociety:latest

# Si no esta:
ollama pull fsociety
```

### 4. Construir sandbox Docker

```bash
docker build -t fsociety-sandbox ./sandbox
```

### 5. Configurar entorno

```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

### 6. Test rapido

```bash
python test_arnes.py
```

## Primera Mision

### Mision de prueba (sin sandbox)

```bash
python main.py --mission "Listar los subagentes disponibles y sus capacidades"
```

### Mision con sandbox

```bash
python main.py --mission "Realizar reconocimiento basico de example.com" --sandbox
```

### Mision completa

```bash
python main.py --mission "Operacion completa contra target.com: reconocimiento, identificacion de vulnerabilidades, y reporte" --sandbox --output ./resultados
```

## Comandos utiles

```bash
# Listar subagentes
python main.py --list-agents

# Listar skills
python main.py --list-skills

# Modo verbose
python main.py --mission "Tu mision" --verbose

# Modo async
python main.py --mission "Tu mision" --async
```

## Estructura de una mision

1. **Planificacion**: El orquestador analiza la mision
2. **Reconocimiento**: Delega a RECON
3. **Analisis**: Evalua resultados
4. **Explotacion**: Delega a EXPLOIT (si aplica)
5. **Post-Explotacion**: Delega a POST-EX (si aplica)
6. **Reporte**: Genera informe final

## Troubleshooting

### Ollama no conecta

```bash
# Iniciar Ollama
ollama serve

# En otra terminal:
ollama list
```

### Docker no inicia

```bash
# Verificar Docker Desktop (Windows/Mac)
# O servicio Docker (Linux)
sudo systemctl start docker
```

### Error de importaciones

```bash
# Reinstalar
pip uninstall arnes-fsociety
pip install -e .
```

## Siguientes pasos

1. **Personalizar prompts**: Edita `prompts/orchestrator.txt`
2. **Agregar skills**: Crea nuevas skills en `skills/`
3. **Configurar MCP**: Edita `mcp_config.yml`
4. **Auto-mejora**: Configura `better_harness/config.toml`

## Documentacion completa

Ver `README.md` para documentacion detallada.

---

**FSOCIETY STATE DIVISION**
