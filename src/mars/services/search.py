from tavily import TavilyClient
from mars.config.settings import get_settings
import logging

logger = logging.getLogger(__name__)

class TavilySearchService:
    def __init__(self):
        s = get_settings()
        self.client = None
        self.max_results = s.tavily_max_results
        if s.tavily_api_key:
            self.client = TavilyClient(api_key=s.tavily_api_key)
        else:
            logger.warning(
                "TAVILY_API_KEY is not configured - falling back to free DuckDuckGo search"
            )

    def search(self, query: str) -> list[dict]:
        if self.client is not None:
            try:
                result = self.client.search(
                    query=query, search_depth="advanced", max_results=self.max_results
                )
                return result.get("results", [])
            except Exception as exc:
                logger.warning("Tavily search failed (%s); falling back to DuckDuckGo", exc)
        return self._duckduckgo_search(query)

    def _duckduckgo_search(self, query: str) -> list[dict]:
        """Free web search fallback (no API key required)."""
        try:
            from ddgs import DDGS
        except ImportError:
            from duckduckgo_search import DDGS
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=self.max_results):
                results.append(
                    {
                        "title": r.get("title", ""),
                        "url": r.get("href", r.get("url", "")),
                        "content": r.get("body", r.get("content", "")),
                        "source": "duckduckgo",
                    }
                )
        return results
