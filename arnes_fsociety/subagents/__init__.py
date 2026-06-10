"""Subagentes especializados para operaciones de red team"""

from .recon import RECON_AGENT
from .exploit import EXPLOIT_AGENT
from .osint import OSINT_AGENT
from .post_exploit import POST_EXPLOIT_AGENT
from .cyber_warfare import CYBER_WARFARE_AGENT

__all__ = [
    "RECON_AGENT",
    "EXPLOIT_AGENT",
    "OSINT_AGENT",
    "POST_EXPLOIT_AGENT",
    "CYBER_WARFARE_AGENT",
]
