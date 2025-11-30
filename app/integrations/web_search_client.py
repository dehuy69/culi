"""Web search client using Google Custom Search API."""
import httpx
from typing import List, Dict, Any
import asyncio
from bs4 import BeautifulSoup
import html2text
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Configure html2text converter
html_converter = html2text.HTML2Text()
html_converter.ignore_links = False
html_converter.ignore_images = True
html_converter.body_width = 0  # Don't wrap lines


async def fetch_url_content(url: str, timeout: float = 10.0) -> str:
    """
    Fetch and extract text content from a URL.
    
    Args:
        url: URL to fetch
        timeout: Request timeout in seconds
        
    Returns:
        Extracted text content, or empty string if error
    """
    try:
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            # Set user agent to avoid blocking
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            
            # Parse HTML and extract text
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header", "aside"]):
                script.decompose()
            
            # Convert to text using html2text
            text = html_converter.handle(str(soup))
            
            # Clean up: remove excessive whitespace
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            content = '\n'.join(lines)
            
            # Limit content length to avoid token limits (keep first 5000 chars)
            if len(content) > 5000:
                content = content[:5000] + "... (truncated)"
            
            logger.debug(f"Fetched content from {url}: {len(content)} characters")
            return content
            
    except httpx.TimeoutException:
        logger.warning(f"Timeout fetching {url}")
        return ""
    except httpx.HTTPStatusError as e:
        logger.warning(f"HTTP error fetching {url}: {e.response.status_code}")
        return ""
    except Exception as e:
        logger.warning(f"Error fetching {url}: {str(e)}")
        return ""


async def search_web(query: str, num_results: int = 10, fetch_content: bool = True, max_content_results: int = 5) -> List[Dict[str, Any]]:
    """
    Search the web using Google Custom Search API and optionally fetch full content.
    
    Args:
        query: Search query
        num_results: Number of results to return (max 10 per page)
        fetch_content: Whether to fetch full content of top results
        max_content_results: Maximum number of results to fetch full content for
        
    Returns:
        List of search results with title, link, snippet, and optionally full_content
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
                result = {
                    "title": item.get("title", ""),
                    "link": item.get("link", ""),
                    "snippet": item.get("snippet", ""),
                }
                results.append(result)
            
            # Fetch full content for top results if requested
            if fetch_content and results:
                logger.info(f"Fetching full content for top {min(max_content_results, len(results))} results")
                
                # Fetch content concurrently for top results
                fetch_tasks = []
                for i, result in enumerate(results[:max_content_results]):
                    fetch_tasks.append(fetch_url_content(result["link"]))
                
                # Wait for all fetches to complete
                contents = await asyncio.gather(*fetch_tasks, return_exceptions=True)
                
                # Add content to results
                for i, content in enumerate(contents):
                    if i < len(results):
                        if isinstance(content, Exception):
                            logger.warning(f"Error fetching content for {results[i]['link']}: {str(content)}")
                            results[i]["full_content"] = ""
                        else:
                            results[i]["full_content"] = content
                            if content:
                                logger.info(f"Fetched {len(content)} characters from {results[i]['link']}")
            
            logger.info(f"Web search completed: {len(results)} results for query: {query}")
            return results
            
    except httpx.HTTPStatusError as e:
        logger.error(f"Google Search API error: {e.response.status_code} - {e.response.text}")
        return []
    except Exception as e:
        logger.error(f"Web search error: {str(e)}")
        return []

