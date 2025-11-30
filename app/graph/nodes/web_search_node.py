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
        
        # Build kb_context from results
        if results:
            context_parts = []
            for r in results[:5]:  # Use top 5 results
                title = r.get("title", "")
                snippet = r.get("snippet", "")
                full_content = r.get("full_content", "")
                link = r.get("link", "")
                
                # Prefer full_content if available, otherwise use snippet
                if full_content:
                    context_parts.append(f"**{title}** ({link}):\n{full_content}")
                else:
                    context_parts.append(f"**{title}** ({link}): {snippet}")
            
            state["kb_context"] = "\n\n---\n\n".join(context_parts)
            logger.info(f"Built kb_context with {len(context_parts)} results, total length: {len(state['kb_context'])}")
        else:
            state["kb_context"] = "No web search results found."
        
        logger.info(f"Web search completed: {len(results)} results")
        
    except Exception as e:
        logger.error(f"Web search error: {str(e)}")
        state["web_results"] = []
        state["kb_context"] = f"Error during web search: {str(e)}"
    
    return state

