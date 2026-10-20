"""Evidence-aware project playbook; no invented demand or unsourced figures."""
from .engine import diagnose, recommend_experiment
from .knowledge import find_methods
from .storage import Store

_STEPS = {
    "idea": ("Identificar perfil e problema do cliente", "Mapear alternativas e concorrentes locais", "Conduzir entrevistas centradas em acontecimentos reais", "Testar compromisso comercial antes de construir"),
    "validation": ("Definir oferta e preço de teste", "Executar experiência comercial com limite de custo", "Registar respostas, vendas e rejeições", "Rever decisão com base na evidência"),
    "launch": ("Preparar processo operacional e qualidade", "Verificar requisitos legais aplicáveis", "Confirmar margem por venda e caixa", "Realizar aquisição e entrega piloto"),
    "operating": ("Organizar números por produto e canal", "Identificar o principal gargalo", "Experimentar melhoria controlada", "Comparar margem e satisfação"),
    "scaling": ("Verificar economia unitária estável", "Experimentar novo canal em pequena escala", "Verificar capacidade e qualidade", "Investir gradualmente mediante resultados"),
}


def build_blueprint(store: Store, project_id: str, goal: str = "") -> dict:
    diagnosis = diagnose(store, project_id, goal)
    p = diagnosis["project"]
    ev = store.evidence(project_id)
    exp = store.experiments(project_id)
    verified = [e for e in ev if e["status"] == "verified"]
    stage = p["stage"]
    methods = find_methods(" ".join([goal, stage, p["idea"]]) or stage, stage=stage, limit=3)
    if not methods:
        methods = find_methods("", limit=3)
    tasks = []
    for i, title in enumerate(_STEPS[stage], 1):
        tasks.append({"order": i, "task": title, "status": "recommended_not_executed", "owner": "user_and_REB", "proof_required": True})
    return {
        "project_id": project_id, "goal": goal or p["objective"], "stage": stage,
        "basis": {"verified_claims_user_marked": len(verified), "unverified_claims": len(ev)-len(verified), "experiments": len(exp), "source_links": [e["url"] for e in verified if e["url"]][:10]},
        "recommended_specialists": [a["key"] for a in diagnosis["selected_agents"]],
        "tasks": tasks,
        "next_experiment": recommend_experiment(p, len(ev)),
        "methods": methods,
        "decision_gate": {"before_spend": "Confirmar orçamento, evidências, autorização e alternativa reversível.", "before_launch": "Verificar obrigações legais, capacidade e métricas de qualidade."},
        "unknowns": ["Dimensão real da procura", "Disposição para pagar", "Concorrência regional", "Custos completos e licenças aplicáveis"],
        "risk_notice": "Plano inicial determinístico, não investigação realizada nem promessa de sucesso. URLs marcadas como verificadas não foram auditadas automaticamente.",
    }
