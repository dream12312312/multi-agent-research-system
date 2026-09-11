import uuid
from langgraph.graph import StateGraph, START, END
from mars.schemas.state import ResearchState
from mars.agents.research import research_node
from mars.agents.analysis import analysis_node
from mars.agents.verification import verification_node
from mars.agents.memory import memory_node

def supervisor_node(state: ResearchState) -> ResearchState:
    """Lightweight deterministic supervisor.

    The supervisor chooses the next specialist based on workflow state. This is
    intentionally deterministic for a research demo; a learned router can replace
    this policy once Langfuse provides enough routing-quality data.
    """
    if not state.get("search_results"): next_agent="research"
    elif not state.get("analysis"): next_agent="analysis"
    elif not state.get("verification"): next_agent="verification"
    else: next_agent="memory"
    return {**state,"next_agent":next_agent}

def route(state: ResearchState): return state["next_agent"]

def build_graph():
    g=StateGraph(ResearchState)
    g.add_node("supervisor", supervisor_node)
    g.add_node("research", research_node)
    g.add_node("analysis", analysis_node)
    g.add_node("verification", verification_node)
    g.add_node("memory", memory_node)
    g.add_edge(START,"supervisor")
    g.add_conditional_edges("supervisor", route, {"research":"research","analysis":"analysis","verification":"verification","memory":"memory"})
    g.add_edge("research","supervisor")
    g.add_edge("analysis","supervisor")
    g.add_edge("verification","supervisor")
    g.add_edge("memory",END)
    return g.compile()

def run_research(query: str, session_id: str | None=None):
    return build_graph().invoke({"query":query,"session_id":session_id or str(uuid.uuid4()),"memories":[],"errors":[]})
