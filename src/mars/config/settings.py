import os
from dataclasses import dataclass
from dotenv import load_dotenv
load_dotenv()
@dataclass(frozen=True)
class Settings:
    hf_token: str = os.getenv("HF_TOKEN", "")
    hf_model: str = os.getenv("HF_MODEL", "meta-llama/Llama-3.1-8B-Instruct")
    hf_provider: str = os.getenv("HF_PROVIDER", "auto")
    hf_max_tokens: int = int(os.getenv("HF_MAX_TOKENS", "1024"))
    hf_temperature: float = float(os.getenv("HF_TEMPERATURE", "0.2"))
def get_settings() -> Settings:
    return Settings()
