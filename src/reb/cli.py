"""REB command-line interface. All actions are local unless explicitly configured."""
import argparse
import json
import os
import sys
from pathlib import Path
from . import __version__
from .agents import AGENTS
from .engine import diagnose, recommend_experiment, spending_review
from .errors import REBError
from .evolution import adaptive_explanation, skill_profile
from .finance import financial_scenario
from .nexus import CAPABILITIES, make_delegation, discover_skills
from .provider import consult_agent
from .mission import run_mission
from .knowledge import find_methods
from .blueprint import build_blueprint
from .nexus_client import nexus_tools, nexus_call
from .research import tavily_search, research_project
from .storage import Store


def dump(o):
    print(json.dumps(o, ensure_ascii=False, indent=2, default=str))


def parser():
    p = argparse.ArgumentParser(prog="reb", description="REB — inteligência empresarial orientada por evidências")
    p.add_argument("--db", help="Caminho alternativo para base SQLite")
    subs = p.add_subparsers(dest="command", required=True)
    subs.add_parser("doctor", help="Verificar a instalação")
    subs.add_parser("agents", help="Listar especialistas")
    subs.add_parser("projects", help="Listar projetos")
    init = subs.add_parser("init", help="Criar projeto")
    for arg in ("name", "idea"):
        init.add_argument(arg)
    init.add_argument("--market", default="Portugal")
    init.add_argument("--stage", choices=["idea", "validation", "launch", "operating", "scaling"], default="idea")
    init.add_argument("--budget", default="0")
    init.add_argument("--objective", default="Validar procura")
    for name, desc in (("diagnose", "Diagnóstico e próximos passos"), ("export", "Exportar todos os dados em JSON"), ("progress", "Progresso de aprendizagem"), ("suggest-experiment", "Sugerir experiência")):
        x = subs.add_parser(name, help=desc)
        x.add_argument("project_id")
        if name == "diagnose":
            x.add_argument("--question", default="")
    ev = subs.add_parser("evidence", help="Registar evidência")
    ev.add_argument("project_id"); ev.add_argument("claim")
    ev.add_argument("--url", default="")
    ev.add_argument("--status", choices=["verified", "unverified", "inferred", "contradicted"], default="unverified")
    ev.add_argument("--notes", default="")
    ex = subs.add_parser("experiment", help="Criar uma experiência falsificável")
    ex.add_argument("project_id"); ex.add_argument("hypothesis")
    ex.add_argument("--metric", required=True); ex.add_argument("--target", required=True)
    ex.add_argument("--cap", default="0")
    result = subs.add_parser("experiment-result", help="Registar resultado observado")
    result.add_argument("experiment_id"); result.add_argument("observed"); result.add_argument("--state", choices=["completed", "inconclusive", "stopped"], required=True)
    j = subs.add_parser("journal", help="Adicionar entrada ao diário")
    j.add_argument("project_id"); j.add_argument("body")
    j.add_argument("--kind", choices=["activity", "decision", "result", "lesson"], default="activity")
    j.add_argument("--revenue", default="0"); j.add_argument("--cost", default="0"); j.add_argument("--customers", type=int, default=0)
    f = subs.add_parser("finance", help="Calcular cenários financeiros")
    f.add_argument("--price", required=True); f.add_argument("--variable", required=True)
    f.add_argument("--fixed", required=True); f.add_argument("--units", type=int, required=True)
    f.add_argument("--cash", default="0"); f.add_argument("--cac", default="0")
    gate = subs.add_parser("gate", help="Verificação antes de investimento")
    gate.add_argument("project_id"); gate.add_argument("cost")
    gate.add_argument("--approved", action="store_true")
    learn = subs.add_parser("learn", help="Registar competência demonstrada")
    learn.add_argument("project_id"); learn.add_argument("topic", choices=["finance", "sales", "marketing", "operations", "strategy", "leadership", "validation"])
    learn.add_argument("level", type=int); learn.add_argument("demonstration")
    explain = subs.add_parser("explain", help="Explicar um conceito de forma adaptativa")
    explain.add_argument("topic"); explain.add_argument("level", type=int)
    n = subs.add_parser("nexus", help="Ver catálogo de capacidades do Nexus")
    n.add_argument("--skills-root", default="skills")
    delegate = subs.add_parser("delegate", help="Preparar delegação (não executa)")
    delegate.add_argument("provider"); delegate.add_argument("objective")
    r = subs.add_parser("research", help="Pesquisar fontes públicas (Tavily opcional)")
    r.add_argument("query")
    rp = subs.add_parser("research-project", help="Pesquisar e guardar fontes DESCONHECIDAS/Não verificadas")
    rp.add_argument("project_id"); rp.add_argument("query")
    rp.add_argument("--max-results",type=int, default=5)
    ask = subs.add_parser("ask", help="Consultar especialista com IA externa configurada")
    ask.add_argument("project_id"); ask.add_argument("agent", choices=sorted(a.key for a in AGENTS)); ask.add_argument("task")
    mission = subs.add_parser("mission", help="Consultar vários especialistas e um auditor com IA configurada")
    mission.add_argument("project_id"); mission.add_argument("goal"); mission.add_argument("--max-agents", type=int, default=4)
    kb = subs.add_parser("methods", help="Pesquisar métodos empresariais com fontes e limitações")
    kb.add_argument("query", nargs="?", default=""); kb.add_argument("--stage", default="")
    plan = subs.add_parser("blueprint", help="Plano baseado no estágio e nas evidências do projeto")
    plan.add_argument("project_id"); plan.add_argument("--goal", default="")
    nt = subs.add_parser("nexus-tools", help="Descobrir ferramentas MCP configuradas")
    nt.add_argument("provider"); nt.add_argument("--config", required=True)
    nc = subs.add_parser("nexus-call", help="Executar ferramenta MCP autorizada, com confirmação")
    nc.add_argument("provider"); nc.add_argument("tool"); nc.add_argument("--config", required=True)
    nc.add_argument("--project-id", default="", help="Guardar recibo de execução neste projeto")
    nc.add_argument("--args", default="{}"); nc.add_argument("--approve-external", action="store_true")
    nc.add_argument("--approve-write", action="store_true")
    integ = subs.add_parser("integrations", help="Diagnosticar ligações REA/RES/HubSpot")
    integ.add_argument("--config", default=None); integ.add_argument("--skills-root", default=None)
    hub = subs.add_parser("hubspot-read", help="Leitura autorizada e sem PII do HubSpot")
    hub.add_argument("kind", choices=["contacts", "deals"]); hub.add_argument("--limit", type=int, default=20)
    hub.add_argument("--approve-read", action="store_true")
    studio = subs.add_parser("studio", help="Abrir painel local REB Studio")
    studio.add_argument("--port", type=int, default=8765)
    subs.add_parser("mcp", help="Iniciar servidor MCP stdio")
    return p


def run(args):
    command = args.command
    if command == "studio":
        from .studio import serve as serve_studio
        serve_studio(args.db, args.port)
        return
    if command == "mcp":
        from .mcp_stdio import serve
        serve(args.db)
        return
    if command == "integrations":
        from .integrations import diagnose_integrations
        dump(diagnose_integrations(args.config,args.skills_root)); return
    if command == "hubspot-read":
        from .business_connectors import hubspot_read
        dump(hubspot_read(args.kind,limit=args.limit,approved=args.approve_read)); return
    if command == "doctor":
        dump({"reb_version": __version__, "python": sys.version.split()[0], "database": str(args.db or os.environ.get("REB_DB_PATH", "~/.reb/projects.sqlite3")), "model_configured": all(os.environ.get(k) for k in ("REB_MODEL_API_KEY", "REB_MODEL_BASE_URL", "REB_MODEL")), "web_search_configured": bool(os.environ.get("TAVILY_API_KEY")), "mcp": "reb-mcp or reb mcp", "result": "ready_for_local_operation"})
        return
    if command == "agents":
        dump([{"key": a.key, "title": a.title, "mission": a.mission, "outputs": a.outputs} for a in AGENTS]); return
    if command == "finance":
        dump(financial_scenario(args.price, args.variable, args.fixed, args.units, args.cash, args.cac)); return
    if command == "methods":
        dump(find_methods(args.query, stage=args.stage)); return
    if command == "nexus-tools":
        dump(nexus_tools(args.config, args.provider)); return
    if command == "nexus-call":
        try: payload=json.loads(args.args)
        except ValueError: raise REBError("--args tem de ser JSON válido") from None
        if args.project_id:
            with Store(args.db) as st: st.get_project(args.project_id)  # Validate before external call.
        response=nexus_call(args.config,args.provider,args.tool,payload,approved_external=args.approve_external,approved_write=args.approve_write)
        if args.project_id:
            with Store(args.db) as st:
                response["receipt"] = st.add_delegation(args.project_id,args.provider,args.tool,payload,response["result"])
        dump(response); return
    if command == "nexus":
        dump({"capabilities": CAPABILITIES, "skills": discover_skills(args.skills_root)}); return
    if command == "delegate":
        dump(make_delegation(args.provider, args.objective)); return
    if command == "research":
        dump({"results": tavily_search(args.query)}); return
    if command == "explain":
        dump(adaptive_explanation(args.topic, args.level)); return
    with Store(args.db) as store:
        if command == "init": out = store.add_project(args.name, args.idea, args.market, args.stage, args.budget, args.objective)
        elif command == "projects": out = store.list_projects()
        elif command == "diagnose": out = diagnose(store, args.project_id, args.question)
        elif command == "export": out = store.export(args.project_id)
        elif command == "research-project": out = research_project(store, args.project_id, args.query, args.max_results)
        elif command == "blueprint": out = build_blueprint(store, args.project_id, args.goal)
        elif command == "progress": out = skill_profile(store, args.project_id)
        elif command == "suggest-experiment": out = recommend_experiment(store.get_project(args.project_id), len(store.evidence(args.project_id)))
        elif command == "evidence": out = store.add_evidence(args.project_id, args.claim, args.url, args.status, notes=args.notes)
        elif command == "experiment": out = store.add_experiment(args.project_id, args.hypothesis, args.metric, args.target, args.cap)
        elif command == "experiment-result": out = store.set_experiment_result(args.experiment_id, args.observed, args.state)
        elif command == "journal": out = store.add_journal(args.project_id, args.body, args.kind, args.revenue, args.cost, args.customers)
        elif command == "gate": out = spending_review(store, args.project_id, args.cost, approved=args.approved)
        elif command == "learn": out = store.add_learning(args.project_id, args.topic, args.level, args.demonstration)
        elif command == "ask": out = consult_agent(args.agent, args.task, store.export(args.project_id))
        elif command == "mission": out = run_mission(store, args.project_id, args.goal, args.max_agents)
        else: raise REBError("Comando não implementado")
        dump(out)


def main(argv=None):
    p = parser()
    args = p.parse_args(argv)
    try:
        run(args)
    except (REBError, ValueError) as exc:
        print("REB: " + str(exc), file=sys.stderr)
        return 2
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
