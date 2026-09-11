import time

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from mars.config.settings import get_settings

# Free models tried in order when the primary model is unavailable/rate-limited.
FREE_FALLBACK_MODELS = [
    "google/gemma-4-31b-it:free",
    "nvidia/nemotron-3.5-lightning:free",
    "inclusionai/ling-3.0-flash-vl:free",
    "nex-agi/nex-n2.5-mini:free",
]

class LLMService:
    def __init__(self):
        s = get_settings()
        if not s.openrouter_api_key:
            raise RuntimeError("OPENROUTER_API_KEY is not configured")
        self._api_key = s.openrouter_api_key
        self._temperature = s.hf_temperature
        self._max_tokens = s.hf_max_tokens
        self._primary = s.llm_model
        self._models = [s.llm_model] + [m for m in FREE_FALLBACK_MODELS if m != s.llm_model]
        self.model = self._build(self._primary)

    def _build(self, model_id: str) -> ChatOpenAI:
        return ChatOpenAI(
            model=model_id,
            api_key=self._api_key,
            base_url="https://openrouter.ai/api/v1",
            temperature=self._temperature,
            max_tokens=self._max_tokens,
            default_headers={
                "HTTP-Referer": "https://localhost:8501",
                "X-Title": "Multi-Agent Research System",
            },
        )

    def invoke(self, system: str, prompt: str) -> str:
        messages = [SystemMessage(content=system), HumanMessage(content=prompt)]
        last_exc: Exception | None = None
        for model_id in self._models:
            for attempt in range(3):
                try:
                    model = self._build(model_id) if attempt or model_id != self._primary else self.model
                    response = model.invoke(messages)
                    return response.content if isinstance(response.content, str) else str(response.content)
                except Exception as exc:
                    last_exc = exc
                    status = getattr(getattr(exc, "body", None), "get", lambda *_: None)("code")
                    retriable = status in (429, 408, 500, 502, 503, 504) or status is None
                    if not retriable:
                        break  # non-retriable for this model -> try next model
                    time.sleep(2 * (attempt + 1))
        raise RuntimeError(f"All LLM models failed. Last error: {last_exc}") from last_exc
