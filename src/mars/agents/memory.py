from mars.mcp.client import LocalMCPToolClient
from mars.schemas.state import ResearchState

def memory_node(state: ResearchState) -> ResearchState:
    tools=LocalMCPToolClient()
    # Fallback: make sure a final answer always exists for the UI.
    if not state.get("final_answer"):
        fallback = state.get("analysis") or state.get("verification") or state.get("query", "")
        state = {**state, "final_answer": fallback}
    tools.memory_add(state["session_id"], "research_summary", {"query":state["query"],"summary":state.get("final_answer","")[:2500]})
    return {**state,"next_agent":"finish"}
