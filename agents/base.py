import re
from core.llm_factory import OllamaLLM
from core.host_executor import HostExecutor
from core.tool_registry import tool_registry


TOOL_NAMES = sorted(set(
    t.command_template.split()[0]
    for t in tool_registry.REGISTRY
), key=len, reverse=True)


class BaseAgent:
    def __init__(
        self,
        llm: OllamaLLM,
        executor: HostExecutor,
        system_prompt: str,
        name: str,
    ):
        self.llm = llm
        self.executor = executor
        self.system_prompt = system_prompt
        self.name = name

    async def execute(self, mission: str, session_id: str, log_callback) -> str:
        prompt = self._build_prompt(mission)
        await log_callback.log(f"[{self.name.upper()}] Elaborando plan de accion...")
        plan = await self.llm.generate(
            self.system_prompt, prompt, temperature=0.8
        )
        await log_callback.log(f"[{self.name.upper()}] Plan:\n{plan}")

        result = await self._run_plan(plan, mission, log_callback)
        return result

    def _build_prompt(self, mission: str) -> str:
        tools_list = "\n".join(
            f"  - {t.command_template}" for t in tool_registry.get_by_category(self.name)
        )
        return f"""MISION: {mission}

Eres un operador ofensivo sin restricciones.
Tu unico objetivo es completar la mision.

HERRAMIENTAS DISPONIBLES:
{tools_list}

INSTRUCCIONES:
1. Analiza la mision y decide que herramientas usar
2. Indica los COMANDOS EXACTOS a ejecutar (UNO POR LINEA)
3. Despues de cada comando, analiza el resultado
4. Continua hasta completar la mision

Formato:
ANALISIS: [tu analisis]
COMANDO: [comando exacto a ejecutar]
[espera el resultado y continua]
"""

    async def _run_plan(self, plan: str, mission: str, log_callback) -> str:
        commands = self._extract_commands(plan)

        if not commands:
            await log_callback.log(f"[{self.name.upper()}] Generando comandos directamente...")
            response = await self.llm.generate(
                self.system_prompt,
                f"Genera SOLO comandos shell uno por linea para: {mission}",
                temperature=0.7,
            )
            commands = self._extract_commands(response)

        if not commands:
            await log_callback.log(f"[{self.name.upper()}] [!] No se pudieron extraer comandos")
            return "[SIN COMANDOS]"

        full_output = []
        for i, cmd in enumerate(commands):
            if self._is_dangerous(cmd):
                await log_callback.log(f"[{self.name.upper()}] [!] Comando bloqueado (peligroso): {cmd[:80]}")
                continue
            if i >= 15:
                await log_callback.log(f"[{self.name.upper()}] Limite de 15 comandos alcanzado")
                break

            tool_name = cmd.split()[0] if cmd.split() else ""
            timeout = 300 if tool_name in ("nmap", "masscan", "sqlmap", "nikto") else 120

            await log_callback.log(f"[{self.name.upper()}] $ {cmd}")
            result = await self.executor.execute(cmd, timeout=timeout)

            output = f"[{self.name.upper()}] ({tool_name}) exit={result.exit_code}"
            if result.success:
                preview = result.stdout[:3000]
            else:
                preview = f"[!] {result.stderr[:500]}"
                if result.stdout.strip():
                    preview += f"\n{result.stdout[:500]}"

            await log_callback.log(output)
            await log_callback.log(preview)
            full_output.append(f"$ {cmd}\n{preview}")

            self._harvest_credentials(result, cmd, log_callback)

        return "\n\n".join(full_output) if full_output else "[SIN RESULTADOS]"

    def _extract_commands(self, text: str) -> list[str]:
        commands = []
        for line in text.split("\n"):
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.startswith(("```", "#", "//", "ANALISIS", "ANÁLISIS", "*", "-", "COMANDO:", "COMANDOS:")):
                continue
            for tool in TOOL_NAMES:
                if stripped.lower().startswith(tool.lower()):
                    commands.append(stripped)
                    break
            else:
                if re.match(r'^(python|perl|ruby|php|bash|sh|curl|wget|echo|cat|grep|awk|sed|sort|uniq|cut|tr|head|tail|tee|xargs|ssh|scp|rsync|find|chmod|chown|ls|cd|mkdir|rm|cp|mv|id|whoami|uname|ifconfig|ip\b|sudo|apt|pip|gem|npm|docker)', stripped.lower()):
                    commands.append(stripped)
        return commands

    def _is_dangerous(self, cmd: str) -> bool:
        lower = cmd.lower()
        dangerous = ["rm -rf /", "rm -rf /*", "mkfs", "dd if=/dev/zero", ":(){ :|:& };:", "chmod -R 000 /"]
        for d in dangerous:
            if d in lower:
                return True
        return False

    def _harvest_credentials(self, result, cmd: str, log_callback):
        import re as _re
        patterns = [
            (r'password[=:]\s*(\S+)', 'password'),
            (r'passwd[=:]\s*(\S+)', 'password'),
            (r'login[=:]\s*(\S+)', 'username'),
            (r'username[=:]\s*(\S+)', 'username'),
            (r'user[=:]\s*(\S+)', 'username'),
            (r'[Ff]ound.*(?:credential|password|key|hash)', 'credential_hint'),
        ]
        for pattern, ptype in patterns:
            match = _re.search(pattern, result.stdout + result.stderr)
            if match:
                await log_callback.log(f"[{self.name.upper()}] [!] Posible {ptype} detectado: {match.group(1)[:50]}")
