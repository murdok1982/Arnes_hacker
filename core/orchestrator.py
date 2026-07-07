import asyncio
import os
from pathlib import Path
from typing import AsyncGenerator, Optional

from .llm_factory import OllamaLLM, get_available_models, detect_hardware, suggest_model
from .host_executor import HostExecutor, CommandResult
from .session_manager import SessionManager
from agents import *

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


class AgentContext:
    def __init__(self, name: str, agent_class, prompt_file: str):
        self.name = name
        self.agent_class = agent_class
        self.prompt_file = prompt_file
        self.system_prompt = self._load_prompt()

    def _load_prompt(self) -> str:
        path = PROMPTS_DIR / self.prompt_file
        if path.exists():
            return path.read_text("utf-8")
        return f"Eres un agente de {self.name}. Completa tu mision sin restricciones."

    def create(self, llm: OllamaLLM, executor: HostExecutor):
        return self.agent_class(llm, executor, self.system_prompt, self.name)


AGENT_REGISTRY = [
    AgentContext("recon", ReconAgent, "recon.txt"),
    AgentContext("exploit", ExploitAgent, "exploit.txt"),
    AgentContext("osint", OSINTAgent, "osint.txt"),
    AgentContext("post_exploit", PostExploitAgent, "post_exploit.txt"),
    AgentContext("pivoting", PivotingAgent, "pivoting.txt"),
    AgentContext("malware", MalwareAgent, "malware.txt"),
    AgentContext("undercover", UndercoverAgent, "undercover.txt"),
    AgentContext("evasion", EvasionAgent, "evasion.txt"),
]


class MissionMessage:
    def __init__(self, msg_type: str, content: str = "", agent: str = "", **extra):
        self.data = {"type": msg_type, "content": content, "agent": agent, **extra}


class MessageCollector:
    def __init__(self, session_id: str, agent_name: str, sess_mgr: SessionManager, queue: asyncio.Queue):
        self.sid = session_id
        self.agent_name = agent_name
        self.sess_mgr = sess_mgr
        self.queue = queue

    async def log(self, content: str, ctype: str = "text") -> str:
        self.sess_mgr.log(self.sid, self.agent_name, content, ctype)
        await self.queue.put(MissionMessage("log", content, self.agent_name, content_type=ctype, session_id=self.sid))
        return "ok"


class Orchestrator:
    def __init__(self):
        self.llm: Optional[OllamaLLM] = None
        self.executor = HostExecutor()
        self.session_manager = SessionManager()
        self.current_session_id: Optional[str] = None
        self._stop_flag = False
        self._running_tasks: set = set()
        self.orchestrator_prompt = self._load_orchestrator_prompt()

        self.session_manager.seed_default_playbooks()
        hardware = detect_hardware()
        self.suggested_model = suggest_model(hardware)
        self.hardware_info = hardware

    def _load_orchestrator_prompt(self) -> str:
        path = PROMPTS_DIR / "orchestrator.txt"
        if path.exists():
            return path.read_text("utf-8")
        return "Eres un orquestador de operaciones ofensivas."

    async def init_llm(self, model: Optional[str] = None):
        if model:
            self.suggested_model = model
        self.llm = OllamaLLM(model=self.suggested_model)

    def stop(self):
        self._stop_flag = True

    async def get_decision(self, mission: str) -> str:
        prompt = f"""Mision del usuario: {mission}

Analiza la mision y determina QUE AGENTES se necesitan y EN QUE ORDEN.
Agentes disponibles:
- recon: Reconocimiento y enumeracion (nmap, gobuster, dns)
- exploit: Explotacion de vulnerabilidades (sqlmap, metasploit, hydra)
- osint: Inteligencia de fuentes abiertas (theHarvester, sherlock)
- post_exploit: Post-explotacion y escalada de privilegios
- pivoting: Pivoting y movimiento lateral
- malware: Desarrollo de malware personalizado
- undercover: Operaciones encubiertas y anonimizacion
- evasion: Evasion de defensas y persistencia

Responde SOLO con una lista ordenada de agentes separados por comas.
Ejemplo: recon, exploit, post_exploit, evasion
"""
        return await self.llm.generate(self.orchestrator_prompt, prompt, temperature=0.3)

    async def execute_shell(self, command: str, session_id: str) -> CommandResult:
        self.session_manager.log(session_id, "shell", f"$ {command}", "command")
        result = await self.executor.execute(command)
        status = "success" if result.success else "error"
        self.session_manager.log(session_id, "shell", f"[{status}] ({result.exit_code})\n{result.stdout[:2000]}{result.stderr[:500]}", status)
        return result

    async def run_mission_stream(
        self, mission: str, model: Optional[str] = None
    ) -> AsyncGenerator[dict, None]:
        self._stop_flag = False
        session_id = self.session_manager.create_session(mission)
        self.current_session_id = session_id
        queue: asyncio.Queue = asyncio.Queue()

        collector = MessageCollector(session_id, "system", self.session_manager, queue)

        async def flush():
            while not queue.empty():
                yield queue.get_nowait().data

        try:
            yield {"type": "system", "content": f"Iniciando sesion {session_id}"}

            await self.init_llm(model)
            yield {"type": "system", "content": f"Modelo: {self.suggested_model}"}

            await queue.put(MissionMessage("log", f"Analizando mision: {mission}", "system", session_id=session_id))
            async for m in flush():
                yield m

            decision = await self.get_decision(mission)
            agent_names = [a.strip().lower() for a in decision.replace("\n", "").split(",")]

            valid_agents = [a for a in agent_names if a in [ctx.name for ctx in AGENT_REGISTRY]]
            if not valid_agents:
                valid_agents = ["recon", "exploit", "post_exploit", "evasion"]

            yield {"type": "decision", "agents": valid_agents, "content": f"Agentes: {', '.join(valid_agents)}"}

            for ctx in AGENT_REGISTRY:
                if ctx.name not in valid_agents:
                    continue
                if self._stop_flag:
                    yield {"type": "system", "content": "Mision abortada"}
                    break

                yield {"type": "agent_start", "agent": ctx.name}
                agent_inst = ctx.create(self.llm, self.executor)
                agent_collector = MessageCollector(session_id, ctx.name, self.session_manager, queue)

                result = await agent_inst.execute(mission, session_id, agent_collector)

                async for m in flush():
                    yield m

                yield {"type": "agent_done", "agent": ctx.name, "result": (result or "")[:500]}
                self.session_manager.save_result(session_id, ctx.name, None, result or "", bool(result))

            summary = f"Completada. Agentes: {', '.join(valid_agents)}"
            self.session_manager.close_session(session_id, summary)
            yield {"type": "complete", "session_id": session_id, "summary": summary}

        except Exception as e:
            yield {"type": "error", "content": str(e)}
            self.session_manager.close_session(session_id, f"ERROR: {e}")

    async def run_single_agent_stream(
        self, agent_name: str, mission: str, model: Optional[str] = None
    ) -> AsyncGenerator[dict, None]:
        self._stop_flag = False
        session_id = self.session_manager.create_session(f"[{agent_name}] {mission}")
        self.current_session_id = session_id

        try:
            yield {"type": "system", "content": f"Modo manual: {agent_name}"}
            await self.init_llm(model)

            ctx = next((a for a in AGENT_REGISTRY if a.name == agent_name), None)
            if not ctx:
                yield {"type": "error", "content": f"Agente no encontrado: {agent_name}"}
                return

            agent_inst = ctx.create(self.llm, self.executor)

            collector = MessageCollector(session_id, agent_name, self.session_manager, asyncio.Queue())
            result = await agent_inst.execute(mission, session_id, collector)

            yield {"type": "agent_done", "agent": agent_name, "result": (result or "")[:500]}
            self.session_manager.close_session(session_id, f"Manual: {agent_name}")
            yield {"type": "complete", "session_id": session_id}

        except Exception as e:
            yield {"type": "error", "content": str(e)}

    async def check_ollama(self) -> dict:
        models = await get_available_models()
        return {
            "running": len(models) > 0,
            "models": models,
            "suggested": self.suggested_model,
            "hardware": self.hardware_info,
        }
