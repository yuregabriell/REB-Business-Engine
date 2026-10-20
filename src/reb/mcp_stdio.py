"""REB MCP stdio server, JSON-RPC 2.0 newline framing.

Implements essential MCP lifecycle and tools; no log messages on stdout.
Host requires an MCP client; launching directly is not an interactive terminal.
"""
import json
import sys
from . import __version__
from .storage import Store
from .engine import diagnose, spending_review, recommend_experiment
from .finance import financial_scenario
from .agents import AGENTS
from .nexus import CAPABILITIES, make_delegation
from .evolution import skill_profile, adaptive_explanation
from .provider import consult_agent
from .mission import run_mission
from .knowledge import find_methods
from .blueprint import build_blueprint
from .research import research_project
from .errors import REBError


def schema(required: list[str], properties: dict) -> dict:
    return {"type": "object", "properties": properties, "required": required, "additionalProperties": False}
S = lambda text: {"type": "string", "description": text}

TOOLS = [
 {"name": "reb_create_project", "description": "Cria projeto empresarial local; guarda estado SQLite.", "inputSchema": schema(["name", "idea"], {"name": S("Nome"), "idea": S("Ideia"), "market": S("Região"), "stage": {"type": "string", "enum": ["idea", "validation", "launch", "operating", "scaling"]}, "budget": S("Orçamento nominal"), "objective": S("Meta")})},
 {"name": "reb_list_projects", "description": "Lista projetos locais.", "inputSchema": schema([], {})},
 {"name": "reb_get_project", "description": "Devolve estado completo, fontes, experiências e diário.", "inputSchema": schema(["project_id"], {"project_id": S("ID")})},
 {"name": "reb_diagnose", "description": "Diagnóstico baseado em estado real, sem simular fontes nem vendas.", "inputSchema": schema(["project_id"], {"project_id": S("ID"), "question": S("Questão")})},
 {"name": "reb_record_evidence", "description": "Regista facto, hipótese ou afirmação incerta com proveniência; 'verified' requer URL.", "inputSchema": schema(["project_id", "claim"], {"project_id": S("ID"), "claim": S("Afirmação"), "url": S("URL fonte"), "status": {"type": "string", "enum": ["verified", "inferred", "unverified", "contradicted"]}, "notes": S("Notas")})},
 {"name": "reb_financial_scenario", "description": "Cálculo determinístico de resultado e ponto de equilíbrio por período.", "inputSchema": schema(["price", "variable_cost", "fixed_cost", "units"], {"price": S("Preço"), "variable_cost": S("Custo variável unitário"), "fixed_cost": S("Custo fixo período"), "units": {"type": "integer", "minimum": 0}, "cash": S("Caixa"), "cac": S("Aquisição por venda")})},
 {"name": "reb_investment_gate", "description": "Verifica orçamento, evidências e autorização antes de gastar. Não efetua pagamento.", "inputSchema": schema(["project_id", "cost"], {"project_id": S("ID"), "cost": S("Custo"), "approved": {"type": "boolean"}})},
 {"name": "reb_suggest_experiment", "description": "Sugere experimento para o estágio do projeto.", "inputSchema": schema(["project_id"], {"project_id": S("ID")})},
 {"name": "reb_create_experiment", "description": "Guarda hipótese, métrica, meta e limite de gastos.", "inputSchema": schema(["project_id", "hypothesis", "metric", "target"], {"project_id": S("ID"), "hypothesis": S("Hipótese"), "metric": S("Indicador"), "target": S("Limiar de decisão"), "cap": S("Orçamento do teste")})},
 {"name": "reb_experiment_result", "description": "Regista resultado real de experiência.", "inputSchema": schema(["experiment_id", "observed", "state"], {"experiment_id": S("ID"), "observed": S("Observações"), "state": {"type": "string", "enum": ["completed", "inconclusive", "stopped"]}})},
 {"name": "reb_journal", "description": "Regista atividade, decisão, aprendizagem e resultados, como declarados pelo utilizador.", "inputSchema": schema(["project_id", "body"], {"project_id": S("ID"), "body": S("Descrição"), "kind": {"type": "string", "enum": ["activity", "decision", "result", "lesson"]}, "revenue": S("Receita declarada"), "cost": S("Custo declarado"), "customers": {"type": "integer", "minimum": 0}})},
 {"name": "reb_learning", "description": "Regista competência demonstrada; não atribui nível só pelo tempo de utilização.", "inputSchema": schema(["project_id", "topic", "level", "demonstration"], {"project_id": S("ID"), "topic": S("finance/sales/marketing/operations/strategy/leadership/validation"), "level": {"type": "integer", "minimum": 0, "maximum": 4}, "demonstration": S("Exemplo de competência")})},
 {"name": "reb_evolution_profile", "description": "Perfil de competências por área.", "inputSchema": schema(["project_id"], {"project_id": S("ID")})},
 {"name": "reb_adaptive_explanation", "description": "Linguagem adaptativa por tema e nível.", "inputSchema": schema(["topic", "level"], {"topic": S("Tema"), "level": {"type": "integer", "minimum": 0, "maximum": 4}})},
 {"name": "reb_nexus_catalog", "description": "Capacidades REA/RES e outros conectores, incluindo pré-requisitos.", "inputSchema": schema([], {})},
 {"name": "reb_prepare_delegation", "description": "Prepara tarefa de outra skill/MCP; não a executa silenciosamente.", "inputSchema": schema(["provider", "objective"], {"provider": S("rea/res/market_research/business_core"), "objective": S("O que precisa fazer")})},
 {"name": "reb_run_mission", "description": "Orquestra múltiplos especialistas e auditor mediante API de IA configurada; não executa gastos nem publica.", "inputSchema": schema(["project_id", "goal"], {"project_id": S("ID"), "goal": S("Objetivo"), "max_agents": {"type": "integer", "minimum": 2, "maximum": 8}})},
 {"name": "reb_methods", "description": "Pesquisar metodologias com fonte, nível de evidência e ressalvas.", "inputSchema": schema([], {"query":S("Problema"), "stage":S("Etapa")})},
 {"name": "reb_research_sources", "description": "Pesquisa pública via Tavily opcional; grava sempre resultados como NÃO VERIFICADOS. Pode consumir quota da API configurada.", "inputSchema": schema(["project_id", "query"], {"project_id":S("ID"), "query":S("Consulta"), "max_results":{"type":"integer", "minimum":1, "maximum":10}})},
 {"name": "reb_blueprint", "description": "Plano determinístico orientado por evidências e experimentos, não garantia de sucesso.", "inputSchema": schema(["project_id"], {"project_id":S("ID"), "goal":S("Objetivo")})},
 {"name": "reb_consult_specialist", "description": "Consultar especialista configurado por API externa; exige REB_MODEL_*.", "inputSchema": schema(["project_id", "agent", "task"], {"project_id": S("ID"), "agent": {"type": "string", "enum": [a.key for a in AGENTS]}, "task": S("Objetivo")})},
]


def tool_call(store: Store, name: str, a: dict):
    if name == "reb_create_project": return store.add_project(a["name"], a["idea"], a.get("market", "Portugal"), a.get("stage", "idea"), a.get("budget", "0"), a.get("objective", "Validar procura"))
    if name == "reb_list_projects": return store.list_projects()
    if name == "reb_get_project": return store.export(a["project_id"])
    if name == "reb_diagnose": return diagnose(store, a["project_id"], a.get("question", ""))
    if name == "reb_record_evidence": return store.add_evidence(a["project_id"], a["claim"], a.get("url", ""), a.get("status", "unverified"), notes=a.get("notes", ""))
    if name == "reb_financial_scenario": return financial_scenario(a["price"], a["variable_cost"], a["fixed_cost"], a["units"], a.get("cash", "0"), a.get("cac", "0"))
    if name == "reb_investment_gate": return spending_review(store, a["project_id"], a["cost"], a.get("approved", False))
    if name == "reb_suggest_experiment": return recommend_experiment(store.get_project(a["project_id"]), len(store.evidence(a["project_id"])))
    if name == "reb_create_experiment": return store.add_experiment(a["project_id"], a["hypothesis"], a["metric"], a["target"], a.get("cap", "0"))
    if name == "reb_experiment_result": return store.set_experiment_result(a["experiment_id"], a["observed"], a["state"])
    if name == "reb_journal": return store.add_journal(a["project_id"], a["body"], a.get("kind", "activity"), a.get("revenue", "0"), a.get("cost", "0"), a.get("customers", 0))
    if name == "reb_learning": return store.add_learning(a["project_id"], a["topic"], a["level"], a["demonstration"])
    if name == "reb_evolution_profile": return skill_profile(store, a["project_id"])
    if name == "reb_adaptive_explanation": return adaptive_explanation(a["topic"], a["level"])
    if name == "reb_nexus_catalog": return CAPABILITIES
    if name == "reb_prepare_delegation": return make_delegation(a["provider"], a["objective"])
    if name == "reb_run_mission": return run_mission(store, a["project_id"], a["goal"], a.get("max_agents", 4))
    if name == "reb_methods": return find_methods(a.get("query", ""), stage=a.get("stage", ""))
    if name == "reb_research_sources": return research_project(store, a["project_id"], a["query"], a.get("max_results",5))
    if name == "reb_blueprint": return build_blueprint(store, a["project_id"], a.get("goal", ""))
    if name == "reb_consult_specialist": return consult_agent(a["agent"], a["task"], store.export(a["project_id"]))
    raise REBError("Ferramenta não encontrada: " + name)


def dispatch(message: dict, store: Store) -> dict | None:
    mid = message.get("id")
    method = message.get("method")
    if mid is None:  # notification, no response
        return None
    try:
        if method == "initialize":
            result = {"protocolVersion": "2024-11-05", "serverInfo": {"name": "reb-business-engine", "version": __version__}, "capabilities": {"tools": {"listChanged": False}}}
        elif method == "ping": result = {}
        elif method == "tools/list": result = {"tools": TOOLS}
        elif method == "tools/call":
            p = message.get("params") or {}
            args = p.get("arguments") or {}
            if not isinstance(args, dict): raise REBError("Argumentos devem ser objeto JSON")
            value = tool_call(store, p.get("name", ""), args)
            result = {"content": [{"type": "text", "text": json.dumps(value, ensure_ascii=False, default=str)}], "isError": False}
        else:
            return {"jsonrpc": "2.0", "id": mid, "error": {"code": -32601, "message": "Method not found"}}
        return {"jsonrpc": "2.0", "id": mid, "result": result}
    except (REBError, KeyError, ValueError, TypeError) as exc:
        if method == "tools/call":
            return {"jsonrpc": "2.0", "id": mid, "result": {"content": [{"type": "text", "text": str(exc)}], "isError": True}}
        return {"jsonrpc": "2.0", "id": mid, "error": {"code": -32602, "message": "Invalid parameters"}}


def serve(path=None):
    with Store(path) as store:
        for line in sys.stdin:
            if not line.strip(): continue
            try:
                msg = json.loads(line)
                if not isinstance(msg, dict): raise ValueError("Invalid message")
                response = dispatch(msg, store)
                if response is not None:
                    sys.stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
                    sys.stdout.flush()
            except (json.JSONDecodeError, ValueError, TypeError):
                sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "Parse error"}}) + "\n")
                sys.stdout.flush()


def main():
    serve()

if __name__ == "__main__": main()
