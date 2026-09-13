from mars.schemas.state import ResearchState
from mars.services.llm import LLMService
from mars.observability.langfuse import Observability


SYSTEM = """You are the answer agent.

Write the final answer to the user's question using the analysis and the
verification report. Only state claims that are supported by the verification;
clearly mark anything unsupported or uncertain. Do not invent sources or URLs.
"""


def answer_node(state: ResearchState) -> ResearchState:
    obs = Observability()
    with obs.span("answer_agent", {"query": state.get("query", "")}):
        llm = LLMService()
        citations = "\n".join(
            f"- {c.get('title')} | {c.get('url')}"
            for c in (state.get("citations") or [])
            if isinstance(c, dict)
        )
        prompt = f"""Question:
{state.get("query", "")}

Analysis:
{state.get("analysis", "")}

Verification report:
{state.get("verification", "")}

Available sources:
{citations}

Write the final answer in markdown. Structure it as:
1. A direct answer to the question.
2. Key supporting points with source URLs where available.
3. Caveats: anything unsupported or uncertain.

Do not invent sources or URLs.
"""
        final_answer = llm.invoke(SYSTEM, prompt)
    return {**state, "final_answer": final_answer, "next_agent": "memory"}
