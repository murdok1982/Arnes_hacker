"""
Docker Sandbox Backend - Ejecucion Aislada de Payloads
Sandbox basado en Docker con Kali Linux para ejecucion segura de herramientas ofensivas
"""

import io
import tarfile
import uuid
from pathlib import Path
from typing import Any

import docker
from docker.errors import ContainerError, ImageNotFound
from deepagents.backends.sandbox import BaseSandbox


class DockerSandboxBackend(BaseSandbox):
    """
    Backend de sandbox basado en Docker para ejecucion aislada de payloads.
    
    Caracteristicas:
    - Contenedor efimero por sesion
    - Kali Linux con herramientas preinstaladas
    - Red aislada (bridge o none)
    - Limites de recursos (CPU, memoria)
    - Sin persistencia (se destruye al finalizar)
    - Volumenes temporales para intercambio de archivos
    """
    
    def __init__(
        self,
        image: str = "kalilinux/kali-rolling:latest",
        network_mode: str = "bridge",
        mem_limit: str = "2g",
        cpu_quota: int = 200000,
        cpu_period: int = 100000,
        timeout: int = 300,
        max_output_bytes: int = 1024 * 1024,
        volumes: dict[str, dict[str, str]] | None = None,
        environment: dict[str, str] | None = None,
        auto_cleanup: bool = True,
    ):
        super().__init__()
        self.image = image
        self.network_mode = network_mode
        self.mem_limit = mem_limit
        self.cpu_quota = cpu_quota
        self.cpu_period = cpu_period
        self.timeout = timeout
        self.max_output_bytes = max_output_bytes
        self.volumes = volumes or {}
        self.environment = environment or {}
        self.auto_cleanup = auto_cleanup
        
        self._id = str(uuid.uuid4())[:8]
        self.client = docker.from_env()
        self.container = None
        
        self._ensure_image()
        self._create_container()
    
    @property
    def id(self) -> str:
        """Identificador unico del backend"""
        return self._id
    
    def _ensure_image(self) -> None:
        """Verifica que la imagen Docker existe, la descarga si es necesario"""
        try:
            self.client.images.get(self.image)
        except ImageNotFound:
            self.client.images.pull(self.image)
    
    def _create_container(self) -> None:
        """Crea el contenedor sandbox"""
        self.container = self.client.containers.create(
            image=self.image,
            name=f"fsociety-sandbox-{self._id}",
            network_mode=self.network_mode,
            mem_limit=self.mem_limit,
            cpu_quota=self.cpu_quota,
            cpu_period=self.cpu_period,
            volumes=self.volumes,
            environment=self.environment,
            detach=True,
            stdin_open=True,
        )
        self.container.start()
    
    def execute(self, command: str) -> str:
        """
        Ejecuta un comando en el sandbox Docker.
        
        Args:
            command: Comando a ejecutar
        
        Returns:
            Salida del comando (stdout + stderr)
        """
        if not self.container:
            raise RuntimeError("Sandbox container not initialized")
        
        try:
            exit_code, output = self.container.exec_run(
                cmd=["bash", "-c", command],
                stdout=True,
                stderr=True,
                demux=False,
            )
            
            result = output.decode("utf-8", errors="replace")
            
            if len(result) > self.max_output_bytes:
                result = result[:self.max_output_bytes] + "\n[TRUNCATED]"
            
            return f"[exit_code={exit_code}]\n{result}"
        
        except Exception as e:
            return f"[ERROR] {str(e)}"
    
    def read(self, path: str) -> str:
        """Lee un archivo del sandbox"""
        if not self.container:
            raise RuntimeError("Sandbox container not initialized")
        
        try:
            bits, stat = self.container.get_archive(path)
            
            tar_stream = io.BytesIO()
            for chunk in bits:
                tar_stream.write(chunk)
            tar_stream.seek(0)
            
            with tarfile.open(fileobj=tar_stream) as tar:
                member = tar.getmembers()[0]
                file_obj = tar.extractfile(member)
                if file_obj:
                    content = file_obj.read()
                    return content.decode("utf-8", errors="replace")
                return ""
        
        except Exception as e:
            return f"[ERROR] Failed to read {path}: {str(e)}"
    
    def write(self, path: str, content: str) -> str:
        """Escribe un archivo en el sandbox"""
        if not self.container:
            raise RuntimeError("Sandbox container not initialized")
        
        try:
            tar_stream = io.BytesIO()
            with tarfile.open(fileobj=tar_stream, mode="w") as tar:
                data = content.encode("utf-8")
                info = tarfile.TarInfo(name=Path(path).name)
                info.size = len(data)
                tar.addfile(info, io.BytesIO(data))
            
            tar_stream.seek(0)
            self.container.put_archive(str(Path(path).parent), tar_stream)
            
            return f"[OK] Written to {path}"
        
        except Exception as e:
            return f"[ERROR] Failed to write {path}: {str(e)}"
    
    def edit(self, path: str, old: str, new: str) -> str:
        """Edita un archivo en el sandbox"""
        try:
            content = self.read(path)
            if content.startswith("[ERROR]"):
                return content
            
            if old not in content:
                return f"[ERROR] Pattern not found in {path}"
            
            new_content = content.replace(old, new, 1)
            return self.write(path, new_content)
        
        except Exception as e:
            return f"[ERROR] Failed to edit {path}: {str(e)}"
    
    def glob(self, pattern: str) -> str:
        """Busca archivos en el sandbox"""
        return self.execute(f"find / -path '{pattern}' 2>/dev/null | head -100")
    
    def upload_files(self, files: dict[str, str]) -> str:
        """
        Sube multiples archivos al sandbox.
        
        Args:
            files: Diccionario {path: content}
        
        Returns:
            Resultado de la operacion
        """
        results = []
        for path, content in files.items():
            result = self.write(path, content)
            results.append(f"{path}: {result}")
        return "\n".join(results)
    
    def download_files(self, paths: list[str]) -> dict[str, str]:
        """Descarga multiples archivos del sandbox"""
        results = {}
        for path in paths:
            results[path] = self.read(path)
        return results
    
    def cleanup(self) -> None:
        """Limpia el contenedor sandbox"""
        if self.container and self.auto_cleanup:
            try:
                self.container.stop(timeout=5)
                self.container.remove(force=True)
            except Exception:
                pass
            finally:
                self.container = None
    
    def __del__(self):
        """Destructor: limpia el contenedor"""
        self.cleanup()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()
        return False
