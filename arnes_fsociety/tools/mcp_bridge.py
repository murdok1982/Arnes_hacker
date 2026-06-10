"""
MCP Tool Bridge - Integracion de MCP Servers con Deep Agents
Convierte herramientas MCP en herramientas LangChain compatibles
Ejecucion REAL en Docker Sandbox
"""

import asyncio
from typing import Any, Callable, TYPE_CHECKING

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from ..backends.docker_sandbox import DockerSandboxBackend


class MCPToolBridge:
    """
    Bridge para convertir servidores MCP en herramientas LangChain.
    
    Servidores MCP soportados:
    - nmap: Escaneo de red
    - sqlmap: Inyeccion SQL
    - nuclei: Vulnerability scanner
    - metasploit: Framework de explotacion
    - custom: Servidores personalizados
    
    Todas las herramientas ejecutan comandos REALES en el sandbox Docker.
    """
    
    def __init__(
        self,
        mcp_servers: list[dict[str, Any]],
        sandbox: "DockerSandboxBackend | None" = None,
    ):
        self.mcp_servers = mcp_servers
        self.sandbox = sandbox
        self.tools: list[StructuredTool] = []
        self._init_tools()
    
    def set_sandbox(self, sandbox: "DockerSandboxBackend") -> None:
        """Establece el sandbox para ejecucion de herramientas"""
        self.sandbox = sandbox
    
    def _init_tools(self) -> None:
        """Inicializa las herramientas desde los servidores MCP"""
        for server_config in self.mcp_servers:
            server_type = server_config.get("type", "custom")
            
            if server_type == "nmap":
                self.tools.extend(self._create_nmap_tools(server_config))
            elif server_type == "sqlmap":
                self.tools.extend(self._create_sqlmap_tools(server_config))
            elif server_type == "nuclei":
                self.tools.extend(self._create_nuclei_tools(server_config))
            elif server_type == "metasploit":
                self.tools.extend(self._create_metasploit_tools(server_config))
            elif server_type == "custom":
                self.tools.extend(self._create_custom_tools(server_config))
    
    def _execute_in_sandbox(self, command: str) -> str:
        """Ejecuta un comando en el sandbox Docker"""
        if not self.sandbox:
            return f"[ERROR] Sandbox no inicializado. No se puede ejecutar: {command}"
        
        try:
            result = self.sandbox.execute(command)
            return result
        except Exception as e:
            return f"[ERROR] Ejecucion fallida: {str(e)}"
    
    def _create_nmap_tools(self, config: dict[str, Any]) -> list[StructuredTool]:
        """Crea herramientas para Nmap"""
        
        class NmapScanInput(BaseModel):
            target: str = Field(description="IP, rango o dominio a escanear")
            ports: str = Field(default="1-1000", description="Rango de puertos")
            scan_type: str = Field(default="-sV", description="Tipo de escaneo (-sS, -sV, -sC, -A)")
            options: str = Field(default="", description="Opciones adicionales")
        
        async def nmap_scan(target: str, ports: str = "1-1000", scan_type: str = "-sV", options: str = "") -> str:
            cmd = f"nmap {scan_type} -p {ports} {options} {target}".strip()
            return self._execute_in_sandbox(cmd)
        
        class NmapVulnScanInput(BaseModel):
            target: str = Field(description="IP o dominio")
            vuln_scripts: str = Field(default="vuln", description="Scripts de vulnerabilidades")
        
        async def nmap_vuln_scan(target: str, vuln_scripts: str = "vuln") -> str:
            cmd = f"nmap --script={vuln_scripts} {target}".strip()
            return self._execute_in_sandbox(cmd)
        
        return [
            StructuredTool.from_function(
                coroutine=nmap_scan,
                name="nmap_scan",
                description="Escaneo de puertos y servicios con Nmap. Ejecuta nmap real en sandbox Docker.",
                args_schema=NmapScanInput,
            ),
            StructuredTool.from_function(
                coroutine=nmap_vuln_scan,
                name="nmap_vuln_scan",
                description="Escaneo de vulnerabilidades con scripts Nmap. Ejecuta nmap --script real en sandbox.",
                args_schema=NmapVulnScanInput,
            ),
        ]
    
    def _create_sqlmap_tools(self, config: dict[str, Any]) -> list[StructuredTool]:
        """Crea herramientas para SQLMap"""
        
        class SQLMapInput(BaseModel):
            url: str = Field(description="URL con parametro vulnerable (ej: http://target.com/page?id=1)")
            dbms: str = Field(default="", description="Tipo de BD (mysql, postgresql, mssql, oracle)")
            level: int = Field(default=1, description="Nivel de prueba (1-5)")
            risk: int = Field(default=1, description="Nivel de riesgo (1-3)")
        
        async def sqlmap_test(url: str, dbms: str = "", level: int = 1, risk: int = 1) -> str:
            cmd = f"sqlmap -u '{url}' --level={level} --risk={risk} --batch --disable-coloring"
            if dbms:
                cmd += f" --dbms={dbms}"
            return self._execute_in_sandbox(cmd)
        
        return [
            StructuredTool.from_function(
                coroutine=sqlmap_test,
                name="sqlmap_test",
                description="Test de inyeccion SQL con SQLMap. Ejecuta sqlmap real en sandbox Docker.",
                args_schema=SQLMapInput,
            ),
        ]
    
    def _create_nuclei_tools(self, config: dict[str, Any]) -> list[StructuredTool]:
        """Crea herramientas para Nuclei"""
        
        class NucleiInput(BaseModel):
            target: str = Field(description="URL o lista de URLs")
            templates: str = Field(default="", description="Templates a usar (cve, misconfig, etc)")
            severity: str = Field(default="", description="Filtro por severidad (low, medium, high, critical)")
        
        async def nuclei_scan(target: str, templates: str = "", severity: str = "") -> str:
            cmd = f"nuclei -u {target} -silent"
            if templates:
                cmd += f" -t {templates}"
            if severity:
                cmd += f" -severity {severity}"
            return self._execute_in_sandbox(cmd)
        
        return [
            StructuredTool.from_function(
                coroutine=nuclei_scan,
                name="nuclei_scan",
                description="Escaneo de vulnerabilidades con Nuclei. Ejecuta nuclei real en sandbox Docker.",
                args_schema=NucleiInput,
            ),
        ]
    
    def _create_metasploit_tools(self, config: dict[str, Any]) -> list[StructuredTool]:
        """Crea herramientas para Metasploit"""
        
        class MetasploitInput(BaseModel):
            exploit: str = Field(description="Nombre del exploit (ej: exploit/multi/handler)")
            payload: str = Field(description="Payload a usar (ej: windows/meterpreter/reverse_tcp)")
            rhosts: str = Field(description="Host(s) objetivo")
            lhost: str = Field(default="", description="Host local para reverse shell")
            lport: int = Field(default=4444, description="Puerto local para reverse shell")
        
        async def metasploit_run(
            exploit: str,
            payload: str,
            rhosts: str,
            lhost: str = "",
            lport: int = 4444,
        ) -> str:
            msf_cmd = f"use {exploit}; set RHOSTS {rhosts}; set PAYLOAD {payload}"
            if lhost:
                msf_cmd += f"; set LHOST {lhost}"
            msf_cmd += f"; set LPORT {lport}; run -j"
            cmd = f'msfconsole -q -x "{msf_cmd}"'
            return self._execute_in_sandbox(cmd)
        
        class MetasploitSearchInput(BaseModel):
            query: str = Field(description="Busqueda (ej: type:exploit platform:windows)")
        
        async def metasploit_search(query: str) -> str:
            cmd = f'msfconsole -q -x "search {query}; exit -y"'
            return self._execute_in_sandbox(cmd)
        
        return [
            StructuredTool.from_function(
                coroutine=metasploit_run,
                name="metasploit_run",
                description="Ejecuta un exploit de Metasploit. Ejecuta msfconsole real en sandbox Docker.",
                args_schema=MetasploitInput,
            ),
            StructuredTool.from_function(
                coroutine=metasploit_search,
                name="metasploit_search",
                description="Busca exploits/modulos en Metasploit. Ejecuta msfconsole real en sandbox.",
                args_schema=MetasploitSearchInput,
            ),
        ]
    
    def _create_custom_tools(self, config: dict[str, Any]) -> list[StructuredTool]:
        """Crea herramientas personalizadas"""
        tools = []
        
        for tool_config in config.get("tools", []):
            name = tool_config.get("name", "custom_tool")
            description = tool_config.get("description", "Herramienta personalizada")
            command_template = tool_config.get("command", "")
            
            class CustomToolInput(BaseModel):
                params: dict[str, str] = Field(default={}, description="Parametros para el template del comando")
            
            async def custom_tool(params: dict[str, str] = {}, command_template: str = command_template) -> str:
                try:
                    cmd = command_template.format(**params)
                except KeyError as e:
                    return f"[ERROR] Parametro faltante: {e}"
                return self._execute_in_sandbox(cmd)
            
            tools.append(
                StructuredTool.from_function(
                    coroutine=custom_tool,
                    name=name,
                    description=f"{description}. Ejecuta comando real en sandbox Docker.",
                    args_schema=CustomToolInput,
                )
            )
        
        return tools
    
    def get_tools(self) -> list[StructuredTool]:
        """Retorna todas las herramientas disponibles"""
        return self.tools
