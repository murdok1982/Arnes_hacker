
╔══════════════════════════════════════════════════════════════╗
║                    ARNES HACKER v2.0                         ║
║     Marco de Ciberoperaciones Multi-Agente con IA Local     ║
╚══════════════════════════════════════════════════════════════╝

---

## 📋 Que es?

Un sistema que usa **Inteligencia Artificial local** (Ollama) para automatizar
ciberoperaciones. La IA decide que herramientas usar y las ejecuta por ti,
todo desde una interfaz web estilo Matrix.

## ✅ Requisitos

- Linux (Kali, Parrot, Ubuntu...)
- 4 GB RAM minimo (8 GB+ recomendado)
- Conexion a internet solo para instalar

---

## 🛠️ Los 8 Agentes

| Agente | Funcion |
|--------|---------|
| 🕵️ **RECON** | Descubre puertos y servicios |
| 💥 **EXPLOIT** | Explota vulnerabilidades |
| 🔍 **OSINT** | Busca informacion en redes |
| 🔼 **POST-EXPLOIT** | Escala privilegios |
| 🔀 **PIVOTING** | Movimiento lateral en red |
| 🦠 **MALWARE** | Crea payloads personalizados |
| 🕶️ **UNDERCOVER** | Operaciones anonimas (Tor) |
| 🛡️ **EVASION** | Evita antivirus y deteccion |

---

## 💻 Instalacion (3 pasos)

**Paso 1.** Abre una terminal.

**Paso 2.** Copia y pega:

```bash
git clone https://github.com/murdok1982/Arnes_hacker
cd Arnes_hacker
chmod +x install.sh start.sh
./install.sh
```

**Paso 3.** Cuando termine:

```bash
./start.sh
```

Abre Chrome/Firefox y ve a: **http://localhost:8080**

> ⏳ La primera vez tarda unos minutos descargando el modelo de IA (~4 GB).

---

## 🎮 Como se usa?

1. Se abre una web con estilo Matrix
2. Escribe tu mision en español
3. La IA piensa y ejecuta las herramientas
4. Ves los resultados en tiempo real

**Ejemplos de misiones:**

- `Escanea la IP 192.168.1.1`
- `Compromete example.com`
- `Busca informacion de acme corp`
- `Crea un payload para Windows`
- `Configura Tor y haz todo anonimo`

Tambien puedes usar los botones rapidos para misiones comunes.

---

## ⚡ Modo Shell

Cambia a modo Shell en la web para ejecutar comandos directamente sin IA:

```bash
nmap -sV 192.168.1.1
whois example.com
sqlmap -u 'http://ejemplo.com' --batch
```

---

## ❓ Preguntas Frecuentes

| Problema | Solucion |
|----------|----------|
| "No funciona" | Verifica que Ollama corra: `ollama list` |
| "La IA no responde" | El modelo tarda en cargar la primera vez |
| "Faltan herramientas" | En Kali vienen casi todas. Instala las que falten. |
| "Se ve feo" | Usa Chrome o Firefox moderno |

---

## ⚠️ Aviso

Esta herramienta es para **profesionales de seguridad ofensiva y pentesters
autorizados**. Usala solo en sistemas que te pertenezcan o tengas autorizacion
por escrito para probar. El uso ilegal es responsabilidad tuya.
