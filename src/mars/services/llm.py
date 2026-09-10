from mars.config.settings import get_settings
class LLMService:
    def __init__(self):
        self.settings = get_settings()
    def invoke(self, system: str, prompt: str) -> str:
        raise NotImplementedError("LLM integration will be implemented in Step 2.")
