"""
State Store Backend - Memoria Persistente de Operaciones
Sistema de memoria para almacenar conocimiento de operaciones, IoCs, y lecciones aprendidas
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Literal

from langgraph.store.base import BaseStore, Item, SearchItem


class StateStoreBackend(BaseStore):
    """
    Backend de memoria persistente para operaciones de red team.
    
    Almacena:
    - Conocimiento de operaciones anteriores
    - IoCs (Indicadores de Compromiso)
    - Tecnicas exitosas por objetivo
    - Lecciones aprendidas
    - Herramientas y payloads efectivos
    """
    
    def __init__(
        self,
        backend_type: str = "sqlite",
        redis_url: str = "redis://localhost:6379",
        persistence_path: Path | None = None,
    ):
        super().__init__()
        self.backend_type = backend_type
        self.redis_url = redis_url
        self.persistence_path = persistence_path or Path("./memory/operations.db")
        
        self.persistence_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self) -> None:
        """Inicializa la base de datos SQLite"""
        with sqlite3.connect(self.persistence_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS operations (
                    id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    mission TEXT NOT NULL,
                    target TEXT,
                    status TEXT,
                    result TEXT,
                    metadata TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS iocs (
                    id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    type TEXT NOT NULL,
                    value TEXT NOT NULL,
                    context TEXT,
                    severity TEXT,
                    source_operation TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS techniques (
                    id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    success_rate REAL,
                    target_type TEXT,
                    notes TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS knowledge_base (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    namespace TEXT DEFAULT 'default'
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS lessons_learned (
                    id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    operation_id TEXT,
                    lesson TEXT NOT NULL,
                    category TEXT,
                    applicability TEXT
                )
            """)
    
    def put(
        self,
        namespace: tuple[str, ...],
        key: str,
        value: dict[str, Any],
        index: Literal[False] | list[str] | None = None,
        *,
        ttl: float | None = None,
    ) -> None:
        """
        Almacena un valor en la memoria.
        
        Args:
            namespace: Tupla de strings (categoria, subcategoria, ...)
            key: Clave unica
            value: Valor a almacenar
            index: Parametro de indexacion (no usado en esta implementacion)
            ttl: Time-to-live en segundos (no usado en esta implementacion)
        """
        ns_str = ":".join(namespace)
        timestamp = datetime.utcnow().isoformat()
        
        with sqlite3.connect(self.persistence_path) as conn:
            if namespace[0] == "operation":
                conn.execute(
                    """INSERT OR REPLACE INTO operations 
                       (id, timestamp, mission, target, status, result, metadata)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (
                        key,
                        timestamp,
                        value.get("mission", ""),
                        value.get("target", ""),
                        value.get("status", ""),
                        json.dumps(value.get("result", {})),
                        json.dumps(value.get("metadata", {})),
                    ),
                )
            
            elif namespace[0] == "ioc":
                conn.execute(
                    """INSERT OR REPLACE INTO iocs
                       (id, timestamp, type, value, context, severity, source_operation)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (
                        key,
                        timestamp,
                        value.get("type", ""),
                        value.get("value", ""),
                        json.dumps(value.get("context", {})),
                        value.get("severity", "medium"),
                        value.get("source_operation", ""),
                    ),
                )
            
            elif namespace[0] == "technique":
                conn.execute(
                    """INSERT OR REPLACE INTO techniques
                       (id, timestamp, name, category, success_rate, target_type, notes)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (
                        key,
                        timestamp,
                        value.get("name", ""),
                        value.get("category", ""),
                        value.get("success_rate", 0.0),
                        value.get("target_type", ""),
                        value.get("notes", ""),
                    ),
                )
            
            elif namespace[0] == "lesson":
                conn.execute(
                    """INSERT OR REPLACE INTO lessons_learned
                       (id, timestamp, operation_id, lesson, category, applicability)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (
                        key,
                        timestamp,
                        value.get("operation_id", ""),
                        value.get("lesson", ""),
                        value.get("category", ""),
                        value.get("applicability", ""),
                    ),
                )
            
            else:
                conn.execute(
                    """INSERT OR REPLACE INTO knowledge_base
                       (key, value, timestamp, namespace)
                       VALUES (?, ?, ?, ?)""",
                    (key, json.dumps(value), timestamp, ns_str),
                )
    
    def get(
        self,
        namespace: tuple[str, ...],
        key: str,
        *,
        refresh_ttl: bool | None = None,
    ) -> Item | None:
        """
        Obtiene un valor de la memoria.
        
        Args:
            namespace: Tupla de strings (categoria, subcategoria, ...)
            key: Clave unica
            refresh_ttl: Si debe refrescar el TTL (no usado en esta implementacion)
        
        Returns:
            Item con el valor o None
        """
        with sqlite3.connect(self.persistence_path) as conn:
            conn.row_factory = sqlite3.Row
            
            if namespace[0] == "operation":
                row = conn.execute(
                    "SELECT * FROM operations WHERE id = ?", (key,)
                ).fetchone()
                if row:
                    value = {
                        "id": row["id"],
                        "timestamp": row["timestamp"],
                        "mission": row["mission"],
                        "target": row["target"],
                        "status": row["status"],
                        "result": json.loads(row["result"]),
                        "metadata": json.loads(row["metadata"]),
                    }
                    return Item(
                        value=value,
                        key=key,
                        namespace=namespace,
                        created_at=row["timestamp"],
                        updated_at=row["timestamp"],
                    )
            
            elif namespace[0] == "ioc":
                row = conn.execute(
                    "SELECT * FROM iocs WHERE id = ?", (key,)
                ).fetchone()
                if row:
                    value = {
                        "id": row["id"],
                        "timestamp": row["timestamp"],
                        "type": row["type"],
                        "value": row["value"],
                        "context": json.loads(row["context"]),
                        "severity": row["severity"],
                        "source_operation": row["source_operation"],
                    }
                    return Item(
                        value=value,
                        key=key,
                        namespace=namespace,
                        created_at=row["timestamp"],
                        updated_at=row["timestamp"],
                    )
            
            elif namespace[0] == "technique":
                row = conn.execute(
                    "SELECT * FROM techniques WHERE id = ?", (key,)
                ).fetchone()
                if row:
                    value = {
                        "id": row["id"],
                        "timestamp": row["timestamp"],
                        "name": row["name"],
                        "category": row["category"],
                        "success_rate": row["success_rate"],
                        "target_type": row["target_type"],
                        "notes": row["notes"],
                    }
                    return Item(
                        value=value,
                        key=key,
                        namespace=namespace,
                        created_at=row["timestamp"],
                        updated_at=row["timestamp"],
                    )
            
            elif namespace[0] == "lesson":
                row = conn.execute(
                    "SELECT * FROM lessons_learned WHERE id = ?", (key,)
                ).fetchone()
                if row:
                    value = {
                        "id": row["id"],
                        "timestamp": row["timestamp"],
                        "operation_id": row["operation_id"],
                        "lesson": row["lesson"],
                        "category": row["category"],
                        "applicability": row["applicability"],
                    }
                    return Item(
                        value=value,
                        key=key,
                        namespace=namespace,
                        created_at=row["timestamp"],
                        updated_at=row["timestamp"],
                    )
            
            else:
                ns_str = ":".join(namespace)
                row = conn.execute(
                    "SELECT * FROM knowledge_base WHERE key = ? AND namespace = ?",
                    (key, ns_str),
                ).fetchone()
                if row:
                    value = json.loads(row["value"])
                    return Item(
                        value=value,
                        key=key,
                        namespace=namespace,
                        created_at=row["timestamp"],
                        updated_at=row["timestamp"],
                    )
        
        return None
    
    def search(
        self,
        namespace_prefix: tuple[str, ...],
        /,
        *,
        query: str | None = None,
        filter: dict[str, Any] | None = None,
        limit: int = 10,
        offset: int = 0,
        refresh_ttl: bool | None = None,
    ) -> list[SearchItem]:
        """
        Busca valores en la memoria.
        
        Args:
            namespace_prefix: Prefijo de namespace a buscar
            query: String de busqueda (no usado en esta implementacion)
            filter: Filtros adicionales (no usado en esta implementacion)
            limit: Limite de resultados
            offset: Offset para paginacion
            refresh_ttl: Si debe refrescar el TTL (no usado en esta implementacion)
        
        Returns:
            Lista de SearchItem encontrados
        """
        results = []
        
        with sqlite3.connect(self.persistence_path) as conn:
            conn.row_factory = sqlite3.Row
            
            if namespace_prefix[0] == "operation":
                rows = conn.execute(
                    f"SELECT * FROM operations ORDER BY timestamp DESC LIMIT {limit} OFFSET {offset}"
                ).fetchall()
                for row in rows:
                    value = {
                        "id": row["id"],
                        "timestamp": row["timestamp"],
                        "mission": row["mission"],
                        "target": row["target"],
                        "status": row["status"],
                        "result": json.loads(row["result"]),
                        "metadata": json.loads(row["metadata"]),
                    }
                    results.append(SearchItem(
                        value=value,
                        key=row["id"],
                        namespace=namespace_prefix,
                        created_at=row["timestamp"],
                        updated_at=row["timestamp"],
                    ))
            
            elif namespace_prefix[0] == "ioc":
                rows = conn.execute(
                    f"SELECT * FROM iocs ORDER BY timestamp DESC LIMIT {limit} OFFSET {offset}"
                ).fetchall()
                for row in rows:
                    value = {
                        "id": row["id"],
                        "timestamp": row["timestamp"],
                        "type": row["type"],
                        "value": row["value"],
                        "context": json.loads(row["context"]),
                        "severity": row["severity"],
                        "source_operation": row["source_operation"],
                    }
                    results.append(SearchItem(
                        value=value,
                        key=row["id"],
                        namespace=namespace_prefix,
                        created_at=row["timestamp"],
                        updated_at=row["timestamp"],
                    ))
            
            elif namespace_prefix[0] == "technique":
                rows = conn.execute(
                    f"SELECT * FROM techniques ORDER BY success_rate DESC LIMIT {limit} OFFSET {offset}"
                ).fetchall()
                for row in rows:
                    value = {
                        "id": row["id"],
                        "timestamp": row["timestamp"],
                        "name": row["name"],
                        "category": row["category"],
                        "success_rate": row["success_rate"],
                        "target_type": row["target_type"],
                        "notes": row["notes"],
                    }
                    results.append(SearchItem(
                        value=value,
                        key=row["id"],
                        namespace=namespace_prefix,
                        created_at=row["timestamp"],
                        updated_at=row["timestamp"],
                    ))
            
            elif namespace_prefix[0] == "lesson":
                rows = conn.execute(
                    f"SELECT * FROM lessons_learned ORDER BY timestamp DESC LIMIT {limit} OFFSET {offset}"
                ).fetchall()
                for row in rows:
                    value = {
                        "id": row["id"],
                        "timestamp": row["timestamp"],
                        "operation_id": row["operation_id"],
                        "lesson": row["lesson"],
                        "category": row["category"],
                        "applicability": row["applicability"],
                    }
                    results.append(SearchItem(
                        value=value,
                        key=row["id"],
                        namespace=namespace_prefix,
                        created_at=row["timestamp"],
                        updated_at=row["timestamp"],
                    ))
            
            else:
                ns_prefix = ":".join(namespace_prefix)
                rows = conn.execute(
                    f"SELECT * FROM knowledge_base WHERE namespace LIKE ? ORDER BY timestamp DESC LIMIT {limit} OFFSET {offset}",
                    (f"{ns_prefix}%",),
                ).fetchall()
                for row in rows:
                    value = json.loads(row["value"])
                    ns_parts = tuple(row["namespace"].split(":"))
                    results.append(SearchItem(
                        value=value,
                        key=row["key"],
                        namespace=ns_parts,
                        created_at=row["timestamp"],
                        updated_at=row["timestamp"],
                    ))
        
        return results
    
    def delete(self, namespace: tuple[str, ...], key: str) -> None:
        """Elimina un valor de la memoria"""
        with sqlite3.connect(self.persistence_path) as conn:
            if namespace[0] == "operation":
                conn.execute("DELETE FROM operations WHERE id = ?", (key,))
            elif namespace[0] == "ioc":
                conn.execute("DELETE FROM iocs WHERE id = ?", (key,))
            elif namespace[0] == "technique":
                conn.execute("DELETE FROM techniques WHERE id = ?", (key,))
            elif namespace[0] == "lesson":
                conn.execute("DELETE FROM lessons_learned WHERE id = ?", (key,))
            else:
                ns_str = ":".join(namespace)
                conn.execute(
                    "DELETE FROM knowledge_base WHERE key = ? AND namespace = ?",
                    (key, ns_str),
                )
    
    def batch(
        self,
        ops: list[tuple[str, tuple[str, ...], str, dict[str, Any]]],
    ) -> list[Any]:
        """
        Ejecuta multiples operaciones en batch.
        
        Args:
            ops: Lista de tuplas (operacion, namespace, key, value)
                 operacion: "put" o "delete"
        
        Returns:
            Lista de resultados
        """
        results = []
        for op in ops:
            operation, namespace, key, value = op
            if operation == "put":
                self.put(namespace, key, value)
                results.append(None)
            elif operation == "delete":
                self.delete(namespace, key)
                results.append(None)
            else:
                results.append(None)
        return results
    
    async def abatch(
        self,
        ops: list[tuple[str, tuple[str, ...], str, dict[str, Any]]],
    ) -> list[Any]:
        """Version asincrona de batch"""
        return self.batch(ops)
