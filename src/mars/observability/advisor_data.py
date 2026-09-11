from mars.config.settings import get_settings

def recent_observations(limit: int | None = None) -> list[dict]:
    s=get_settings(); limit=limit or s.advisor_window
    if not (s.langfuse_public_key and s.langfuse_secret_key):
        return [{"status":"langfuse_not_configured","hint":"Configure Langfuse to enable trace-driven optimization."}]
    try:
        from langfuse import Langfuse
        client=Langfuse(public_key=s.langfuse_public_key,secret_key=s.langfuse_secret_key,host=s.langfuse_host)
        traces=client.get_traces(limit=limit)
        return [t.model_dump() if hasattr(t,"model_dump") else dict(t) for t in traces.data]
    except Exception as e:
        return [{"status":"langfuse_error","error":str(e)}]
