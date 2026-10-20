"""Local persistent workspace: SQLite, without any third-party dependencies."""
from __future__ import annotations
import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from .errors import REBError


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def workspace_path() -> Path:
    return Path(os.environ.get("REB_DB_PATH", str(Path.home() / ".reb" / "projects.sqlite3"))).expanduser()


class Store:
    def __init__(self, path: str | Path | None = None):
        self.path = Path(path).expanduser() if path else workspace_path()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(str(self.path))
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA foreign_keys=ON")
        self.db.executescript("""
        CREATE TABLE IF NOT EXISTS projects(
          id TEXT PRIMARY KEY, name TEXT NOT NULL, idea TEXT NOT NULL,
          market TEXT NOT NULL, stage TEXT NOT NULL, budget TEXT NOT NULL,
          objective TEXT NOT NULL, created_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS evidence(
          id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES projects(id),
          claim TEXT NOT NULL, url TEXT, status TEXT NOT NULL,
          source_type TEXT NOT NULL, notes TEXT NOT NULL, collected_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS experiments(
          id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES projects(id),
          hypothesis TEXT NOT NULL, metric TEXT NOT NULL, target TEXT NOT NULL,
          cap TEXT NOT NULL, state TEXT NOT NULL, observed TEXT,
          created_at TEXT NOT NULL, updated_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS journal(
          id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES projects(id),
          kind TEXT NOT NULL, body TEXT NOT NULL, revenue TEXT NOT NULL,
          cost TEXT NOT NULL, customers INTEGER NOT NULL, created_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS learning(
          id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES projects(id),
          topic TEXT NOT NULL, level INTEGER NOT NULL, demonstration TEXT NOT NULL,
          created_at TEXT NOT NULL);
        CREATE INDEX IF NOT EXISTS idx_evidence_project ON evidence(project_id);
        CREATE INDEX IF NOT EXISTS idx_experiments_project ON experiments(project_id);
        CREATE INDEX IF NOT EXISTS idx_journal_project ON journal(project_id);
        CREATE TABLE IF NOT EXISTS delegations(
          id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES projects(id),
          provider TEXT NOT NULL, tool TEXT NOT NULL, request_json TEXT NOT NULL,
          result_json TEXT NOT NULL, status TEXT NOT NULL, created_at TEXT NOT NULL);
        CREATE INDEX IF NOT EXISTS idx_delegations_project ON delegations(project_id);
        CREATE INDEX IF NOT EXISTS idx_learning_project ON learning(project_id);
        """)
        self.db.commit()

    def close(self):
        self.db.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    def add_project(self, name: str, idea: str, market: str = "Portugal", stage: str = "idea", budget: str = "0", objective: str = "Validar procura") -> dict:
        if not name.strip() or not idea.strip():
            raise REBError("Nome e ideia são obrigatórios.")
        if stage not in {"idea", "validation", "launch", "operating", "scaling"}:
            raise REBError("Etapa inválida.")
        from .finance import money
        money(budget, allow_negative=False)
        p = {"id": uuid4().hex[:12], "name": name.strip(), "idea": idea.strip(), "market": market.strip(), "stage": stage, "budget": str(budget), "objective": objective.strip(), "created_at": utcnow()}
        self.db.execute("INSERT INTO projects VALUES (?,?,?,?,?,?,?,?)", tuple(p.values()))
        self.db.commit()
        return p

    def get_project(self, project_id: str) -> dict:
        row = self.db.execute("SELECT * FROM projects WHERE id=?", (project_id,)).fetchone()
        if not row:
            raise REBError(f"Projeto desconhecido: {project_id}")
        return dict(row)

    def list_projects(self) -> list[dict]:
        return [dict(r) for r in self.db.execute("SELECT * FROM projects ORDER BY created_at DESC")]

    def add_evidence(self, project_id: str, claim: str, url: str = "", status: str = "unverified", source_type: str = "web", notes: str = "") -> dict:
        self.get_project(project_id)
        if not claim.strip():
            raise REBError("A afirmação não pode estar vazia.")
        if status not in {"verified", "inferred", "unverified", "contradicted"}:
            raise REBError("Classificação de evidência inválida.")
        if url:
            from urllib.parse import urlsplit
            p = urlsplit(url)
            if p.scheme not in {"https", "http"} or not p.netloc or p.username or p.password:
                raise REBError("Fonte deve ter URL HTTP(S) válido e sem credenciais.")
        if status == "verified" and not url:
            raise REBError("Uma evidência verificada exige ligação para a fonte.")
        row = {"id": uuid4().hex[:12], "project_id": project_id, "claim": claim.strip(), "url": url, "status": status, "source_type": source_type, "notes": notes, "collected_at": utcnow()}
        self.db.execute("INSERT INTO evidence VALUES (?,?,?,?,?,?,?,?)", tuple(row.values()))
        self.db.commit()
        return row

    def evidence(self, project_id: str) -> list[dict]:
        self.get_project(project_id)
        return [dict(r) for r in self.db.execute("SELECT * FROM evidence WHERE project_id=? ORDER BY collected_at DESC", (project_id,))]

    def add_experiment(self, project_id: str, hypothesis: str, metric: str, target: str, cap: str = "0") -> dict:
        self.get_project(project_id)
        from .finance import money
        money(cap, allow_negative=False)
        if not all(s.strip() for s in [hypothesis, metric, target]):
            raise REBError("Hipótese, métrica e meta são obrigatórios.")
        row = {"id": uuid4().hex[:12], "project_id": project_id, "hypothesis": hypothesis, "metric": metric, "target": target, "cap": str(cap), "state": "planned", "observed": None, "created_at": utcnow(), "updated_at": utcnow()}
        self.db.execute("INSERT INTO experiments VALUES (?,?,?,?,?,?,?,?,?,?)", tuple(row.values()))
        self.db.commit()
        return row

    def set_experiment_result(self, experiment_id: str, observed: str, state: str) -> dict:
        if state not in {"completed", "inconclusive", "stopped"}:
            raise REBError("Estado da experiência inválido.")
        if not observed.strip():
            raise REBError("O resultado observado é obrigatório.")
        cursor = self.db.execute("UPDATE experiments SET observed=?,state=?,updated_at=? WHERE id=?", (observed.strip(), state, utcnow(), experiment_id))
        if cursor.rowcount != 1:
            raise REBError("Experiência não encontrada.")
        self.db.commit()
        return dict(self.db.execute("SELECT * FROM experiments WHERE id=?", (experiment_id,)).fetchone())

    def experiments(self, project_id: str) -> list[dict]:
        self.get_project(project_id)
        return [dict(r) for r in self.db.execute("SELECT * FROM experiments WHERE project_id=? ORDER BY created_at DESC", (project_id,))]

    def add_journal(self, project_id: str, body: str, kind: str = "activity", revenue: str = "0", cost: str = "0", customers: int = 0) -> dict:
        self.get_project(project_id)
        from .finance import money
        money(revenue, allow_negative=False)
        money(cost, allow_negative=False)
        if not body.strip():
            raise REBError("Entrada do diário vazia.")
        if kind not in {"activity", "decision", "result", "lesson"}:
            raise REBError("Tipo de entrada inválido.")
        if not isinstance(customers, int) or customers < 0:
            raise REBError("Número de clientes inválido.")
        row = {"id": uuid4().hex[:12], "project_id": project_id, "kind": kind, "body": body.strip(), "revenue": str(revenue), "cost": str(cost), "customers": customers, "created_at": utcnow()}
        self.db.execute("INSERT INTO journal VALUES (?,?,?,?,?,?,?,?)", tuple(row.values()))
        self.db.commit()
        return row

    def journal(self, project_id: str) -> list[dict]:
        self.get_project(project_id)
        return [dict(r) for r in self.db.execute("SELECT * FROM journal WHERE project_id=? ORDER BY created_at ASC, rowid ASC", (project_id,))]

    def add_learning(self, project_id: str, topic: str, level: int, demonstration: str) -> dict:
        self.get_project(project_id)
        if topic not in {"finance", "sales", "marketing", "operations", "strategy", "leadership", "validation"}:
            raise REBError("Área de aprendizagem inválida.")
        if not isinstance(level, int) or not 0 <= level <= 4:
            raise REBError("Nível deve estar entre 0 e 4.")
        if not demonstration.strip():
            raise REBError("É necessário registar evidência da competência.")
        row = {"id": uuid4().hex[:12], "project_id": project_id, "topic": topic, "level": level, "demonstration": demonstration.strip(), "created_at": utcnow()}
        self.db.execute("INSERT INTO learning VALUES (?,?,?,?,?,?)", tuple(row.values()))
        self.db.commit()
        return row

    def learning(self, project_id: str) -> list[dict]:
        self.get_project(project_id)
        return [dict(r) for r in self.db.execute("SELECT * FROM learning WHERE project_id=? ORDER BY created_at ASC, rowid ASC", (project_id,))]

    def add_delegation(self, project_id: str, provider: str, tool: str, arguments: dict, result: dict) -> dict:
        """Store an external execution receipt, not automatically evidence of truth.

        Caller is responsible for completing explicit authorization and execution.
        """
        self.get_project(project_id)
        if not provider.strip() or not tool.strip() or not isinstance(arguments, dict) or not isinstance(result, dict):
            raise REBError("Registo de delegação inválido")
        # Do not persist raw arguments or response: they may contain secrets or PII.
        row = {"id": uuid4().hex[:12], "project_id": project_id, "provider": provider,
               "tool": tool, "request_json": json.dumps({"argument_keys": list(arguments)}, ensure_ascii=False),
               "result_json": json.dumps({"isError": result.get("isError", False), "content_types":
                  [x.get("type", "unknown") for x in result.get("content", []) if isinstance(x, dict)]}, ensure_ascii=False),
               "status": "remote_error" if result.get("isError") else "completed_unverified",
               "created_at": utcnow()}
        self.db.execute("INSERT INTO delegations VALUES (?,?,?,?,?,?,?,?)", tuple(row.values()))
        self.db.commit()
        return {**row, "request": json.loads(row["request_json"]), "result_summary": json.loads(row["result_json"])}

    def delegations(self, project_id: str) -> list[dict]:
        self.get_project(project_id)
        return [dict(r) for r in self.db.execute("SELECT * FROM delegations WHERE project_id=? ORDER BY created_at, rowid", (project_id,))]

    def export(self, project_id: str) -> dict:
        return {"project": self.get_project(project_id), "evidence": self.evidence(project_id), "experiments": self.experiments(project_id), "journal": self.journal(project_id), "learning": self.learning(project_id), "delegations": self.delegations(project_id)}
