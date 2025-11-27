"""Web search client using Google Custom Search API."""
import httpx
from typing import List, Dict, Any
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


async def search_web(query: str, num_results: int = 10) -> List[Dict[str, Any]]:
    """
    Search the web using Google Custom Search API.
    
    Args:
        query: Search query
        num_results: Number of results to return (max 10 per page)
        
    Returns:
        List of search results with title, link, snippet
    """
    if not settings.google_search_api_key or not settings.google_search_cx:
        logger.warning("Google Search API not configured. Returning empty results.")
        return []
    
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": settings.google_search_api_key,
        "cx": settings.google_search_cx,
        "q": query,
        "num": min(num_results, 10),  # Max 10 per request
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=30.0)
            response.raise_for_status()
            data = response.json()
            
            results = []
            for item in data.get("items", []):
                results.append({
                    "title": item.get("title", ""),
                    "link": item.get("link", ""),
                    "snippet": item.get("snippet", ""),
                })
            
            logger.info(f"Web search completed: {len(results)} results for query: {query}")
            return results
            
    except httpx.HTTPStatusError as e:
        logger.error(f"Google Search API error: {e.response.status_code} - {e.response.text}")
        return []
    except Exception as e:
        logger.error(f"Web search error: {str(e)}")
        return []

