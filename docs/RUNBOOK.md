# Runbook

## Startup

```bash
docker compose up --build
```

## Required secrets

`HF_TOKEN`, `TAVILY_API_KEY`; Langfuse credentials are optional for local demos.

## Common failures

### HF_TOKEN missing
The LLM adapter fails fast. Set the token in `.env`.

### Tavily key missing
Research cannot start because the MCP web-search tool is unavailable.

### Langfuse unavailable
Research still works. Advisor returns a telemetry-unavailable status.

### Configuration changed but behavior did not change
Restart/redeploy the application after approval. The approved JSON is the deployment configuration source for the reference implementation.
