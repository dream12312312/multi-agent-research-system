from mars.mcp.client import LocalMCPToolClient
from mars.observability.langfuse import Observability
from mars.schemas.state import ResearchState

SYSTEM="""You are the research agent. Investigate the user's question using the supplied web results. Prefer primary sources, official documentation, standards, papers, and credible reporting. Never invent URLs. Return concise evidence-backed findings."""

def _normalize_results(results):
    """Ensure search results are always a list[dict] for downstream agents and the UI."""
    if results is None:
        return []
    if isinstance(results, str):
        return [{"title": "Search results", "url": "", "content": results}]
    if isinstance(results, dict):
        for key in ("results", "data", "items"):
            if key in results:
                return _normalize_results(results[key])
        return [results]
    if isinstance(results, (list, tuple)):
        out = []
        for item in results:
            if isinstance(item, dict):
                out.append(item)
            elif isinstance(item, str):
                out.append({"title": "Search result", "url": "", "content": item})
        return out
    return []

def research_node(state: ResearchState) -> ResearchState:
    obs=Observability(); tools=LocalMCPToolClient()
    with obs.span("research_agent", {"query":state["query"]}):
        results=_normalize_results(tools.web_search(state["query"]))
        from mars.services.llm import LLMService
        llm=LLMService()
        compact = "\n".join(
            f"- {r.get('title')} | {r.get('url')} | {r.get('content', '')[:1200]}"
            for r in results
            if isinstance(r, dict)
        )
        prompt=f"Question: {state['query']}\n\nSearch results:\n{compact}\n\nProduce 4-8 evidence-backed findings."
        text=llm.invoke(SYSTEM,prompt)
        return {
            **state,
            "search_results": results,
            "research_findings": text,
            "next_agent": "analysis",
        }
