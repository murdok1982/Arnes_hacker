#!/usr/bin/env python3
"""
Test rapido del arnes FSOCIETY
Verifica que todos los componentes estan correctamente configurados
"""

import sys
from pathlib import Path

def test_imports():
    """Verifica que todos los modulos se pueden importar"""
    print("[+] Verificando importaciones...")
    
    try:
        from arnes_fsociety import create_arnes, ArnesFSociety
        print("    [OK] arnes_fsociety")
    except Exception as e:
        print(f"    [ERROR] arnes_fsociety: {e}")
        return False
    
    try:
        from arnes_fsociety.subagents import RECON_AGENT, EXPLOIT_AGENT, OSINT_AGENT, POST_EXPLOIT_AGENT, CYBER_WARFARE_AGENT
        print("    [OK] subagents")
    except Exception as e:
        print(f"    [ERROR] subagents: {e}")
        return False
    
    try:
        from arnes_fsociety.backends.docker_sandbox import DockerSandboxBackend
        print("    [OK] docker_sandbox")
    except Exception as e:
        print(f"    [ERROR] docker_sandbox: {e}")
        return False
    
    try:
        from arnes_fsociety.memory.state_store import StateStoreBackend
        print("    [OK] state_store")
    except Exception as e:
        print(f"    [ERROR] state_store: {e}")
        return False
    
    try:
        from arnes_fsociety.tools.mcp_bridge import MCPToolBridge
        print("    [OK] mcp_bridge")
    except Exception as e:
        print(f"    [ERROR] mcp_bridge: {e}")
        return False
    
    return True

def test_ollama():
    """Verifica que Ollama esta disponible"""
    print("\n[+] Verificando Ollama...")
    
    try:
        import subprocess
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=5)
        
        if "fsociety" in result.stdout:
            print("    [OK] Modelo fsociety encontrado")
            return True
        else:
            print("    [WARNING] Modelo fsociety no encontrado")
            print("    Ejecutar: ollama pull fsociety")
            return False
    except Exception as e:
        print(f"    [ERROR] Ollama no disponible: {e}")
        return False

def test_docker():
    """Verifica que Docker esta disponible"""
    print("\n[+] Verificando Docker...")
    
    try:
        import subprocess
        result = subprocess.run(["docker", "info"], capture_output=True, text=True, timeout=5)
        
        if result.returncode == 0:
            print("    [OK] Docker disponible")
            return True
        else:
            print("    [WARNING] Docker no responde correctamente")
            return False
    except Exception as e:
        print(f"    [ERROR] Docker no disponible: {e}")
        return False

def test_directories():
    """Verifica que los directorios necesarios existen"""
    print("\n[+] Verificando directorios...")
    
    required_dirs = [
        "arnes_fsociety",
        "skills",
        "prompts",
        "sandbox",
        "output",
        "memory",
    ]
    
    all_ok = True
    for dir_name in required_dirs:
        if Path(dir_name).exists():
            print(f"    [OK] {dir_name}/")
        else:
            print(f"    [MISSING] {dir_name}/")
            all_ok = False
    
    return all_ok

def test_files():
    """Verifica que los archivos necesarios existen"""
    print("\n[+] Verificando archivos...")
    
    required_files = [
        "main.py",
        "pyproject.toml",
        "prompts/orchestrator.txt",
        "arnes_fsociety/memory/AGENTS.md",
        "sandbox/Dockerfile",
    ]
    
    all_ok = True
    for file_name in required_files:
        if Path(file_name).exists():
            print(f"    [OK] {file_name}")
        else:
            print(f"    [MISSING] {file_name}")
            all_ok = False
    
    return all_ok

def test_backend_apis():
    """Verifica que las APIs de backends son correctas"""
    print("\n[+] Verificando APIs de backends...")
    
    try:
        from arnes_fsociety.backends.docker_sandbox import DockerSandboxBackend
        from deepagents.backends.sandbox import BaseSandbox
        
        # Verificar metodos abstractos implementados
        required_methods = ['execute', 'read', 'write', 'edit', 'glob', 'upload_files', 'download_files', 'id']
        for method in required_methods:
            if hasattr(DockerSandboxBackend, method):
                print(f"    [OK] DockerSandboxBackend.{method}")
            else:
                print(f"    [MISSING] DockerSandboxBackend.{method}")
                return False
    except Exception as e:
        print(f"    [ERROR] {e}")
        return False
    
    try:
        from arnes_fsociety.memory.state_store import StateStoreBackend
        from langgraph.store.base import BaseStore
        
        # Verificar metodos abstractos implementados
        required_methods = ['put', 'get', 'search', 'delete', 'batch', 'abatch']
        for method in required_methods:
            if hasattr(StateStoreBackend, method):
                print(f"    [OK] StateStoreBackend.{method}")
            else:
                print(f"    [MISSING] StateStoreBackend.{method}")
                return False
    except Exception as e:
        print(f"    [ERROR] {e}")
        return False
    
    return True

def test_composite_backend():
    """Verifica que CompositeBackend se puede crear correctamente"""
    print("\n[+] Verificando CompositeBackend...")
    
    try:
        from deepagents.backends import CompositeBackend, StateBackend
        
        cb = CompositeBackend(
            default=StateBackend(),
            routes={"/sandbox": StateBackend()}
        )
        print("    [OK] CompositeBackend con default + routes")
        return True
    except Exception as e:
        print(f"    [ERROR] {e}")
        return False

def test_mcp_tools():
    """Verifica que las herramientas MCP se crean correctamente"""
    print("\n[+] Verificando herramientas MCP...")
    
    try:
        from arnes_fsociety.tools.mcp_bridge import MCPToolBridge
        
        bridge = MCPToolBridge([
            {"type": "nmap"},
            {"type": "sqlmap"},
            {"type": "nuclei"},
            {"type": "metasploit"},
        ])
        
        tools = bridge.get_tools()
        print(f"    [OK] {len(tools)} herramientas creadas")
        
        for tool in tools:
            print(f"        - {tool.name}: {tool.description[:50]}...")
        
        return len(tools) > 0
    except Exception as e:
        print(f"    [ERROR] {e}")
        return False

def test_memory_store():
    """Verifica que el store de memoria funciona"""
    print("\n[+] Verificando memoria persistente...")
    
    try:
        from arnes_fsociety.memory.state_store import StateStoreBackend
        from pathlib import Path
        import tempfile
        
        # Usar un archivo temporal para testing
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            temp_path = Path(f.name)
        
        store = StateStoreBackend(persistence_path=temp_path)
        
        # Test put
        store.put(("test", "unit"), "key1", {"data": "value1"})
        print("    [OK] put()")
        
        # Test get
        item = store.get(("test", "unit"), "key1")
        if item and item.value.get("data") == "value1":
            print("    [OK] get()")
        else:
            print("    [FAIL] get() - valor incorrecto")
            return False
        
        # Test search
        items = store.search(("test",), limit=10)
        if len(items) > 0:
            print("    [OK] search()")
        else:
            print("    [FAIL] search() - no encontro items")
            return False
        
        # Test delete
        store.delete(("test", "unit"), "key1")
        print("    [OK] delete()")
        
        # Limpiar
        del store
        import gc
        gc.collect()
        import time
        time.sleep(0.1)
        temp_path.unlink(missing_ok=True)
        
        return True
    except Exception as e:
        print(f"    [ERROR] {e}")
        return False

def test_arnes_creation():
    """Verifica que el arnes se puede crear sin sandbox"""
    print("\n[+] Verificando creacion del arnes (sin sandbox)...")
    
    try:
        from arnes_fsociety import create_arnes
        from pathlib import Path
        
        project_root = Path(__file__).parent.resolve()
        
        arnes = create_arnes(
            model_name="fsociety",
            sandbox_enabled=False,
            project_root=project_root,
        )
        
        print("    [OK] Arnes creado sin sandbox")
        
        if arnes.agent:
            print("    [OK] Agente principal inicializado")
        else:
            print("    [FAIL] Agente principal no inicializado")
            return False
        
        if arnes.memory:
            print("    [OK] Memoria persistente inicializada")
        else:
            print("    [FAIL] Memoria persistente no inicializada")
            return False
        
        return True
    except Exception as e:
        print(f"    [ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=" * 60)
    print("  ARNES FSOCIETY - Test de Componentes")
    print("=" * 60)
    
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("Ollama", test_ollama()))
    results.append(("Docker", test_docker()))
    results.append(("Directories", test_directories()))
    results.append(("Files", test_files()))
    results.append(("Backend APIs", test_backend_apis()))
    results.append(("CompositeBackend", test_composite_backend()))
    results.append(("MCP Tools", test_mcp_tools()))
    results.append(("Memory Store", test_memory_store()))
    results.append(("Arnes Creation", test_arnes_creation()))
    
    print("\n" + "=" * 60)
    print("  RESULTADOS")
    print("=" * 60)
    
    for name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"  {name:20s} [{status}]")
    
    print("=" * 60)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    if passed == total:
        print(f"\n[OK] Todos los tests pasaron ({passed}/{total}). Sistema listo.")
        print("\nProximo paso: python main.py --list-agents")
        return 0
    else:
        print(f"\n[WARNING] {total - passed} test(s) fallaron ({passed}/{total}).")
        print("Revisa la configuracion antes de ejecutar misiones.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
