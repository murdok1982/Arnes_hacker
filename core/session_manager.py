import json
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional


DB_PATH = Path(__file__).parent.parent / "memory" / "sessions.db"


class SessionManager:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA busy_timeout=5000")
        return conn

    def _init_db(self):
        conn = self._get_conn()
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                mission TEXT NOT NULL,
                status TEXT DEFAULT 'active',
                created_at TEXT DEFAULT (datetime('now')),
                updated_at TEXT DEFAULT (datetime('now')),
                summary TEXT DEFAULT ''
            );
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                agent TEXT NOT NULL,
                content TEXT NOT NULL,
                content_type TEXT DEFAULT 'text',
                timestamp TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (session_id) REFERENCES sessions(id)
            );
            CREATE TABLE IF NOT EXISTS results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                agent TEXT NOT NULL,
                tool_name TEXT,
                result_text TEXT,
                output_json TEXT,
                success INTEGER DEFAULT 0,
                timestamp TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (session_id) REFERENCES sessions(id)
            );
            CREATE TABLE IF NOT EXISTS credentials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                target TEXT NOT NULL,
                username TEXT DEFAULT '',
                password TEXT DEFAULT '',
                hash TEXT DEFAULT '',
                service TEXT DEFAULT '',
                source TEXT DEFAULT 'manual',
                timestamp TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (session_id) REFERENCES sessions(id)
            );
            CREATE TABLE IF NOT EXISTS targets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                target TEXT NOT NULL,
                hostname TEXT DEFAULT '',
                ports TEXT DEFAULT '',
                os TEXT DEFAULT '',
                services TEXT DEFAULT '',
                notes TEXT DEFAULT '',
                timestamp TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (session_id) REFERENCES sessions(id)
            );
            CREATE TABLE IF NOT EXISTS playbooks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT DEFAULT '',
                agents TEXT NOT NULL,
                prompt_template TEXT DEFAULT '',
                created_at TEXT DEFAULT (datetime('now'))
            );
            """
        )
        conn.commit()
        conn.close()

    def create_session(self, mission: str) -> str:
        session_id = str(uuid.uuid4())[:8]
        conn = self._get_conn()
        conn.execute(
            "INSERT INTO sessions (id, mission) VALUES (?, ?)",
            (session_id, mission),
        )
        conn.commit()
        conn.close()
        return session_id

    def log(self, session_id: str, agent: str, content: str, content_type: str = "text"):
        conn = self._get_conn()
        conn.execute(
            "INSERT INTO logs (session_id, agent, content, content_type) VALUES (?, ?, ?, ?)",
            (session_id, agent, content, content_type),
        )
        conn.execute(
            "UPDATE sessions SET updated_at = datetime('now') WHERE id = ?",
            (session_id,),
        )
        conn.commit()
        conn.close()

    def save_result(
        self,
        session_id: str,
        agent: str,
        tool_name: Optional[str],
        result_text: str,
        success: bool = False,
        output_json: Optional[dict] = None,
    ):
        conn = self._get_conn()
        conn.execute(
            "INSERT INTO results (session_id, agent, tool_name, result_text, output_json, success) VALUES (?, ?, ?, ?, ?, ?)",
            (session_id, agent, tool_name, result_text, json.dumps(output_json) if output_json else None, int(success)),
        )
        conn.commit()
        conn.close()

    def get_session(self, session_id: str) -> Optional[dict]:
        conn = self._get_conn()
        row = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
        conn.close()
        if row:
            return dict(row)
        return None

    def get_logs(self, session_id: str, limit: int = 200) -> list[dict]:
        conn = self._get_conn()
        rows = conn.execute(
            "SELECT * FROM logs WHERE session_id = ? ORDER BY timestamp ASC LIMIT ?",
            (session_id, limit),
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_results(self, session_id: str) -> list[dict]:
        conn = self._get_conn()
        rows = conn.execute(
            "SELECT * FROM results WHERE session_id = ? ORDER BY timestamp ASC",
            (session_id,),
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_recent_sessions(self, limit: int = 20) -> list[dict]:
        conn = self._get_conn()
        rows = conn.execute(
            "SELECT id, mission, status, created_at, updated_at, summary FROM sessions ORDER BY updated_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def add_credential(self, session_id: str, target: str, username: str = "", password: str = "", hash_value: str = "", service: str = "", source: str = "manual"):
        conn = self._get_conn()
        conn.execute(
            "INSERT INTO credentials (session_id, target, username, password, hash, service, source) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (session_id, target, username, password, hash_value, service, source),
        )
        conn.commit()
        conn.close()

    def get_credentials(self, session_id: Optional[str] = None) -> list[dict]:
        conn = self._get_conn()
        if session_id:
            rows = conn.execute("SELECT * FROM credentials WHERE session_id = ? ORDER BY timestamp DESC", (session_id,)).fetchall()
        else:
            rows = conn.execute("SELECT * FROM credentials ORDER BY timestamp DESC LIMIT 100").fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def add_target(self, session_id: str, target: str, hostname: str = "", ports: str = "", os: str = "", services: str = ""):
        conn = self._get_conn()
        conn.execute(
            "INSERT INTO targets (session_id, target, hostname, ports, os, services) VALUES (?, ?, ?, ?, ?, ?)",
            (session_id, target, hostname, ports, os, services),
        )
        conn.commit()
        conn.close()

    def get_targets(self, session_id: Optional[str] = None) -> list[dict]:
        conn = self._get_conn()
        if session_id:
            rows = conn.execute("SELECT * FROM targets WHERE session_id = ? ORDER BY timestamp DESC", (session_id,)).fetchall()
        else:
            rows = conn.execute("SELECT * FROM targets ORDER BY timestamp DESC LIMIT 100").fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def add_playbook(self, name: str, description: str, agents: str, prompt_template: str = ""):
        conn = self._get_conn()
        conn.execute(
            "INSERT OR REPLACE INTO playbooks (name, description, agents, prompt_template) VALUES (?, ?, ?, ?)",
            (name, description, agents, prompt_template),
        )
        conn.commit()
        conn.close()

    def get_playbooks(self) -> list[dict]:
        conn = self._get_conn()
        rows = conn.execute("SELECT * FROM playbooks ORDER BY name ASC").fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def seed_default_playbooks(self):
        default_playbooks = [
            ("escaneo_completo", "Escaneo completo: puertos, servicios, vulnerabilidades", "recon", "Escanea a fondo {target}. Descubre todos los puertos, servicios, y vulnerabilidades."),
            ("compromiso_rapido", "Compromiso rapido: recon → exploit → post-exploit", "recon,exploit,post_exploit", "Compromete {target}. Escanea, explota vulnerabilidades, y escala privilegios."),
            ("osint_profundo", "OSINT profundo: recopila toda la informacion publica", "osint,recon", "Investiga {target} a fondo. Busca emails, subdominios, tecnologias, brechas."),
            ("pivoting_red", "Pivoting: compromete y move lateralmente en la red", "recon,exploit,post_exploit,pivoting", "Compromete {target} y usalo como pivot para escanear y atacar la red interna {subnet}."),
            ("payload_malware", "Genera payload personalizado con evasion", "malware,evasion", "Genera un payload ofuscado para {target} con tecnicas de evasion."),
            ("anonimo_total", "Modo anonimo: Tor + proxychains + evasion", "undercover,evasion", "Configura anonimizacion total y ejecuta todas las operaciones detras de Tor/proxychains."),
        ]
        for name, desc, agents, template in default_playbooks:
            self.add_playbook(name, desc, agents, template)

    def export_session_json(self, session_id: str) -> dict:
        session = self.get_session(session_id)
        logs = self.get_logs(session_id)
        results = self.get_results(session_id)
        creds = self.get_credentials(session_id)
        targets = self.get_targets(session_id)
        return {
            "session": session,
            "logs": logs,
            "results": results,
            "credentials": creds,
            "targets": targets,
            "exported_at": datetime.now().isoformat(),
        }

    def close_session(self, session_id: str, summary: str = ""):
        conn = self._get_conn()
        conn.execute(
            "UPDATE sessions SET status = 'completed', updated_at = datetime('now'), summary = ? WHERE id = ?",
            (summary[:500], session_id),
        )
        conn.commit()
        conn.close()
