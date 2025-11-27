"""Web search node for external information research."""
from typing import Dict, Any
import asyncio
from app.integrations.web_search_client import search_web
from app.core.logging import get_logger

logger = get_logger(__name__)


def web_search_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Search the web for information.
    
    Args:
        state: Current graph state
        
    Returns:
        Updated state with web_results and kb_context
    """
    user_input = state.get("user_input", "")
    chat_context = state.get("chat_context", "")
    
    # Build search query
    query = f"{user_input} {chat_context}".strip()
    
    # Perform search
    try:
        # Run async search
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If already in async context, use asyncio.create_task
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, search_web(query, num_results=10))
                results = future.result()
        else:
            results = asyncio.run(search_web(query, num_results=10))
        
        state["web_results"] = results
        
        # Summarize results for kb_context
        if results:
            summaries = [f"{r.get('title', '')}: {r.get('snippet', '')}" for r in results[:5]]
            state["kb_context"] = "\n\n".join(summaries)
        else:
            state["kb_context"] = "No web search results found."
        
        logger.info(f"Web search completed: {len(results)} results")
        
    except Exception as e:
        logger.error(f"Web search error: {str(e)}")
        state["web_results"] = []
        state["kb_context"] = f"Error during web search: {str(e)}"
    
    return state

