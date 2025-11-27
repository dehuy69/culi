"""Factory for creating app connection clients."""
from typing import Any, Optional
from app.models.app_connection import AppConnection, ConnectionType, SupportedAppType
from app.integrations.kiotviet_direct_client import KiotVietDirectClient
from app.utils.crypto import decrypt
from app.core.logging import get_logger

logger = get_logger(__name__)


# Placeholder for future MCP client
class MCPClient:
    """Generic MCP client for custom MCP servers."""
    # TODO: Implement in Phase 3
    pass


def create_app_client(connection: AppConnection) -> Any:
    """
    Factory function to create appropriate client based on connection type.
    
    Args:
        connection: AppConnection model instance
        
    Returns:
        Client instance (KiotVietDirectClient, MCPClient, etc.)
        
    Raises:
        ValueError: If connection type is invalid or required fields are missing
    """
    if connection.connection_type == ConnectionType.SUPPORTED_APP:
        if connection.supported_app_type == SupportedAppType.KIOTVIET:
            # KiotViet: Always use direct API client
            if not connection.client_id or not connection.client_secret_encrypted:
                raise ValueError("KiotViet connection requires client_id and client_secret")
            if not connection.retailer:
                raise ValueError("KiotViet connection requires retailer name")
            
            # Decrypt client secret
            client_secret = decrypt(connection.client_secret_encrypted)
            
            logger.info(f"Creating KiotVietDirectClient for connection {connection.id}")
            return KiotVietDirectClient(
                client_id=connection.client_id,
                client_secret=client_secret,
                retailer=connection.retailer
            )
        else:
            raise ValueError(f"Unsupported app type: {connection.supported_app_type}")
    
    elif connection.connection_type == ConnectionType.CUSTOM_MCP:
        if not connection.mcp_server_url:
            raise ValueError("Custom MCP connection requires mcp_server_url")
        
        # TODO: Implement MCPClient in Phase 3
        raise NotImplementedError("Custom MCP client not yet implemented")
    
    else:
        raise ValueError(f"Invalid connection type: {connection.connection_type}")


async def close_client(client: Any) -> None:
    """
    Close client connection if it has a close method.
    
    Args:
        client: Client instance
    """
    if hasattr(client, "close"):
        if callable(client.close):
            # Check if it's async
            import asyncio
            if asyncio.iscoroutinefunction(client.close):
                await client.close()
            else:
                client.close()

