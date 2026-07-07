import asyncio
import os
import shlex
import shutil
from typing import Optional


class CommandResult:
    def __init__(self, stdout: str, stderr: str, exit_code: int, command: str):
        self.stdout = stdout
        self.stderr = stderr
        self.exit_code = exit_code
        self.command = command
        self.success = exit_code == 0

    def __str__(self) -> str:
        if self.success:
            return self.stdout
        return f"[ERROR] ({self.exit_code}): {self.stderr or self.stdout}"


class HostExecutor:
    def __init__(self):
        self.timeout_default = 300
        self._check_tools()

    def _check_tools(self):
        required = ["nmap", "sqlmap", "msfconsole", "hydra", "gobuster", "nikto"]
        self.available_tools = {}
        for tool in required:
            path = shutil.which(tool)
            self.available_tools[tool] = path is not None

    def tool_available(self, name: str) -> bool:
        if name in self.available_tools:
            return self.available_tools[name]
        path = shutil.which(name)
        self.available_tools[name] = path is not None
        return path is not None

    async def execute(
        self,
        command: str,
        timeout: Optional[int] = None,
        workdir: Optional[str] = None,
        env: Optional[dict] = None,
    ) -> CommandResult:
        timeout = timeout or self.timeout_default
        env_base = os.environ.copy()
        if env:
            env_base.update(env)

        try:
            proc = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=workdir,
                env=env_base,
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    proc.communicate(), timeout=timeout
                )
            except asyncio.TimeoutError:
                proc.kill()
                await proc.wait()
                return CommandResult(
                    stdout="",
                    stderr=f"[TIMEOUT] Comando excedio {timeout}s: {command[:100]}...",
                    exit_code=-1,
                    command=command,
                )

            return CommandResult(
                stdout=stdout.decode("utf-8", errors="replace"),
                stderr=stderr.decode("utf-8", errors="replace"),
                exit_code=proc.returncode or 0,
                command=command,
            )

        except FileNotFoundError:
            return CommandResult(
                stdout="",
                stderr=f"[ERROR] Comando no encontrado: {command.split()[0]}",
                exit_code=-1,
                command=command,
            )
        except Exception as e:
            return CommandResult(
                stdout="",
                stderr=f"[ERROR] {e}",
                exit_code=-1,
                command=command,
            )

    async def execute_quoted(self, *args: str, timeout: Optional[int] = None) -> CommandResult:
        return await self.execute(
            " ".join(shlex.quote(a) for a in args), timeout=timeout
        )

    def format_result(self, result: CommandResult, tool_name: str = "") -> str:
        lines = []
        if tool_name:
            lines.append(f"[{tool_name.upper()}] Comando: {result.command}")
        if result.success:
            lines.append(result.stdout.strip())
        else:
            lines.append(result.stderr.strip() or result.stdout.strip())
        return "\n".join(lines)
