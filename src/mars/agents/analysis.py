from mars.schemas.state import ResearchState
from mars.services.llm import LLMService
from mars.observability.langfuse import Observability

def analysis_node(state: ResearchState) -> ResearchState:
    obs=Observability()
    with obs.span("analysis_agent"):
        llm=LLMService()
        evidence="\n".join(
            f"- {r.get('title')} | {r.get('url')} | {r.get('content', '')[:1200]}"
            for r in (state.get("search_results") or [])
            if isinstance(r, dict)
        )
        prompt=f"Question: {state['query']}\nResearch evidence:\n{evidence}\n\nSynthesize a direct answer. Separate facts, inference, and open questions. Cite source URLs from the evidence where available."
        answer=llm.invoke("You are a senior technical/business analyst.",prompt)
        return {**state,"analysis":answer,"next_agent":"verification"}
