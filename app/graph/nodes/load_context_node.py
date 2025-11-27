"""Load context node to load workspace, connected app, and conversation history."""
from typing import Dict, Any
from app.repositories.connected_app_repo import ConnectedAppRepository
from app.repositories.conversation_repo import ConversationRepository
from app.repositories.message_repo import MessageRepository, MessageSender
from app.domain.apps.base import ConnectedAppConfig, AppCategory, ConnectionMethod
from app.utils.crypto import decrypt
from app.core.logging import get_logger

logger = get_logger(__name__)


def load_context_node(state: Dict[str, Any], db=None) -> Dict[str, Any]:
    """
    Load workspace context: connected app and conversation history.
    Can be done in ChatService instead - this node is optional.
    
    Args:
        state: Current graph state
        db: Database session (will be loaded from context if not provided)
        
    Returns:
        Updated state with connected_app and messages
    """
    workspace_id = state.get("workspace_id")
    conversation_id = state.get("conversation_id")
    
    if not workspace_id or not db:
        logger.warning("No workspace_id or db session in state")
        return state
    
    try:
        # Load default connected app for workspace
        connected_app_model = ConnectedAppRepository.get_default(db, int(workspace_id))
        
        if not connected_app_model:
            # Try to get any active connection
            all_connections = ConnectedAppRepository.get_by_workspace(db, int(workspace_id))
            active_connections = [c for c in all_connections if c.status.value == "active"]
            if active_connections:
                connected_app_model = active_connections[0]
                logger.info(f"Using first active connection: {connected_app_model.id} (no default set)")
        
        # Map to ConnectedAppConfig
        if connected_app_model:
            # Build credentials dict
            credentials = {}
            if connected_app_model.connection_method == ConnectionMethod.API:
                if connected_app_model.client_id and connected_app_model.client_secret_encrypted:
                    credentials["client_id"] = connected_app_model.client_id
                    credentials["client_secret"] = decrypt(connected_app_model.client_secret_encrypted)
                if connected_app_model.retailer:
                    credentials["retailer"] = connected_app_model.retailer
            elif connected_app_model.connection_method == ConnectionMethod.MCP:
                if connected_app_model.mcp_server_url:
                    credentials["mcp_server_url"] = connected_app_model.mcp_server_url
                if connected_app_model.mcp_auth_config_encrypted:
                    import json
                    credentials["mcp_auth_config"] = json.loads(decrypt(connected_app_model.mcp_auth_config_encrypted))
            
            # Add extra config from config_json
            if connected_app_model.config_json:
                credentials.update(connected_app_model.config_json)
            
            # Create ConnectedAppConfig
            app_config = ConnectedAppConfig(
                app_id=connected_app_model.app_id,
                name=connected_app_model.name,
                category=connected_app_model.app_category,
                connection_method=connected_app_model.connection_method,
                credentials=credentials,
                extra={},
            )
            
            # Map to state format (ConnectedApp TypedDict)
            state["connected_app"] = {
                "id": str(connected_app_model.id),
                "name": connected_app_model.name,
                "category": connected_app_model.app_category.value,
                "connection_method": connected_app_model.connection_method.value,
                "config": app_config.dict(),
            }
            
            logger.info(f"Loaded connected app: {connected_app_model.name} ({connected_app_model.app_id})")
        else:
            logger.info(f"No connected app found for workspace {workspace_id}")
        
        # Load conversation history if conversation_id exists
        if conversation_id:
            try:
                messages = MessageRepository.get_by_conversation(db, int(conversation_id))
                # Convert to OpenAI format if not already done
                if "messages" not in state or not state["messages"]:
                    messages_format = []
                    for msg in messages:
                        messages_format.append({
                            "role": "user" if msg.sender == MessageSender.USER else "assistant",
                            "content": msg.content
                        })
                    state["messages"] = messages_format
            except Exception as e:
                logger.warning(f"Could not load conversation history: {str(e)}")
    
    except Exception as e:
        logger.error(f"Error in load_context_node: {str(e)}", exc_info=True)
        state["error"] = f"Failed to load context: {str(e)}"
    
    return state

