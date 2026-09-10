from mars.services.llm import LLMService
def test_llm_service_exists():
    assert LLMService() is not None
