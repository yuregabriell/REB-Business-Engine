"""Demonstrated learning, not arbitrary XP from chat volume."""
from .storage import Store


def skill_profile(store: Store, project_id: str) -> dict:
    history = store.learning(project_id)
    levels = {k: 0 for k in ("finance", "sales", "marketing", "operations", "strategy", "leadership", "validation")}
    demonstrations = {}
    for row in history:
        # Most recent demonstrated level is the current level. A regression is possible.
        levels[row["topic"]] = row["level"]
        demonstrations[row["topic"]] = row["demonstration"]
    return {"project_id": project_id, "levels": levels, "demonstrations": demonstrations,
            "note": "Níveis são registos de competências demonstradas, não diagnósticos psicológicos."}


def adaptive_explanation(topic: str, level: int) -> dict:
    if level < 0 or level > 4:
        raise ValueError("level must be 0..4")
    glossary = {
        "finance": ("Quanto entra e quanto sai do teu negócio.", "Receita menos custos variáveis e fixos.", "Margem de contribuição, break-even e cash flow.", "Análise de sensibilidade e retorno ajustado ao risco.", "Otimização de capital e estrutura económica por segmento."),
        "validation": ("Vamos perceber se alguém pagaria pela ideia.", "Definimos uma hipótese e um teste pequeno.", "Desenhamos testes falsificáveis com critérios de decisão.", "Comparamos força de evidência e custo experimental.", "Desenhamos portfólio de experimentos e decisões sequenciais."),
        "sales": ("Vamos encontrar pessoas interessadas no serviço.", "Vamos organizar contactos e acompanhar respostas.", "Vamos medir a conversão por etapa do funil.", "Vamos analisar ciclo de vendas e retenção.", "Vamos otimizar LTV/CAC por segmento e canal."),
    }
    entries = glossary.get(topic, ("Comecemos pelas bases.", "Vamos aplicar o conceito.", "Analisemos os indicadores.", "Comparemos diferentes cenários.", "Otimizemos a estratégia com evidências."))
    return {"topic": topic, "level": level, "explanation": entries[level], "preference": "O utilizador pode sempre pedir mais simplicidade ou detalhe."}
