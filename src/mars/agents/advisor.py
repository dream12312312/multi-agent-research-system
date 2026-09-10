import json
from pathlib import Path
from mars.config.settings import get_settings
from mars.services.llm import LLMService
from mars.schemas.state import Recommendation

class ConfigurationAdvisor:
    def analyze(self, observations: list[dict]) -> Recommendation:
        s=get_settings(); cfg=json.loads(Path(s.approved_config_path).read_text())
        prompt=f"""You are a configuration advisor for a multi-agent research system.\nCurrent config: {json.dumps(cfg)}\nRecent observations: {json.dumps(observations)[:18000]}\n\nRecommend only high-confidence changes to model, temperature, max tokens, prompts, or routing. Do not recommend unsafe secrets or infrastructure mutations. Return JSON with keys model, temperature, max_tokens, prompt_changes, routing_changes, rationale, expected_impact, risk."""
        raw=LLMService().invoke("You optimize AI systems using measured traces, not guesses.",prompt)
        try:
            data=json.loads(raw[raw.find("{"):raw.rfind("}")+1])
            return Recommendation.model_validate(data)
        except Exception as e:
            return Recommendation(rationale=f"Advisor output could not be parsed: {e}",expected_impact="none",risk="high")
