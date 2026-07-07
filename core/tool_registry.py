import shutil


class ToolDefinition:
    def __init__(self, name: str, description: str, command_template: str, category: str, required: bool = False):
        self.name = name
        self.description = description
        self.command_template = command_template
        self.category = category
        self.required = required

    def available(self) -> bool:
        tool_name = self.command_template.split()[0]
        return shutil.which(tool_name) is not None

    def build_command(self, **kwargs) -> str:
        return self.command_template.format(**kwargs)


_TOOLS: list[ToolDefinition] = [
    ToolDefinition("nmap_scan", "Escaneo de puertos y servicios", "nmap -sV -sC -T4 -A {target}", "recon", True),
    ToolDefinition("nmap_full", "Escaneo completo todos los puertos", "nmap -p- -sV -T4 {target}", "recon", True),
    ToolDefinition("nmap_vuln", "Escaneo de vulnerabilidades NSE", "nmap --script=vuln -sV {target}", "recon", True),
    ToolDefinition("nmap_os", "Deteccion de sistema operativo", "nmap -O -sV {target}", "recon", True),
    ToolDefinition("masscan", "Escaneo masivo de puertos", "masscan {target} -p1-65535 --rate=1000", "recon"),
    ToolDefinition("dnsrecon", "Reconocimiento DNS", "dnsrecon -d {target}", "recon"),
    ToolDefinition("dnsenum", "Enumeracion DNS", "dnsenum {target}", "recon"),
    ToolDefinition("gobuster_dirs", "Fuerza bruta de directorios web", "gobuster dir -u {url} -w /usr/share/wordlists/dirb/common.txt", "recon"),
    ToolDefinition("gobuster_dns", "Fuerza bruta de subdominios", "gobuster dns -d {domain} -w /usr/share/wordlists/dirb/common.txt", "recon"),
    ToolDefinition("ffuf", "Fuzzing web rapido", "ffuf -u {url}/FUZZ -w /usr/share/wordlists/dirb/common.txt", "recon"),
    ToolDefinition("nikto", "Escaneo de vulnerabilidades web", "nikto -h {target}", "recon", True),
    ToolDefinition("theharvester", "Recoleccion de emails/subdominios", "theHarvester -d {domain} -b all", "osint"),
    ToolDefinition("whatweb", "Deteccion de tecnologias web", "whatweb {target}", "recon"),
    ToolDefinition("wpscan", "Escaneo de WordPress", "wpscan --url {url} --no-update", "exploit"),
    ToolDefinition("sqlmap", "SQL injection automation", "sqlmap -u '{url}' --batch --random-agent", "exploit", True),
    ToolDefinition("sqlmap_db", "SQL injection con dump de DB", "sqlmap -u '{url}' --batch --random-agent --dump", "exploit"),
    ToolDefinition("hydra_ssh", "Fuerza bruta SSH", "hydra -l {user} -P {wordlist} ssh://{target}", "exploit"),
    ToolDefinition("hydra_ftp", "Fuerza bruta FTP", "hydra -l {user} -P {wordlist} ftp://{target}", "exploit"),
    ToolDefinition("hydra_http_post", "Fuerza bruta HTTP POST", "hydra -l {user} -P {wordlist} {target} http-post-form '{path}:{params}:{fail}'", "exploit"),
    ToolDefinition("john", "Cracking de hashes", "john --wordlist={wordlist} {hash_file}", "exploit"),
    ToolDefinition("hashcat", "Cracking de hashes con GPU", "hashcat -m {mode} -a 0 {hash_file} {wordlist}", "exploit"),
    ToolDefinition("searchsploit", "Busqueda de exploits", "searchsploit {query}", "exploit", True),
    ToolDefinition("nuclei", "Escaneo de vulnerabilidades con templates", "nuclei -u {target} -severity low,medium,high,critical", "exploit"),
    ToolDefinition("metasploit_search", "Busqueda en Metasploit", "msfconsole -q -x 'search {query}; exit'", "exploit", True),
    ToolDefinition("msfvenom", "Generacion de payloads", "msfvenom -p {payload} LHOST={lhost} LPORT={lport} -f {format} -o {output}", "malware", True),
    ToolDefinition("proxychains", "Ejecutar comando via proxy", "proxychains {command}", "pivoting"),
    ToolDefinition("ncat", "Netcat para reverse shells", "ncat -lvnp {port}", "exploit"),
    ToolDefinition("socat", "Socat para port forwarding", "socat TCP-LISTEN:{lport},reuseaddr,fork TCP:{target}:{rport}", "pivoting"),
    ToolDefinition("sshuttle", "VPN over SSH", "sshuttle -r {user}@{target} {subnet}", "pivoting"),
    ToolDefinition("chisel_client", "Cliente Chisel para tunel", "chisel client {lhost}:{lport} R:{rport}:{target}:{rport2}", "pivoting"),
    ToolDefinition("chisel_server", "Servidor Chisel", "chisel server -p {port} --reverse", "pivoting"),
    ToolDefinition("macchanger", "Cambiar MAC address", "macchanger -r {interface}", "undercover"),
    ToolDefinition("tor", "Iniciar/verificar Tor", "systemctl status tor 2>/dev/null || tor --version", "undercover"),
    ToolDefinition("steghide", "Esteganografia en imagenes", "steghide {action} -sf {file}", "undercover"),
    ToolDefinition("curl_anon", "Solicitud HTTP anonima (Tor)", "curl --socks5-hostname 127.0.0.1:9050 {url}", "undercover"),
    ToolDefinition("upx", "Comprimir/Ofuscar binarios", "upx {file} -o {output}", "evasion"),
]

CATEGORY_NAMES = {
    "recon": "Reconocimiento",
    "exploit": "Explotacion",
    "osint": "OSINT",
    "post_exploit": "Post-Explotacion",
    "pivoting": "Pivoting",
    "malware": "Malware",
    "undercover": "Undercover",
    "evasion": "Evasion",
    "general": "General",
}


class ToolRegistry:
    REGISTRY: list[ToolDefinition] = _TOOLS

    def get_by_category(self, category: str) -> list[ToolDefinition]:
        if category == "all":
            return self.REGISTRY
        return [t for t in self.REGISTRY if t.category == category]

    def get(self, name: str) -> ToolDefinition | None:
        for t in self.REGISTRY:
            if t.name == name:
                return t
        return None

    def available(self) -> list[ToolDefinition]:
        return [t for t in self.REGISTRY if t.available()]

    def missing_critical(self) -> list[str]:
        return [t.name for t in self.REGISTRY if t.required and not t.available()]

    @property
    def total(self) -> int:
        return len(self.REGISTRY)

    @property
    def available_count(self) -> int:
        return len(self.available())

    @property
    def categories(self) -> list[str]:
        return list(dict.fromkeys(t.category for t in self.REGISTRY))


tool_registry = ToolRegistry()

REVERSE_CATEGORIES = CATEGORY_NAMES
TOOL_REGISTRY = _TOOLS


def get_tools_by_category(category: str) -> list[ToolDefinition]:
    return tool_registry.get_by_category(category)


def get_tool(name: str) -> ToolDefinition | None:
    return tool_registry.get(name)


def get_available_tools() -> list[ToolDefinition]:
    return tool_registry.available()


def check_critical_tools() -> list[str]:
    return tool_registry.missing_critical()
