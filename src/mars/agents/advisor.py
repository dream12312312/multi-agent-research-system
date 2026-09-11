import json
from pathlib import Path
from mars.config.settings import get_settings
from mars.services.llm import LLMService
from mars.schemas.state import Recommendation

class ConfigurationAdvisor:
    def analyze(self, observations: list[dict]) -> Recommendation:
        s=get_settings(); cfg=json.loads(Path(s.approved_config_path_abs).read_text())
        prompt=f"""You are a configuration advisor for a multi-agent research system.\nCurrent config: {json.dumps(cfg)}\nRecent observations: {json.dumps(observations)[:18000]}\n\nRecommend only high-confidence changes to model, temperature, max tokens, prompts, or routing. Do not recommend unsafe secrets or infrastructure mutations.\n\nRespond with EXACTLY ONE JSON object and nothing else, using ALL of these keys:\n{{"model": string or null, "temperature": number or null, "max_tokens": integer or null, "prompt_changes": object, "routing_changes": object, "rationale": string, "expected_impact": string, "risk": string}}\nEvery key is required (use null or empty object if no change)."""
        raw=LLMService().invoke("You optimize AI systems using measured traces, not guesses. Always answer with a single valid JSON object.",prompt)
        try:
            raw=raw[raw.find("{"):raw.rfind("}")+1]
            data, _=json.JSONDecoder(strict=False).raw_decode(raw)
            data.setdefault("rationale", "No rationale provided.")
            data.setdefault("expected_impact", "unknown")
            data.setdefault("risk", "medium")
            data.setdefault("prompt_changes", {})
            data.setdefault("routing_changes", {})
            return Recommendation.model_validate(data)
        except Exception as e:
            return Recommendation(rationale=f"Advisor output could not be parsed: {e}",expected_impact="none",risk="high")
