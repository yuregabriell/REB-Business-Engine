"""Multi-specialist consultation with a required skeptical audit.

No unattended external actions. This action calls a model provider only after an
operator explicitly configures model credentials and invokes it.
"""
from .agents import AGENT_MAP, select_agents
from .engine import diagnose
from .provider import consult_agent, model_config
from .storage import Store
from .errors import REBError


def run_mission(store: Store, project_id: str, goal: str, max_agents: int = 4) -> dict:
    if not goal.strip(): raise REBError("Objetivo da missão vazio.")
    if not 2 <= max_agents <= 8: raise REBError("max_agents precisa ser entre 2 e 8.")
    model_config()  # Fail before taking any external action if not configured.
    diagnostic = diagnose(store, project_id, goal)
    routed = [a["key"] for a in select_agents(diagnostic["project"]["stage"], goal)]
    # Always challenge outcomes: auditor is last, even under maximum-agent cap.
    chosen = [a for a in routed if a not in {"orchestrator", "auditor"}][:max_agents - 2]
    chosen = ["orchestrator"] + chosen + ["auditor"]
    reports = []
    for key in chosen:
        prior = [{"agent": r["agent"], "draft": r["content"][:6500]} for r in reports]
        context = {"diagnosis": diagnostic, "previous_drafts": prior}
        task = goal + ("\nReview all prior proposals skeptically, cite unsupported claims, and identify falsifying tests." if key == "auditor" else "")
        report = consult_agent(key, task, context)
        reports.append(report)
    return {"project_id": project_id, "goal": goal, "agents_consulted": chosen,
            "reports": reports, "state": "draft_requires_evidence_validation",
            "note": "Os relatórios não equivalem a validação de mercado, autorização de despesas ou execução de tarefas."}
