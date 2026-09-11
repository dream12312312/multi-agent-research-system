from typing import Any, Literal
from pydantic import BaseModel, Field
from typing_extensions import TypedDict

class Source(BaseModel):
    title: str
    url: str
    snippet: str = ""
    score: float | None = None

class ResearchFinding(BaseModel):
    claim: str
    evidence: str
    sources: list[Source] = Field(default_factory=list)
    confidence: float = 0.5

class Recommendation(BaseModel):
    model: str | None = None
    temperature: float | None = None
    max_tokens: int | None = None
    prompt_changes: dict[str, str] = Field(default_factory=dict)
    routing_changes: dict[str, str] = Field(default_factory=dict)
    rationale: str
    expected_impact: str
    risk: str = "low"

class ResearchState(TypedDict, total=False):
    query: str
    session_id: str
    memories: list[dict[str, Any]]
    search_results: list[dict[str, Any]]
    findings: list[ResearchFinding]
    analysis: str
    verification: str
    final_answer: str
    citations: list[Source]
    trace_id: str
    recommendation: Recommendation | None
    next_agent: Literal["research", "analysis", "verification", "memory", "finish"]
    errors: list[str]
