import json
from pathlib import Path

def test_base_config_valid():
    cfg=json.loads(Path("config/base.json").read_text())
    assert cfg["model"]
    assert 0 <= cfg["temperature"] <= 2
    assert cfg["max_tokens"] > 0
