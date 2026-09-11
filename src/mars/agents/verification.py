from mars.schemas.state import ResearchState
from mars.observability.langfuse import Observability
from mars.services.llm import LLMService


SYSTEM = """You are the verification agent.

Verify the research findings against the supplied sources.
Identify unsupported claims and provide concise, evidence-backed verification.
Do not invent sources or URLs.
"""


def _normalize_results(results):
    if results is None:
        return []

    if isinstance(results, str):
        return [
            {
                "title": "Search Results",
                "url": "",
                "content": results,
            }
        ]

    if isinstance(results, dict):
        if "results" in results:
            return _normalize_results(results["results"])

        if "data" in results:
            return _normalize_results(results["data"])

        if "items" in results:
            return _normalize_results(results["items"])

        return [results]

    if isinstance(results, (list, tuple)):
        normalized = []

        for item in results:
            if isinstance(item, dict):
                normalized.append(item)
            elif isinstance(item, str):
                normalized.append(
                    {
                        "title": "Search Result",
                        "url": "",
                        "content": item,
                    }
                )

        return normalized

    return []


def verification_node(state: ResearchState) -> ResearchState:
    obs = Observability()

    results = _normalize_results(
        state.get("search_results")
    )

    source_parts = []

    for result in results:
        title = str(result.get("title", "Source"))
        url = str(result.get("url", ""))
        content = str(result.get("content", ""))

        source_parts.append(
            f"{title}: {url}\n{content[:800]}"
        )

    sources = "\n\n".join(source_parts)

    citations = []

    for result in results:
        url = str(result.get("url", ""))

        if url:
            citations.append(
                {
                    "title": str(
                        result.get("title", "Source")
                    ),
                    "url": url,
                    "snippet": str(
                        result.get("content", "")
                    )[:300],
                }
            )

    with obs.span(
        "verification_agent",
        {"query": state["query"]},
    ):
        llm = LLMService()

        prompt = f"""Question:

{state["query"]}

Research findings:

{state.get("analysis", "")}

Sources:

{sources}

Verify the research findings against the supplied sources.

Determine:
1. Which claims are supported.
2. Which claims are unsupported or questionable.
3. What evidence supports the important claims.

Do not invent evidence or sources.
"""

        verification = llm.invoke(
            SYSTEM,
            prompt,
        )

    return {
        **state,
        "verification": verification,
        "citations": citations,
        "final_answer": (
            f"## Answer\n\n{state.get('analysis', '').strip()}\n\n"
            f"## Verification\n\n{verification.strip()}"
        ),
        "next_agent": "memory",
    }