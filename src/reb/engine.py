"""Evidence-gated decision support; never claim business success is guaranteed."""
from collections import Counter
from decimal import Decimal
from .agents import select_agents
from .storage import Store
from .finance import investment_gate, money
from .evolution import skill_profile


def diagnose(store: Store, project_id: str, question: str = "") -> dict:
    project = store.get_project(project_id)
    sources = store.evidence(project_id)
    experiments = store.experiments(project_id)
    journal = store.journal(project_id)
    status_counts = dict(Counter(e["status"] for e in sources))
    verified = sum(e["status"] == "verified" for e in sources)
    completed = sum(e["state"] == "completed" for e in experiments)
    cash_in = sum((money(j["revenue"]) for j in journal), Decimal("0"))
    cash_out = sum((money(j["cost"]) for j in journal), Decimal("0"))
    stage = project["stage"]
    next_actions = []
    if not sources:
        next_actions.append("Investigar concorrentes e registar fontes para as principais hipóteses.")
    elif verified == 0:
        next_actions.append("Verificar as principais afirmações com fontes primárias.")
    if not experiments:
        next_actions.append("Definir uma hipótese falsificável e uma experiência comercial de baixo custo.")
    elif completed == 0:
        next_actions.append("Executar uma experiência e registar observações, não apenas opiniões.")
    if stage in {"launch", "operating", "scaling"}:
        next_actions.append("Rever margem de contribuição e caixa com dados reais de vendas e custos.")
    if not next_actions:
        next_actions.append("Rever dados recentes, identificar gargalo e escolher a próxima experiência.")
    return {
        "project": project,
        "selected_agents": select_agents(stage, question),
        "evidence_summary": {"total": len(sources), "verified_with_url": verified, "by_status": status_counts},
        "experiments": {"total": len(experiments), "completed": completed},
        "journal_totals": {"revenue_recorded": str(cash_in), "cost_recorded": str(cash_out), "net_recorded": str(cash_in - cash_out), "warning": "Registos fornecidos pelo utilizador, não comprovativos bancários."},
        "skills": skill_profile(store, project_id)["levels"],
        "next_actions": next_actions,
        "uncertainty": "Informação insuficiente não deve ser preenchida com dados inventados.",
        "success_guarantee": False,
    }


def recommend_experiment(project: dict, evidence_count: int) -> dict:
    stage = project["stage"]
    templates = {
        "idea": ("Pelo menos alguns potenciais clientes demonstram comportamento de compra.", "Compromissos de compra verificáveis", "Definir meta de validação antes de começar"),
        "validation": ("Um segmento está disposto a pagar pela oferta.", "Pedidos pagos ou compromissos confirmados", "Definir amostra e limiar antes de começar"),
        "launch": ("A oferta gera margem positiva após custos variáveis e aquisição.", "Margem por encomenda real", "Definir margem mínima antes de começar"),
        "operating": ("Uma intervenção resolve o gargalo operacional mais importante.", "Tempo/custo por serviço e conversão", "Definir melhoria mínima mensurável"),
        "scaling": ("Um novo canal é rentável sem prejudicar a qualidade.", "Custo de aquisição, margem e retenção", "Definir limite de custo e critério de paragem"),
    }
    h, m, t = templates[stage]
    return {"hypothesis_template": h, "metric": m, "target_instruction": t,
            "constraints": ["Começar com o teste reversível mais barato", "Medir comportamento real", "Obter consentimento para contactos e gastos", "Registar resultados negativos"],
            "evidence_count": evidence_count,
            "note": "Proposta de experiência, não evidência de viabilidade."}


def spending_review(store: Store, project_id: str, cost: str, approved: bool = False, action_type: str = "spend") -> dict:
    p = store.get_project(project_id)
    ev = store.evidence(project_id)
    return investment_gate(p["budget"], cost, sum(e["status"] == "verified" for e in ev), approved=approved, action_type=action_type)
