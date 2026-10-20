"""Discover local skills and build explicit delegation requests.

No arbitrary code execution, no automatic REA/RES install, no invisible external actions.
"""
from dataclasses import dataclass, asdict
from pathlib import Path
from .errors import REBError

CAPABILITIES = {
    "rea": {"name": "Reverse Engineer Anything", "type": "external_mcp", "status": "not_configured", "purpose": "technical reconnaissance of authorized applications", "requires": "rea-agents setup and MCP server available to the host"},
    "res": {"name": "Reverse Engineering SaaS", "type": "external_skill", "status": "not_configured", "purpose": "document observable SaaS behavior", "requires": "RES skill installed in compatible agent"},
    "market_research": {"name": "Market research", "type": "internal", "status": "available", "purpose": "record evidence, optional Tavily discovery", "requires": "optional TAVILY_API_KEY"},
    "business_core": {"name": "REB Core", "type": "internal", "status": "available", "purpose": "diagnose, finance, journal, evolution", "requires": "none"},
}


def discover_skills(root: str | Path) -> list[dict]:
    root = Path(root)
    if not root.exists():
        return []
    found = []
    for path in sorted(root.glob("*/SKILL.md")):
        # Metadata discovery only; do not execute instructions from untrusted skills automatically.
        name = path.parent.name
        found.append({"name": name, "path": str(path.resolve()), "load_policy": "read_only_until_user_or_host_approves"})
    return found


def make_delegation(provider: str, objective: str, *, evidence: list[dict] | None = None, approved: bool = False) -> dict:
    if provider not in CAPABILITIES:
        raise REBError(f"Capacidade desconhecida: {provider}")
    if not objective.strip():
        raise REBError("É necessário definir um objetivo de delegação.")
    c = CAPABILITIES[provider]
    return {"provider": provider, "provider_kind": c["type"], "objective": objective.strip(),
            "evidence_refs": [e["id"] for e in (evidence or []) if "id" in e],
            "requires_explicit_approval": c["type"].startswith("external"),
            "approved": approved,
            "execution_status": "prepared_not_executed",
            "expected_output": ["artifacts", "source_links", "limitations", "execution_status"],
            "instructions": "Delegação é apenas preparada; executar num host com a ferramenta instalada e autorizada."}
