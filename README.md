# Multi-Agent Research System (MARS)

Production-oriented reference implementation of a specialized research assistant combining:

- **Streamlit** for the user experience
- **LangGraph** for supervisor-driven multi-agent orchestration
- **Hugging Face Inference API** for the LLM
- **Local MCP server** for standardized tool access
- **Tavily** for web research
- **SQLite persistent memory** for cross-session facts/preferences
- **Langfuse** for traces, token/latency/error observability
- **Configuration Advisor Agent** for trace-based optimization recommendations
- **Docker Compose** for reproducible deployment

## Core demonstration

> MCP = tool access, LangGraph = orchestration, Langfuse = observability, Configuration Advisor = continuous improvement.

## Architecture

```text
Streamlit
   |
   v
LangGraph Supervisor
   |---- Research Agent ------> Local MCP ------> Tavily
   |---- Analysis Agent
   |---- Verification Agent
   |---- Memory Agent ---------> Local MCP ------> SQLite
   |
   v
Final Answer + citations
   |
   v
Langfuse traces
   |
   v
Configuration Advisor Agent
   |
   v
Recommendation (model / temp / prompt / max tokens / routing)
   |
   v
Human approval
   |
   v
config/approved.json --> next run
```

## Quick start

1. Copy environment variables:

```bash
cp .env.example .env
```

2. Add at minimum:

- `HF_TOKEN`
- `HF_MODEL`
- `TAVILY_API_KEY`
- Langfuse keys if you want observability

3. Run with Docker:

```bash
docker compose up --build
```

Open `http://localhost:8501`.

For local development:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
streamlit run app/streamlit_app.py
```

In another terminal:

```bash
python -m mars.mcp.server
```

## Configuration advisor

The advisor is deliberately **human-in-the-loop**. It never silently changes production configuration. It reads recent Langfuse observations when credentials are configured, computes simple quality/cost/latency signals, asks an LLM to propose changes, validates the recommendation, and writes a pending recommendation. The Streamlit admin panel requires explicit approval before copying the approved configuration into `config/approved.json`.

This is designed as a safe baseline. In production, connect the approval action to your CI/CD system rather than allowing a running app container to mutate its own deployment.

## Memory

The memory agent stores only useful, non-sensitive research context: user-approved facts, preferences, project context, and prior research summaries. SQLite is used to keep the project easy to run. Replace `SQLiteMemoryStore` with Postgres/Redis/vector storage for a larger deployment.

## Testing

```bash
pytest -q
ruff check .
```

## Security notes

- Never commit `.env` or API keys.
- Keep Langfuse and Tavily credentials server-side.
- Treat web results as untrusted input.
- Human approval is required for configuration changes.
- The local MCP server binds to localhost by default.
- Add authentication before exposing MCP outside the host.

## Project structure

```text
app/                    Streamlit UI
src/mars/               application package
  agents/               research, analysis, verification, memory, advisor agents
  graph/                LangGraph orchestration
  mcp/                  MCP server/client abstractions
  memory/               persistent memory store
  observability/        Langfuse integration and trace analysis
  config/               typed runtime/config management
  schemas/              Pydantic state and API contracts
  services/             LLM and search adapters
config/                 base + approved runtime configuration
scripts/                operational utilities
docs/                   architecture and runbook
tests/                  unit tests
Dockerfile              application image
docker-compose.yml      local deployment
```
