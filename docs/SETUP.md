# Setup checklist

1. Create `.env` from `.env.example`.
2. Add Hugging Face and Tavily credentials.
3. Optionally add Langfuse public/secret keys and host.
4. Start the MCP service before the app when running outside Compose.
5. Run a research query.
6. Inspect Langfuse traces.
7. Run Configuration Advisor.
8. Review the recommendation.
9. Approve it manually.
10. Redeploy/restart the service.

## Model choice

The Hugging Face adapter is intentionally configured through environment/configuration rather than hard-coded business logic. Replace `HF_MODEL` with any compatible instruction/chat model available through your Hugging Face inference provider.
