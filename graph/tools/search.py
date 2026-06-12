import os
from config import settings

def web_search(query: str) -> str:
    """
    Search the web for a query using Tavily API.
    
    Args:
        query (str): The search query.
        
    Returns:
        str: Formatted search results or mock data if API key is missing.
    """
    if not settings.TAVILY_API_KEY or settings.TAVILY_API_KEY == "your_tavily_api_key_here":
        return (
            f"[MOCK SEARCH RESULT FOR: '{query}']\n"
            "- Competitor X has recently announced an AI assistant integration.\n"
            "- Average pricing for similar SaaS tools ranges from $49/month to $199/month.\n"
            "- The customer support ticket triage baseline resolution time is 4 hours.\n"
            "(To fetch real results, configure TAVILY_API_KEY in the .env file)"
        )
    
    try:
        from tavily import TavilyClient
        client = TavilyClient(api_key=settings.TAVILY_API_KEY)
        response = client.search(query=query, max_results=3)
        formatted = []
        for r in response.get("results", []):
            formatted.append(f"Title: {r.get('title')}\nURL: {r.get('url')}\nContent: {r.get('content')}")
        return "\n\n".join(formatted)
    except Exception as e:
        return f"Error executing search: {str(e)}"
