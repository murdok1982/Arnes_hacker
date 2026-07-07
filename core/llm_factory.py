import os
import json
import httpx
from typing import AsyncGenerator

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:7b")


class OllamaLLM:
    def __init__(self, model: str = OLLAMA_MODEL, base_url: str = OLLAMA_BASE_URL):
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.client = httpx.AsyncClient(timeout=300.0)

    async def generate(
        self, system_prompt: str, user_message: str, temperature: float = 0.8
    ) -> str:
        payload = {
            "model": self.model,
            "prompt": user_message,
            "system": system_prompt,
            "stream": False,
            "temperature": temperature,
            "num_ctx": 8192,
        }
        resp = await self.client.post(f"{self.base_url}/api/generate", json=payload)
        resp.raise_for_status()
        data = resp.json()
        return data.get("response", "")

    async def generate_stream(
        self, system_prompt: str, user_message: str, temperature: float = 0.8
    ) -> AsyncGenerator[str, None]:
        payload = {
            "model": self.model,
            "prompt": user_message,
            "system": system_prompt,
            "stream": True,
            "temperature": temperature,
            "num_ctx": 8192,
        }
        async with self.client.stream(
            "POST", f"{self.base_url}/api/generate", json=payload
        ) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                    token = data.get("response", "")
                    if token:
                        yield token
                    if data.get("done", False):
                        break
                except json.JSONDecodeError:
                    continue

    async def chat(
        self,
        system_prompt: str,
        messages: list[dict],
        temperature: float = 0.8,
    ) -> str:
        ollama_messages = [{"role": "system", "content": system_prompt}]
        for msg in messages:
            ollama_messages.append(
                {"role": msg.get("role", "user"), "content": msg.get("content", "")}
            )
        payload = {
            "model": self.model,
            "messages": ollama_messages,
            "stream": False,
            "temperature": temperature,
        }
        resp = await self.client.post(f"{self.base_url}/api/chat", json=payload)
        resp.raise_for_status()
        data = resp.json()
        return data.get("message", {}).get("content", "")

    async def close(self):
        await self.client.aclose()


async def get_available_models() -> list[str]:
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await client.get(
                f"{OLLAMA_BASE_URL}/api/tags"
            )
            resp.raise_for_status()
            data = resp.json()
            return [m["name"] for m in data.get("models", [])]
        except Exception:
            return []


def detect_hardware() -> dict:
    info = {"gpu_memory_gb": 0, "total_ram_gb": 0, "has_nvidia": False, "has_rocm": False}

    try:
        result = os.popen("nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits 2>nul").read().strip()
        if result:
            lines = [l.strip() for l in result.split("\n") if l.strip()]
            if lines:
                info["gpu_memory_gb"] = int(lines[0]) // 1024
                info["has_nvidia"] = True
    except Exception:
        pass

    if not info["has_nvidia"]:
        try:
            result = os.popen("rocm-smi --showmeminfo vram 2>nul").read().strip()
            if result:
                info["has_rocm"] = True
                for line in result.split("\n"):
                    if "VRAM Total" in line:
                        parts = line.split()
                        for p in parts:
                            try:
                                gb = int(p.replace("GB", "").replace("MB", ""))
                                if "MB" in p:
                                    gb = gb // 1024
                                info["gpu_memory_gb"] = max(info["gpu_memory_gb"], gb)
                            except ValueError:
                                continue
        except Exception:
            pass

    try:
        result = os.popen("free -g 2>/dev/null | grep Mem | awk '{print $2}'").read().strip()
        if result:
            info["total_ram_gb"] = int(result)
    except Exception:
        try:
            import psutil
            info["total_ram_gb"] = psutil.virtual_memory().total // (1024**3)
        except ImportError:
            info["total_ram_gb"] = 8

    return info


def suggest_model(hardware: dict) -> str:
    gpu = hardware.get("gpu_memory_gb", 0)
    ram = hardware.get("total_ram_gb", 8)

    if gpu >= 24:
        return "qwen2.5-coder:32b"
    elif gpu >= 16:
        return "qwen2.5-coder:14b"
    elif gpu >= 8:
        return "qwen2.5-coder:14b"
    elif gpu >= 4:
        return "qwen2.5-coder:7b"
    elif ram >= 32:
        return "qwen2.5-coder:7b"
    elif ram >= 16:
        return "qwen2.5-coder:7b-q4_K_M"
    else:
        return "qwen2.5-coder:7b-q4_K_M"
