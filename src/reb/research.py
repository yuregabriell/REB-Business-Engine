"""Optional web source discovery. Snippets are leads, NOT verified business facts."""
import json
import os
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from .errors import MissingProvider, REBError


def tavily_search(query: str, *, max_results: int = 5) -> list[dict]:
    api_key = os.environ.get("TAVILY_API_KEY", "")
    if not api_key:
        raise MissingProvider("Defina TAVILY_API_KEY para pesquisa pública; ou registe fontes manualmente.")
    if not 1 <= max_results <= 10:
        raise REBError("max_results deve estar entre 1 e 10")
    if not query.strip():
        raise REBError("Consulta vazia")
    payload = json.dumps({"api_key": api_key, "query": query, "max_results": max_results, "search_depth": "basic"}).encode("utf-8")
    request = Request("https://api.tavily.com/search", data=payload, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urlopen(request, timeout=20) as response:
            obj = json.loads(response.read(2_000_000))
    except (HTTPError, URLError, TimeoutError, ValueError) as exc:
        raise REBError("Não foi possível pesquisar no fornecedor configurado.") from exc
    return [{"title": r.get("title", ""), "url": r.get("url", ""), "snippet": r.get("content", "")[:1300], "classification": "discovery_unverified", "note": "Confirmar na fonte original antes de citar como facto."} for r in obj.get("results", [])[:max_results]]


def research_project(store, project_id: str, query: str, max_results: int = 5) -> dict:
    """Discover sources through a configured provider and save leads as UNVERIFIED.

    No source is auto-classified as verified; snippets are not primary evidence.
    """
    store.get_project(project_id)
    results = tavily_search(query, max_results=max_results)
    saved = []
    for item in results:
        title = item.get("title", "").strip()
        snippet = item.get("snippet", "").strip()
        source = item.get("url", "")
        if not title and not snippet:
            continue
        evidence = store.add_evidence(project_id, (title + " — " + snippet)[:900], source,
                                      "unverified", source_type="search_discovery", notes="Fonte descoberta; abrir e avaliar evidências originais antes de classificar.")
        saved.append(evidence)
    return {"project_id": project_id, "query": query, "discovered": len(results),
            "saved": len(saved), "evidence_ids": [x["id"] for x in saved], "verification": "required", "warning": "Resultados de pesquisa não são factos verificados."}
