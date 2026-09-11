from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Project root = directory containing pyproject.toml (works no matter where the
# app/server is launched from, since editable installs live under <root>/src).
PROJECT_ROOT = Path(__file__).resolve().parents[3]

def resolve_path(p: str | Path) -> Path:
    path = Path(p)
    return path if path.is_absolute() else PROJECT_ROOT / path

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=str(PROJECT_ROOT / ".env"), extra="ignore")
    hf_token: str = ""
    openrouter_api_key: str = ""
    llm_model: str = "google/gemma-4-31b-it:free"
    hf_model: str = "meta-llama/Llama-3.1-8B-Instruct"
    hf_provider: str = "auto"
    hf_max_tokens: int = 2048
    hf_temperature: float = 0.2
    tavily_api_key: str = ""
    tavily_max_results: int = 5
    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""
    langfuse_host: str = "https://cloud.langfuse.com"
    app_env: str = "development"
    log_level: str = "INFO"
    mcp_host: str = "127.0.0.1"
    mcp_port: int = 8765
    memory_db_path: str = "data/memory.sqlite3"
    approved_config_path: str = "config/approved.json"
    advisor_window: int = 50

@lru_cache
def get_settings() -> Settings:
    return Settings()

@property
def _approved_config_path(self) -> str:
    return str(resolve_path(self.approved_config_path))

@property
def _memory_db_path(self) -> str:
    return str(resolve_path(self.memory_db_path))

Settings.approved_config_path_abs = _approved_config_path
Settings.memory_db_path_abs = _memory_db_path
