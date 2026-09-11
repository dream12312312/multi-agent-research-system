# Architecture

## Responsibilities

### Streamlit
Owns the presentation layer and explicit human approval action.

### LangGraph
Owns deterministic workflow state and agent ordering. The initial graph is linear for reliability; a supervisor can be introduced later with conditional edges once routing policies are measured.

### Agents
- Research: gathers evidence through the MCP tool boundary.
- Analysis: synthesizes evidence.
- Verification: audits claims and produces the final answer.
- Memory: stores a useful research summary for future sessions.
- Configuration Advisor: analyzes telemetry and proposes controlled configuration changes.

### MCP
The local server exposes web search and memory as standardized tools. This creates a clean boundary between orchestration and external capabilities.

### Langfuse
The observability layer wraps agent spans. With Langfuse configured, traces can be exported for advisor analysis. Without Langfuse, the application remains runnable and simply reports that telemetry is unavailable.

## Production evolution

1. Replace SQLite with Postgres + pgvector or a managed memory service.
2. Run MCP behind authenticated HTTPS or an internal service mesh.
3. Use a real LangGraph supervisor with conditional routing after collecting enough trace data.
4. Export Langfuse metrics to a durable analytics store.
5. Put configuration approval behind GitHub Actions/GitOps rather than writing into a running container.
6. Add source quality scoring and citation entailment checks.
