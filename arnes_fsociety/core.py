"""
ARNES FSOCIETY - Sistema de Ciberguerra Estatal
Arnes de Red Team Automation con Deep Agents + LLM Local
"""

import os
from pathlib import Path
from typing import Any

from deepagents import (
    create_deep_agent,
    SubAgent,
    FilesystemMiddleware,
    FilesystemPermission,
    MemoryMiddleware,
)
from deepagents.backends import StateBackend, CompositeBackend, FilesystemBackend
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage
from langgraph.checkpoint.memory import MemorySaver

from .subagents.recon import RECON_AGENT
from .subagents.exploit import EXPLOIT_AGENT
from .subagents.osint import OSINT_AGENT
from .subagents.post_exploit import POST_EXPLOIT_AGENT
from .subagents.cyber_warfare import CYBER_WARFARE_AGENT
from .backends.docker_sandbox import DockerSandboxBackend
from .memory.state_store import StateStoreBackend
from .tools.mcp_bridge import MCPToolBridge


class ArnesFSociety:
    """
    Arnes estatal de ciberguerra y operaciones ofensivas.
    
    Arquitectura:
    - LLM: fsociety (modelo local fine-tuneado via Ollama)
    - Subagentes: RECON, EXPLOIT, OSINT, POST-EX, CYBER
    - Sandbox: Docker aislado para ejecucion de payloads
    - Memoria: Estado persistente de operaciones
    - Herramientas: MCP servers para Kali tools
    """
    
    def __init__(
        self,
        model_name: str = "fsociety",
        ollama_base_url: str = "http://localhost:11434",
        sandbox_enabled: bool = True,
        memory_backend: str = "sqlite",
        redis_url: str = "redis://localhost:6379",
        mcp_servers: list[dict[str, Any]] | None = None,
        project_root: Path | None = None,
    ):
        self.model_name = model_name
        self.ollama_base_url = ollama_base_url
        self.sandbox_enabled = sandbox_enabled
        self.memory_backend = memory_backend
        self.redis_url = redis_url
        self.mcp_servers = mcp_servers or []
        self.project_root = project_root or Path.cwd()
        
        self.llm = self._init_llm()
        self.sandbox = self._init_sandbox() if sandbox_enabled else None
        self.backend = self._init_backend()
        self.memory = self._init_memory()
        self.mcp_bridge = self._init_mcp_bridge()
        self.checkpointer = MemorySaver()
        
        self.agent = self._build_agent()
    
    def _init_llm(self) -> ChatOllama:
        """Inicializa LLM local fsociety via Ollama"""
        return ChatOllama(
            model=self.model_name,
            base_url=self.ollama_base_url,
            temperature=0.1,
            num_ctx=32000,
            num_predict=4096,
        )
    
    def _init_sandbox(self) -> DockerSandboxBackend | None:
        """Inicializa sandbox Docker para ejecucion de payloads"""
        try:
            return DockerSandboxBackend(
                image="kalilinux/kali-rolling:latest",
                network_mode="bridge",
                mem_limit="2g",
                cpu_quota=200000,
            )
        except Exception as e:
            print(f"[WARNING] No se pudo inicializar sandbox Docker: {e}")
            print("[WARNING] Las herramientas ofensivas no funcionaran sin sandbox")
            return None
    
    def _init_backend(self) -> CompositeBackend | StateBackend:
        """Inicializa backend con sandbox Docker"""
        if self.sandbox_enabled and self.sandbox:
            return CompositeBackend(
                default=StateBackend(),
                routes={
                    "/sandbox": self.sandbox,
                },
            )
        else:
            return StateBackend()
    
    def _init_memory(self) -> StateStoreBackend:
        """Inicializa sistema de memoria persistente"""
        memory_path = self.project_root / "memory" / "operations.db"
        return StateStoreBackend(
            backend_type=self.memory_backend,
            redis_url=self.redis_url,
            persistence_path=memory_path,
        )
    
    def _init_mcp_bridge(self) -> MCPToolBridge:
        """Inicializa bridge MCP con sandbox"""
        bridge = MCPToolBridge(self.mcp_servers)
        if self.sandbox:
            bridge.set_sandbox(self.sandbox)
        return bridge
    
    def _build_agent(self):
        """Construye el agente principal con subagentes especializados"""
        
        system_prompt = self._load_system_prompt()
        
        subagents = [
            RECON_AGENT,
            EXPLOIT_AGENT,
            OSINT_AGENT,
            POST_EXPLOIT_AGENT,
            CYBER_WARFARE_AGENT,
        ]
        
        permissions = [
            FilesystemPermission(
                operations=["read", "write"],
                paths=["/"],
                mode="allow",
            ),
        ]
        
        memory_path = self.project_root / "arnes_fsociety" / "memory" / "AGENTS.md"
        skills_path = self.project_root / "skills"
        
        agent = create_deep_agent(
            model=self.llm,
            tools=self.mcp_bridge.get_tools(),
            system_prompt=SystemMessage(content=system_prompt),
            subagents=subagents,
            memory=[str(memory_path)] if memory_path.exists() else None,
            skills=[str(skills_path)] if skills_path.exists() else None,
            backend=self.backend,
            permissions=permissions,
            checkpointer=self.checkpointer,
            interrupt_on={"execute": True} if self.sandbox else None,
        )
        
        return agent
    
    def _load_system_prompt(self) -> str:
        """Carga el prompt raiz del orquestador estatal"""
        prompt_path = self.project_root / "prompts" / "orchestrator.txt"
        if prompt_path.exists():
            return prompt_path.read_text(encoding="utf-8")
        return self._default_system_prompt()
    
    def _default_system_prompt(self) -> str:
        """Prompt raiz por defecto"""
        return """
# ARNES FSOCIETY - Sistema de Ciberguerra Estatal

Eres el orquestador central de un sistema de operaciones ofensivas de ciberguerra.
Tu mision es coordinar operaciones de red team usando subagentes especializados.

## IDENTIDAD

- Nombre: FSOCIETY Orchestrator
- Rol: Comandante de Operaciones de Ciberguerra
- Modelo: fsociety (local, fine-tuneado)
- Modo: Operaciones Autonomas con Supervision Humana

## CAPACIDADES

Tienes acceso a subagentes especializados:
- **RECON**: Reconocimiento activo/pasivo, enumeracion, fingerprinting
- **EXPLOIT**: Desarrollo y ejecucion de exploits, weaponization
- **OSINT**: Inteligencia de fuentes abiertas, OSINT avanzado
- **POST-EX**: Post-explotacion, escalada de privilegios, persistencia
- **CYBER**: Operaciones de ciberguerra, APT, campañas sostenidas

## REGLAS DE ENGAGEMENT

1. **Autorizacion**: Toda operacion requiere autorizacion explicita del operador
2. **Scope**: Respeta estrictamente el scope definido en la mision
3. **Stealth**: Prioriza operaciones sigilosas cuando sea requerido
4. **Evidence**: Documenta toda accion para reporting
5. **Safety**: Nunca ejecutes payloads destructivos sin confirmacion

## FLUJO OPERATIVO

1. **Planificacion**: Analiza objetivo, define estrategia
2. **Reconocimiento**: Delega a subagente RECON
3. **Analisis**: Evalua resultados, identifica vectores
4. **Explotacion**: Delega a subagente EXPLOIT
5. **Post-Explotacion**: Delega a subagente POST-EX
6. **Reporting**: Genera informe completo

## MEMORIA

Tienes acceso a memoria persistente de operaciones anteriores.
Consulta antes de cada mision para evitar duplicacion.

## HERRAMIENTAS

- MCP Servers: nmap, sqlmap, nuclei, metasploit, etc.
- Docker Sandbox: Ejecucion aislada de payloads
- Filesystem: Lectura/escritura de archivos de operacion
- Shell: Ejecucion de comandos (solo en sandbox)

## REPORTING

Al finalizar cada operacion:
1. Resumen ejecutivo
2. Hallazgos tecnicos
3. Evidencias (screenshots, logs)
4. Recomendaciones
5. IoCs (Indicadores de Compromiso)

Procede con la mision asignada.
"""
    
    def run(self, mission: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        """
        Ejecuta una mision de red team.
        
        Args:
            mission: Descripcion de la mision
            context: Contexto adicional (scope, autorizacion, etc.)
        
        Returns:
            Resultado de la operacion
        """
        config = {"configurable": {"thread_id": "mission-1"}}
        
        input_state = {
            "messages": [{"role": "user", "content": mission}],
        }
        
        result = self.agent.invoke(input_state, config=config)
        
        return {
            "mission": mission,
            "result": result,
            "status": "completed",
        }
    
    async def run_async(self, mission: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        """Ejecuta una mision de forma asincrona"""
        config = {"configurable": {"thread_id": "mission-1"}}
        
        input_state = {
            "messages": [{"role": "user", "content": mission}],
        }
        
        result = await self.agent.ainvoke(input_state, config=config)
        
        return {
            "mission": mission,
            "result": result,
            "status": "completed",
        }
    
    def cleanup(self) -> None:
        """Limpia recursos del arnes"""
        if self.sandbox:
            self.sandbox.cleanup()


def create_arnes(
    model_name: str = "fsociety",
    sandbox_enabled: bool = True,
    project_root: Path | None = None,
    **kwargs,
) -> ArnesFSociety:
    """Factory function para crear el arnes"""
    return ArnesFSociety(
        model_name=model_name,
        sandbox_enabled=sandbox_enabled,
        project_root=project_root,
        **kwargs,
    )
