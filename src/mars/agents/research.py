from mars.mcp.client import LocalMCPToolClient
from mars.observability.langfuse import Observability
from mars.schemas.state import ResearchState

SYSTEM="""You are the research agent. Investigate the user's question using the supplied web results. Prefer primary sources, official documentation, standards, papers, and credible reporting. Never invent URLs. Return concise evidence-backed findings."""

def research_node(state: ResearchState) -> ResearchState:
    obs=Observability(); tools=LocalMCPToolClient()
    with obs.span("research_agent", {"query":state["query"]}):
        results=tools.web_search(state["query"])
        from mars.services.llm import LLMService
        llm=LLMService()
        if isinstance(results, str):
            compact = results
        else:
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
            "next_agent": "analysis",
        }
