"""Small, attributed *method* library — not an automated claim of causation.

First-party summaries only. Case studies are observational, not scientific proofs.
Users must assess whether each practice fits their customers, jurisdiction and means.
"""
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Method:
    key: str
    title: str
    categories: tuple[str, ...]
    level: str
    source: str
    source_url: str
    lesson: str
    procedure: tuple[str, ...]
    measurement: str
    caveat: str


METHODS = (
    Method("scientific_validation", "Testar hipóteses como um cientista", ("validation", "strategy", "idea"), "ensaio aleatorizado em startups", "Camuffo et al., Management Science (2020)", "https://doi.org/10.1287/mnsc.2018.3249", "Tratar a estratégia como hipótese testável e rever decisões quando dados a contradizem.", ("Escrever uma hipótese observável", "Identificar medida e limiar antes da experiência", "Executar teste de baixo custo", "Registar resultados, incluindo os negativos", "Continuar, alterar ou abandonar a hipótese"), "Evidências comportamentais e mudança de decisão", "Resultados num grupo e contexto específicos; não implica garantia individual."),
    Method("personal_initiative", "Iniciativa pessoal orientada para a ação", ("operations", "strategy", "idea"), "ensaio aleatorizado com pequenos negócios", "Campos et al., Science (2017)", "https://doi.org/10.1126/science.aan4176", "Definir obstáculos antecipadamente e criar ações concretas para os superar.", ("Definir meta operacional clara", "Enumerar obstáculos controláveis", "Planear resposta proativa para cada obstáculo", "Executar e rever semanalmente"), "Marcos concluídos e lucro medido, não motivação declarada", "A melhoria média estudada não é promessa de resultados em outros mercados."),
    Method("customer_interviews", "Entrevistas centradas em comportamento", ("customers", "validation", "idea"), "metodologia prática (livro)", "Rob Fitzpatrick — The Mom Test", "https://www.momtestbook.com/", "Fazer perguntas sobre comportamentos recentes e dificuldades reais, não pedir elogios à ideia.", ("Escolher segmento específico", "Perguntar quando ocorreu o problema pela última vez", "Investigar alternativas e gastos atuais", "Registar padrões e contradições", "Testar compromisso observável"), "Problemas recorrentes e compromissos verificáveis", "Conselho metodológico; não é evidência experimental de eficácia universal."),
    Method("landing_page", "Validar interesse antes da construção", ("validation", "offers", "saas", "idea"), "relato de fundador", "Joel Gascoigne — How I started Buffer", "https://buffer.com/resources/idea-to-paying-customers-in-7-weeks-how-we-did-it/", "Experimentar uma oferta clara e verificar interesse qualificado antes de desenvolver tudo.", ("Apresentar proposta verdadeira e clara", "Medir visitas e ações concretas", "Explicar honestamente o estado do produto", "Testar intenção de pagamento sem cobranças enganosas", "Decidir se a evidência sustenta desenvolvimento"), "Compromissos e pagamentos reais; visitas são indicadores fracos", "Relato observacional; outros fatores podem explicar o sucesso."),
    Method("concierge", "Prestação manual antes de automatizar", ("operations", "customers", "local-services", "idea"), "ensaio de campo relatado", "Paul Graham — Do Things That Don't Scale", "https://paulgraham.com/ds.html", "Fazer manualmente aquilo que será automatizado depois para descobrir necessidades verdadeiras.", ("Descrever a entrega mínima", "Escolher poucos clientes com consentimento", "Executar manualmente com qualidade", "Medir esforço, custos e satisfação", "Só automatizar as partes repetíveis e desejadas"), "Pagamento, tempo por entrega e recompra", "Exige margem de segurança operacional e pode não escalar."),
    Method("product_market_fit", "Medir valor percebido e retenção", ("growth", "customers", "saas"), "relato de fundador", "Rahul Vohra — How Superhuman Built an Engine to Find Product/Market Fit", "https://review.firstround.com/how-superhuman-built-an-engine-to-find-product-market-fit/", "Segmentar utilizadores e acompanhar sinais de valor antes de escalar aquisição.", ("Entrevistar utilizadores ativos", "Medir retenção e satisfação", "Segmentar perfis com maior valor", "Melhorar bloqueios prioritários", "Medir novamente e comparar"), "Retenção, recompra e feedback longitudinal", "Métrica de inquérito é um sinal, não prova de lucro nem de causalidade."),
    Method("channel_testing", "Experimentar canais de aquisição", ("marketing", "sales", "growth"), "metodologia prática (livro)", "Weinberg & Mares — Traction", "https://www.tractionbook.com/", "Testar vários canais com custos limitados e concentrar recursos nos que mostram procura rentável.", ("Listar canais adequados e legais", "Estimar custo e tempo de teste", "Definir métrica de qualidade do lead", "Executar pilotos de pequena escala", "Comparar custo de aquisição e margem"), "CAC, taxa de conversão e contribuição marginal", "Eficácia varia por mercado, produto e maturidade; evitar extrapolação."),
)


def find_methods(query: str = "", *, stage: str = "", limit: int = 10) -> list[dict]:
    if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 20:
        raise ValueError("limit deve ser de 1 a 20")
    words = set((query + " " + stage).casefold().replace("-", " ").split())
    synonyms = {"clientes": "customers", "cliente": "customers", "mercado": "market", "vendas": "sales", "crescimento": "growth", "ideia": "idea", "validar": "validation", "dinheiro": "finance", "preço": "offers"}
    words.update(synonyms[w] for w in list(words) if w in synonyms)
    ranked = []
    for m in METHODS:
        text = (m.key + " " + m.title + " " + " ".join(m.categories) + " " + m.lesson).casefold().replace("-", " ")
        score = sum(1 for w in words if w in text and len(w) > 2)
        if not words or score:
            ranked.append((score, m.key, asdict(m)))
    return [d for _, _, d in sorted(ranked, key=lambda row: (-row[0], row[1]))[:limit]]
