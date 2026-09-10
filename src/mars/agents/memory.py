from mars.mcp.client import LocalMCPToolClient
from mars.schemas.state import ResearchState

def memory_node(state: ResearchState) -> ResearchState:
    tools=LocalMCPToolClient()
    tools.memory_add(state["session_id"], "research_summary", {"query":state["query"],"summary":state.get("final_answer","")[:2500]})
    return {**state,"next_agent":"finish"}
