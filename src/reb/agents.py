"""Agent capabilities and routing; each role also has an installable Agent Skill."""
from dataclasses import dataclass

@dataclass(frozen=True)
class Agent:
    key: str
    title: str
    mission: str
    outputs: tuple[str, ...]

AGENTS = (
    Agent("orchestrator", "CEO Orchestrator", "Coordinate goals, constraints, experts, priorities and decisions.", ("next_action", "decision_log")),
    Agent("market", "Market Research", "Research competitors, market segments and demand; cite every material claim.", ("competitor_map", "sources")),
    Agent("customers", "Customer Intelligence", "Identify customer problems and buying behavior; distinguish anecdotes from demonstrated demand.", ("segments", "interview_plan")),
    Agent("validation", "Business Validator", "Design cheap, ethical, falsifiable commercial experiments.", ("hypotheses", "experiments")),
    Agent("finance", "Financial Director", "Compute unit economics, cash flow and uncertainty with deterministic tools.", ("scenario", "risk_notes")),
    Agent("offers", "Offer Architect", "Design offers, pricing tests and differentiated value propositions.", ("offer", "pricing_hypotheses")),
    Agent("operations", "Operations Director", "Design realistic staffing, fulfillment, suppliers and service procedures.", ("process_map", "capacity_plan")),
    Agent("regulatory", "Regulatory Specialist", "Find location and industry-specific obligations with official sources; escalate professional advice.", ("compliance_checklist", "unknowns")),
    Agent("marketing", "Marketing Director", "Design measured customer-acquisition channels and compliant campaigns.", ("campaign_tests", "channel_plan")),
    Agent("sales", "Sales Director", "Improve prospect qualification, sales conversations, proposals and conversion measurement.", ("pipeline_plan", "followups")),
    Agent("growth", "Growth Analyst", "Diagnose revenue, retention, acquisition cost and marginal returns.", ("metrics", "experiments")),
    Agent("auditor", "Strategic Auditor", "Challenge assumptions, detect fabricated evidence and counterarguments.", ("counterevidence", "risk_assessment")),
    Agent("knowledge", "Knowledge Scientist", "Select context-appropriate methods from credible scientific and field sources.", ("method_card", "evidence_grade")),
    Agent("evolution", "Evolution Mentor", "Explain and scaffold practical business competence at the user's demonstrated level.", ("teaching_moment", "learning_goal")),
)
AGENT_MAP = {a.key: a for a in AGENTS}

ROUTING = {
    "idea": ("orchestrator", "market", "customers", "validation", "finance", "auditor", "evolution"),
    "validation": ("orchestrator", "market", "customers", "validation", "offers", "sales", "finance", "auditor"),
    "launch": ("orchestrator", "operations", "regulatory", "offers", "marketing", "sales", "finance", "auditor"),
    "operating": ("orchestrator", "finance", "operations", "sales", "growth", "auditor", "evolution"),
    "scaling": ("orchestrator", "growth", "finance", "operations", "marketing", "auditor", "knowledge"),
}


def select_agents(stage: str, question: str = "") -> list[dict]:
    ordered = list(ROUTING.get(stage, ROUTING["idea"]))
    words = question.lower()
    for triggers, key in (
        (("software", "app", "saas", "aplicação", "site"), "operations"),
        (("legislação", "licença", "imposto", "regra", "legal"), "regulatory"),
        (("aprender", "explica", "não entendo", "iniciante"), "evolution"),
        (("pesquisa", "estudo", "livro", "ciência"), "knowledge"),
        (("vendas", "clientes", "negociar"), "sales"),
    ):
        if any(w in words for w in triggers) and key not in ordered:
            ordered.insert(-1, key)
    return [{"key": key, "name": AGENT_MAP[key].title, "mission": AGENT_MAP[key].mission, "outputs": list(AGENT_MAP[key].outputs)} for key in ordered]
