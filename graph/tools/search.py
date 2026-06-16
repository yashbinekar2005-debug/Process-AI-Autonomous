import os
import logging
from config import settings

logger = logging.getLogger("enterprise_agent.tools.search")

def _duckduckgo_search(query: str, max_results: int = 3) -> str:
    """Free web search via DuckDuckGo. No API key needed."""
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
        if not results:
            return f"[No results found for: '{query}']"
        formatted = []
        for r in results:
            title = r.get("title", "Untitled")
            body = r.get("body", "")
            href = r.get("href", "")
            formatted.append(f"Title: {title}\nURL: {href}\nContent: {body}")
        return "\n\n".join(formatted)
    except ImportError:
        logger.warning("duckduckgo_search not installed. Install with: pip install duckduckgo-search")
        return None
    except Exception as e:
        logger.warning(f"DuckDuckGo search failed: {e}")
        return None

def web_search(query: str) -> str:
    """
    Search the web for a query.
    Uses Tavily API if configured, otherwise falls back to DuckDuckGo (free, no API key).
    """
    # Try Tavily first if configured
    if settings.TAVILY_API_KEY and settings.TAVILY_API_KEY != "your_tavily_api_key_here":
        try:
            from tavily import TavilyClient
            client = TavilyClient(api_key=settings.TAVILY_API_KEY)
            response = client.search(query=query, max_results=3)
            formatted = []
            for r in response.get("results", []):
                formatted.append(f"Title: {r.get('title')}\nURL: {r.get('url')}\nContent: {r.get('content')}")
            return "\n\n".join(formatted)
        except Exception as e:
            logger.warning(f"Tavily search failed: {e}. Falling back to DuckDuckGo.")

    # Fallback to DuckDuckGo (free, no API key)
    ddg_result = _duckduckgo_search(query)
    if ddg_result:
        return ddg_result

    # Ultimate fallback: mock data
    return (
        f"[MOCK SEARCH RESULT FOR: '{query}']\n"
        "- Competitor X has recently announced an AI assistant integration.\n"
        "- Average pricing for similar SaaS tools ranges from $49/month to $199/month.\n"
        "- The customer support ticket triage baseline resolution time is 4 hours.\n"
        "(Install 'duckduckgo-search' or configure TAVILY_API_KEY for live results)"
    )
