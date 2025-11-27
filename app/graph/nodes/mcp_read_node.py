"""MCP read node for querying KiotViet data."""
from typing import Dict, Any
import asyncio
import json
from app.integrations.kiotviet_mcp_client import KiotVietMCPClient
from app.core.logging import get_logger
from app.core.llm_config import get_llm

logger = get_logger(__name__)


def mcp_read_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Read data from KiotViet via MCP.
    
    Args:
        state: Current graph state
        
    Returns:
        Updated state with mcp_data
    """
    mcp_connection = state.get("mcp_connection")
    user_input = state.get("user_input", "")
    
    if not mcp_connection:
        logger.warning("No MCP connection available")
        state["mcp_data"] = {"error": "No MCP connection configured"}
        return state
    
    try:
        # Create MCP client
        client = KiotVietMCPClient(
            client_id=mcp_connection["client_id"],
            client_secret=mcp_connection["client_secret"],
            retailer=mcp_connection.get("retailer", "")
        )
        
        # Determine which MCP tool to call based on user input
        # TODO: Use LLM to intelligently select the right tool
        # For now, try common queries
        
        # Simple heuristics for tool selection
        user_lower = user_input.lower()
        results = {}
        
        if "product" in user_lower or "sản phẩm" in user_lower or "hàng hóa" in user_lower:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, client.list_products(page_size=20))
                    results["products"] = future.result()
            else:
                results["products"] = asyncio.run(client.list_products(page_size=20))
        
        elif "invoice" in user_lower or "hóa đơn" in user_lower:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, client.list_invoices(page_size=20))
                    results["invoices"] = future.result()
            else:
                results["invoices"] = asyncio.run(client.list_invoices(page_size=20))
        
        elif "order" in user_lower or "đơn hàng" in user_lower:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, client.list_orders(page_size=20))
                    results["orders"] = future.result()
            else:
                results["orders"] = asyncio.run(client.list_orders(page_size=20))
        
        elif "customer" in user_lower or "khách hàng" in user_lower:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, client.search_customers(page_size=20))
                    results["customers"] = future.result()
            else:
                results["customers"] = asyncio.run(client.search_customers(page_size=20))
        
        else:
            # Default: try to list products
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, client.list_products(page_size=10))
                    results["products"] = future.result()
            else:
                results["products"] = asyncio.run(client.list_products(page_size=10))
        
        state["mcp_data"] = results
        logger.info(f"MCP read completed: {list(results.keys())}")
        
    except Exception as e:
        logger.error(f"MCP read error: {str(e)}")
        state["mcp_data"] = {"error": str(e)}
    
    return state

