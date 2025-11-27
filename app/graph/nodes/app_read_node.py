"""App read node for querying data from apps using adapter pattern."""
from typing import Dict, Any
import asyncio
from app.domain.apps.base import ConnectedAppConfig, AppReadIntent
from app.domain.apps.registry import get_adapter
from app.core.logging import get_logger

logger = get_logger(__name__)


def detect_app_read_intent(user_input: str, app_category: str) -> AppReadIntent:
    """
    Detect what kind of data the user wants to read.
    
    Args:
        user_input: User's input text
        app_category: App category (POS_SIMPLE, ACCOUNTING, etc.)
        
    Returns:
        AppReadIntent with kind and params
    """
    user_lower = user_input.lower()
    
    # Simple heuristics - can be improved with LLM later
    if "hóa đơn" in user_lower or "invoice" in user_lower:
        return AppReadIntent(kind="LIST_INVOICES", params={"page_size": 20})
    
    elif "đơn hàng" in user_lower or "order" in user_lower:
        return AppReadIntent(kind="LIST_ORDERS", params={"page_size": 20})
    
    elif "sản phẩm" in user_lower or "hàng hóa" in user_lower or "product" in user_lower:
        return AppReadIntent(kind="LIST_PRODUCTS", params={"page_size": 20})
    
    elif "khách hàng" in user_lower or "customer" in user_lower:
        return AppReadIntent(kind="LIST_CUSTOMERS", params={"page_size": 20})
    
    elif "nhóm hàng" in user_lower or "danh mục" in user_lower or "category" in user_lower:
        return AppReadIntent(kind="LIST_CATEGORIES", params={"page_size": 100})
    
    elif "chi nhánh" in user_lower or "branch" in user_lower:
        return AppReadIntent(kind="LIST_BRANCHES", params={})
    
    elif "doanh thu" in user_lower or "revenue" in user_lower or "thống kê" in user_lower:
        # Calculate revenue from invoices
        return AppReadIntent(kind="SUMMARY_REVENUE", params={"page_size": 100})
    
    else:
        # Default: try to list products
        return AppReadIntent(kind="LIST_PRODUCTS", params={"page_size": 10})


async def app_read_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Read data from app using adapter pattern.
    Generic for all apps - uses adapter to dispatch.
    
    Args:
        state: Current graph state with connected_app
        
    Returns:
        Updated state with app_data
    """
    connected_app_dict = state.get("connected_app")
    user_input = state.get("user_input", "")
    
    if not connected_app_dict:
        logger.warning("No connected app available")
        state["app_data"] = {"error": "No app connection configured"}
        return state
    
    try:
        # Build ConnectedAppConfig from state
        app_config = ConnectedAppConfig(**connected_app_dict.get("config", {}))
        
        # Detect read intent
        read_intent = detect_app_read_intent(user_input, app_config.category.value)
        logger.info(f"Detected read intent: {read_intent.kind} for app: {app_config.app_id}")
        
        # Get adapter and read data
        adapter = get_adapter(app_config.app_id)
        data = adapter.read(read_intent, app_config)
        
        state["app_data"] = data
        logger.info(f"App read completed: {read_intent.kind}, result keys: {list(data.keys())}")
        
    except Exception as e:
        logger.error(f"App read error: {str(e)}", exc_info=True)
        state["app_data"] = {"error": str(e)}
    
    return state


def app_read_node_sync(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Synchronous wrapper for app_read_node.
    For use in LangGraph nodes that require synchronous functions.
    """
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If loop is already running, use thread pool
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, app_read_node(state))
                return future.result()
        else:
            return asyncio.run(app_read_node(state))
    except RuntimeError:
        # No event loop, create new one
        return asyncio.run(app_read_node(state))
