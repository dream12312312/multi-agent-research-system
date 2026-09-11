from contextlib import contextmanager
from mars.config.settings import get_settings


class Observability:
    def __init__(self):
        s = get_settings()
        self.client = None

        if s.langfuse_public_key and s.langfuse_secret_key:
            try:
                from langfuse import Langfuse

                self.client = Langfuse(
                    public_key=s.langfuse_public_key,
                    secret_key=s.langfuse_secret_key,
                    host=s.langfuse_host,
                )
            except Exception:
                self.client = None

    @contextmanager
    def span(self, name: str, metadata: dict | None = None):
        if not self.client:
            yield None
            return

        try:
            with self.client.start_as_current_observation(
                name=name,
                metadata=metadata or {},
            ) as observation:
                yield observation
        finally:
            self.client.flush()

    def flush(self):
        if self.client:
            self.client.flush()