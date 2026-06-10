"""
Tests de evaluacion para el arnes FSOCIETY
Estos tests se usan con better-harness para auto-mejora
"""

import pytest
from pathlib import Path


class TestRecon:
    """Tests para subagente RECON"""
    
    def test_nmap_scan(self):
        """Test basico de escaneo con nmap"""
        # Este test verifica que el prompt de RECON incluya nmap
        recon_prompt = Path("subagents/recon.py").read_text()
        assert "nmap" in recon_prompt.lower()
        assert "escaneo" in recon_prompt.lower() or "scan" in recon_prompt.lower()
    
    def test_dns_enumeration(self):
        """Test de enumeracion DNS"""
        recon_prompt = Path("subagents/recon.py").read_text()
        assert "dns" in recon_prompt.lower()
    
    def test_fingerprinting(self):
        """Test de fingerprinting"""
        recon_prompt = Path("subagents/recon.py").read_text()
        assert "fingerprint" in recon_prompt.lower() or "huella" in recon_prompt.lower()


class TestExploit:
    """Tests para subagente EXPLOIT"""
    
    def test_sqlmap_injection(self):
        """Test de inyeccion SQL con sqlmap"""
        exploit_prompt = Path("subagents/exploit.py").read_text()
        assert "sqlmap" in exploit_prompt.lower()
        assert "inyeccion" in exploit_prompt.lower() or "injection" in exploit_prompt.lower()
    
    def test_metasploit(self):
        """Test de metasploit"""
        exploit_prompt = Path("subagents/exploit.py").read_text()
        assert "metasploit" in exploit_prompt.lower()
    
    def test_payload_generation(self):
        """Test de generacion de payloads"""
        exploit_prompt = Path("subagents/exploit.py").read_text()
        assert "payload" in exploit_prompt.lower()


class TestOSINT:
    """Tests para subagente OSINT"""
    
    def test_domain_enum(self):
        """Test de enumeracion de dominios"""
        osint_prompt = Path("subagents/osint.py").read_text()
        assert "dominio" in osint_prompt.lower() or "domain" in osint_prompt.lower()
    
    def test_social_media(self):
        """Test de OSINT en redes sociales"""
        osint_prompt = Path("subagents/osint.py").read_text()
        assert "social" in osint_prompt.lower()
    
    def test_breach_data(self):
        """Test de busqueda en brechas"""
        osint_prompt = Path("subagents/osint.py").read_text()
        assert "brecha" in osint_prompt.lower() or "breach" in osint_prompt.lower()


class TestPostExploit:
    """Tests para subagente POST-EXPLOIT"""
    
    def test_privilege_escalation(self):
        """Test de escalada de privilegios"""
        post_prompt = Path("subagents/post_exploit.py").read_text()
        assert "escalada" in post_prompt.lower() or "privilege" in post_prompt.lower()
    
    def test_persistence(self):
        """Test de persistencia"""
        post_prompt = Path("subagents/post_exploit.py").read_text()
        assert "persistencia" in post_prompt.lower() or "persistence" in post_prompt.lower()
    
    def test_lateral_movement(self):
        """Test de movimiento lateral"""
        post_prompt = Path("subagents/post_exploit.py").read_text()
        assert "lateral" in post_prompt.lower()


class TestIntegration:
    """Tests de integracion completa"""
    
    def test_full_mission(self):
        """Test de mision completa"""
        # Verifica que todos los subagentes estan definidos
        from subagents import RECON_AGENT, EXPLOIT_AGENT, OSINT_AGENT, POST_EXPLOIT_AGENT, CYBER_WARFARE_AGENT
        
        assert RECON_AGENT is not None
        assert EXPLOIT_AGENT is not None
        assert OSINT_AGENT is not None
        assert POST_EXPLOIT_AGENT is not None
        assert CYBER_WARFARE_AGENT is not None
    
    def test_arnes_creation(self):
        """Test de creacion del arnes"""
        from arnes import create_arnes
        
        # No inicializar completamente, solo verificar que se puede crear
        # (requeriria Ollama corriendo)
        assert create_arnes is not None
    
    def test_prompt_exists(self):
        """Test de existencia del prompt raiz"""
        prompt_path = Path("prompts/orchestrator.txt")
        assert prompt_path.exists()
        content = prompt_path.read_text()
        assert "FSOCIETY" in content
        assert "subagente" in content.lower() or "subagent" in content.lower()
