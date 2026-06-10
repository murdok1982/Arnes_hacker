<div align="center">

# 🎭 ARNES FSOCIETY
### El Arnes de Ciberguerra Estatal Definitivo

![Version](https://img.shields.io/badge/version-0.1.0-red?style=for-the-badge&logo=hackaday)
![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Kali_Linux-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![License](https://img.shields.io/badge/License-STATE_USE_ONLY-black?style=for-the-badge)

**🔥 Red Team Automation | Ciberguerra | Guerra Hibrida | APT Simulation 🔥**

*Sistema estatal de operaciones ofensivas con IA local, 5 subagentes especializados y sandbox Docker con Kali Linux*

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/murdok1982)

</div>

---

## 🎯 ¿QUE ES ARNES FSOCIETY?

**ARNES FSOCIETY** es un sistema de automatizacion de operaciones de Red Team y Ciberguerra de nivel estatal. Construido sobre **Deep Agents** de LangChain, integra un LLM local fine-tuneado (**fsociety**) con 5 subagentes especializados que ejecutan operaciones ofensivas reales en un sandbox Docker con Kali Linux.

### 🚀 Capacidades Reales

- **🔍 Reconocimiento Avanzado**: Nmap, masscan, DNS enumeration, fingerprinting, WAF detection
- **💥 Explotacion**: SQLMap, Metasploit, Nuclei, weaponization de payloads
- **🕵️ OSINT**: Brechas de datos, geolocalizacion, analisis de redes sociales, inteligencia multi-fuente
- **🔓 Post-Explotacion**: Escalada de privilegios, persistencia, movimiento lateral, exfiltracion
- **⚔️ Ciberguerra**: APT simulation, campañas sostenidas, ataques a infraestructura critica, PSYOPS

---

## 🏗️ ARQUITECTURA

```
┌─────────────────────────────────────────────────────────┐
│              ORQUESTADOR CENTRAL (Deep Agent)            │
│  LLM: fsociety (modelo local fine-tuneado via Ollama)   │
│  Prompt raiz: Identidad + Reglas de Engagement          │
└──────────────┬──────────────────────────────────────────┘
               │
    ┌──────────┼──────────┬──────────────┐
    ▼          ▼          ▼              ▼
[RECON]    [EXPLOIT]   [OSINT]      [POST-EX]
SubAgente  SubAgente   SubAgente    SubAgente
    │          │          │              │
    └──────────┴──────────┴──────────────┘
               │
    ┌──────────┼──────────┐
    ▼          ▼          ▼
[TOOLS]    [MEMORY]   [SANDBOX]
MCP Servers SQLite    Docker Kali
            Store     Linux
```

---

## 🛠️ TECNOLOGIAS

| Componente | Tecnologia |
|------------|------------|
| **LLM** | fsociety (Gemma 4 E4B fine-tuned) via Ollama |
| **Framework** | Deep Agents (LangChain/LangGraph) |
| **Sandbox** | Docker con Kali Linux rolling |
| **Memoria** | SQLite persistente |
| **Herramientas** | Nmap, SQLMap, Nuclei, Metasploit, Impacket |
| **Lenguaje** | Python 3.11+ |

---

## 📦 INSTALACION

### Requisitos

- Python 3.11+
- Ollama (con modelo fsociety)
- Docker Desktop
- uv (gestor de paquetes)

### Instalacion Rapida

```bash
# Clonar repositorio
git clone https://github.com/murdok1982/Arnes_hacker.git
cd Arnes_hacker

# Instalar dependencias
uv sync

# Verificar instalacion
uv run python test_arnes.py
```

### Configuracion

```bash
# Copiar archivo de entorno
cp .env.example .env

# Editar .env con tus valores
# OLLAMA_BASE_URL=http://localhost:11434
# OLLAMA_MODEL=fsociety

# Construir imagen Docker del sandbox
docker build -t fsociety-sandbox ./sandbox
```

---

## 🚀 USO

### Listar Subagentes

```bash
uv run python main.py --list-agents
```

### Ejecutar Mision

```bash
# Mision basica
uv run python main.py --mission "Realizar reconocimiento de target.com"

# Con sandbox habilitado
uv run python main.py --mission "Explotar vulnerabilidad en 192.168.1.100" --sandbox

# Modo async
uv run python main.py --mission "OSINT sobre organizacion ACME" --async
```

### Ejemplos de Misiones

#### 🔍 Reconocimiento
```bash
uv run python main.py --mission "Realizar escaneo completo de puertos y servicios en example.com, identificar tecnologias web y posibles vectores de ataque" --sandbox
```

#### 💥 Explotacion
```bash
uv run python main.py --mission "Explotar vulnerabilidad SQL injection en http://target.com/login.php y obtener acceso a la base de datos" --sandbox
```

#### 🕵️ OSINT
```bash
uv run python main.py --mission "Recopilar inteligencia sobre la organizacion ACME Corp: empleados clave, infraestructura tecnologica, brechas de datos conocidas" --sandbox
```

#### 🔓 Post-Explotacion
```bash
uv run python main.py --mission "Realizar escalada de privilegios en el sistema comprometido 192.168.1.100, establecer persistencia y mapear red interna" --sandbox
```

---

## 🎭 SUBAGENTES ESPECIALIZADOS

### 1. RECON - Reconocimiento
- **Nmap**: Escaneo de puertos, deteccion de servicios, OS fingerprinting
- **Masscan**: Escaneo ultrarapido de rangos IP
- **DNS Enumeration**: Subdominios, registros DNS, zone transfer
- **Fingerprinting**: HTTP Headers, SSL/TLS, Service Banners, WAF Detection

### 2. EXPLOIT - Explotacion
- **SQLMap**: Inyeccion SQL automatizada (MySQL, PostgreSQL, MSSQL, Oracle)
- **Metasploit**: Framework de explotacion modular
- **Nuclei**: Vulnerability scanner con templates
- **Weaponization**: msfvenom, custom shells, obfuscation

### 3. OSINT - Inteligencia
- **Social Media**: LinkedIn, Twitter/X, Facebook, Instagram
- **Email Enumeration**: Hunter.io, breach databases
- **Geolocalizacion**: GPS de fotos, landmarks, satellite imagery
- **Breach Data**: HaveIBeenPwned, DeHashed, Intelligence X

### 4. POST-EX - Post-Explotacion
- **Escalada Linux**: SUID/SGID, sudo misconfigurations, kernel exploits
- **Escalada Windows**: Token impersonation, service misconfigurations, UAC bypass
- **Movimiento Lateral**: Pass-the-Hash, WMI/WinRM, SSH key reuse
- **Persistencia**: Crontab, systemd service, registry Run keys

### 5. CYBER - Ciberguerra
- **APT Simulation**: TTP mapping (MITRE ATT&CK), custom malware, C2 infrastructure
- **Campañas Sostenidas**: Multi-vector attacks, persistence layers, dwell time
- **Infraestructura Critica**: SCADA/ICS, power grid, telecommunications
- **PSYOPS**: Narrative operations, deepfake generation, leak operations

---

## 🛡️ HERRAMIENTAS MCP

| Herramienta | Descripcion |
|-------------|-------------|
| `nmap_scan` | Escaneo de puertos y servicios con Nmap |
| `nmap_vuln_scan` | Escaneo de vulnerabilidades con scripts Nmap |
| `sqlmap_test` | Inyeccion SQL automatizada con SQLMap |
| `nuclei_scan` | Vulnerability scanner con templates |
| `metasploit_run` | Ejecucion de exploits de Metasploit |
| `metasploit_search` | Busqueda de modulos en Metasploit |

**Todas las herramientas ejecutan comandos REALES en el sandbox Docker con Kali Linux**

---

## 🧠 MEMORIA PERSISTENTE

El sistema almacena conocimiento de operaciones anteriores:

- **Operaciones**: Historial completo de misiones
- **IoCs**: Indicadores de Compromiso descubiertos
- **Tecnicas**: Metodos exitosos con tasa de exito
- **Lecciones Aprendidas**: Conocimiento acumulado
- **Knowledge Base**: Almacen generico key-value

---

## 📁 ESTRUCTURA DEL PROYECTO

```
arnes-fsociety/
├── arnes_fsociety/           # Paquete principal
│   ├── core.py              # Core del arnes
│   ├── subagents/           # 5 subagentes especializados
│   │   ├── recon.py        # Reconocimiento
│   │   ├── exploit.py      # Explotacion
│   │   ├── osint.py        # OSINT
│   │   ├── post_exploit.py # Post-Explotacion
│   │   └── cyber_warfare.py# Ciberguerra
│   ├── backends/
│   │   └── docker_sandbox.py  # Sandbox Docker
│   ├── memory/
│   │   ├── state_store.py     # Memoria persistente
│   │   └── AGENTS.md          # Memoria de operaciones
│   └── tools/
│       └── mcp_bridge.py      # Bridge MCP
│
├── main.py                   # Entry point CLI
├── test_arnes.py             # Test de componentes
├── pyproject.toml            # Dependencias
├── docker-compose.yml        # Orquestacion Docker
├── mcp_config.yml            # Configuracion MCP
│
├── prompts/
│   └── orchestrator.txt      # Prompt raiz del orquestador
│
├── skills/                   # Skills reutilizables
│   ├── nmap-recon/SKILL.md
│   ├── sqlmap-exploit/SKILL.md
│   └── metasploit-exploit/SKILL.md
│
├── sandbox/
│   └── Dockerfile            # Imagen Kali Linux
│
└── output/                   # Resultados de operaciones
```

---

## ⚠️ REGLAS DE ENGAGEMENT

1. **Autorizacion**: Toda operacion requiere autorizacion explicita
2. **Scope**: Respeta estrictamente el scope definido
3. **Documentacion**: Cada accion debe ser documentada
4. **Stealth**: Prioriza operaciones sigilosas cuando sea requerido
5. **Safety**: Payloads destructivos requieren doble confirmacion

---

## 🔒 SEGURIDAD

- **Sandbox Aislado**: Todos los payloads se ejecutan en Docker
- **Checkpointer**: MemorySaver para interrupt_on
- **Permisos**: FilesystemPermission para control de acceso
- **Memoria Segura**: SQLite con validacion de inputs

---

## 📊 TESTING

```bash
# Ejecutar tests de componentes
uv run python test_arnes.py
```

**Tests incluidos:**
- Imports de modulos
- Verificacion de Ollama
- Verificacion de Docker
- APIs de backends
- Herramientas MCP
- Memoria persistente
- Creacion del arnes

---

## 🎓 DOCUMENTACION

- [ESTADO_PROYECTO.md](ESTADO_PROYECTO.md) - Estado tecnico detallado
- [AUDITORIA_FINAL.md](AUDITORIA_FINAL.md) - Auditoria completa
- [QUICKSTART.md](QUICKSTART.md) - Guia de inicio rapido

---

## 🤝 CONTRIBUCIONES

Este es un proyecto estatal de uso restringido. Para contribuciones autorizadas:

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

---

## 📜 LICENCIA

Este proyecto es propiedad del Estado. Uso restringido a operaciones autorizadas.

**ADVERTENCIA**: El uso no autorizado de este sistema constituye un delito. Toda operacion requiere autorizacion explicita del propietario del sistema objetivo.

---

## 🙏 AGRADECIMIENTOS

- **LangChain** - Por Deep Agents y el ecosistema de agentes
- **Ollama** - Por hacer posible LLMs locales
- **Kali Linux** - Por las herramientas ofensivas
- **Docker** - Por el sandboxing

---

## 📞 CONTACTO

**Autor**: murdok1982  
**GitHub**: [@murdok1982](https://github.com/murdok1982)  
**Proyectos Relacionados**:
- [NEXUS-OPS](https://github.com/murdok1982/NEXUS-OPS) - Plataforma de Operaciones Ofensivas
- [Global-Intelligence](https://github.com/murdok1982/Global-Intelligence) - Inteligencia Global con IA
- [fsociety](https://github.com/murdok1982/fsociety) - Modelo LLM fine-tuned

---

<div align="center">

## ☕ Apoya este proyecto

Mantener este proyecto y todos los demas lleva muchas horas. Si te ha sido util o simplemente te gusta lo que hago, puedes invitarme a un cafe:

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/murdok1982)

Cada contribucion va directamente a seguir creando mas codigo open-source.

**🔥 FSOCIETY STATE DIVISION 🔥**  
*Sistema de Ciberguerra Estatal v0.1.0*

</div>
