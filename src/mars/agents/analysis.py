from mars.schemas.state import ResearchState
from mars.services.llm import LLMService
from mars.observability.langfuse import Observability

def analysis_node(state: ResearchState) -> ResearchState:
    obs=Observability()
    with obs.span("analysis_agent"):
        llm=LLMService()
        prompt=f"Question: {state['query']}\nResearch evidence:\n{state.get('analysis','')}\n\nSynthesize a direct answer. Separate facts, inference, and open questions. Cite source URLs from the evidence where available."
        answer=llm.invoke("You are a senior technical/business analyst.",prompt)
        return {**state,"analysis":answer,"next_agent":"verification"}
