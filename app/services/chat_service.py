"""Chat service for orchestrating LangGraph execution."""
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.conversation import Conversation
from app.models.message import Message, MessageSender
from app.repositories.conversation_repo import ConversationRepository
from app.repositories.message_repo import MessageRepository
from app.repositories.mcp_connection_repo import MCPConnectionRepository
from app.repositories.workspace_repo import WorkspaceRepository
from app.utils.crypto import decrypt
from app.graph.app_graph import get_graph
from app.graph.state import CuliState
from app.core.logging import get_logger

logger = get_logger(__name__)


class ChatService:
    """Service for chat operations."""
    
    @staticmethod
    def prepare_state(
        db: Session,
        user: User,
        workspace_id: int,
        conversation_id: Optional[int],
        user_input: str
    ) -> Dict[str, Any]:
        """Prepare initial state for LangGraph."""
        # Get or create conversation
        if conversation_id:
            conversation = ConversationRepository.get_by_id(db, conversation_id)
            if not conversation or conversation.workspace_id != workspace_id:
                raise ValueError("Conversation not found or access denied")
        else:
            conversation = ConversationRepository.create(db, workspace_id, title=None)
            conversation_id = conversation.id
        
        # Load chat history
        messages = MessageRepository.get_by_conversation(db, conversation_id)
        messages_openai_format = [
            {
                "role": "user" if msg.sender == MessageSender.USER else "assistant",
                "content": msg.content
            }
            for msg in messages
        ]
        
        # Add current user message
        messages_openai_format.append({
            "role": "user",
            "content": user_input
        })
        
        # Get connected app (new system)
        from app.repositories.connected_app_repo import ConnectedAppRepository
        from app.domain.apps.base import ConnectedAppConfig, AppCategory, ConnectionMethod
        from app.utils.crypto import decrypt
        
        # Get default connected app for workspace
        connected_app_model = ConnectedAppRepository.get_default(db, workspace_id)
        
        if not connected_app_model:
            # Try to get any active connection
            all_connections = ConnectedAppRepository.get_by_workspace(db, workspace_id)
            active_connections = [c for c in all_connections if c.status.value == "active"]
            if active_connections:
                connected_app_model = active_connections[0]
                logger.info(f"Using first active connection: {connected_app_model.id} (no default set)")
        
        # Map to ConnectedAppConfig and state format
        connected_app = None
        if connected_app_model:
            # Build credentials dict
            credentials = {}
            if connected_app_model.connection_method.value == "api":
                if connected_app_model.client_id and connected_app_model.client_secret_encrypted:
                    credentials["client_id"] = connected_app_model.client_id
                    credentials["client_secret"] = decrypt(connected_app_model.client_secret_encrypted)
                if connected_app_model.retailer:
                    credentials["retailer"] = connected_app_model.retailer
            elif connected_app_model.connection_method.value == "mcp":
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
            connected_app = {
                "id": str(connected_app_model.id),
                "name": connected_app_model.name,
                "category": connected_app_model.app_category.value,
                "connection_method": connected_app_model.connection_method.value,
                "config": app_config.dict(),
            }
            
            logger.info(f"Loaded connected app: {connected_app_model.name} ({connected_app_model.app_id})")
        
        # Build initial state
        state: CuliState = {
            "user_id": str(user.id),
            "workspace_id": str(workspace_id),
            "conversation_id": str(conversation_id),
            "user_input": user_input,
            "messages": messages_openai_format,
            "connected_app": connected_app,  # NEW: connected app in new format
            "intent": "",
            "needs_web": False,
            "needs_app": False,  # NEW: changed from needs_mcp
            "needs_plan": False,
            "chat_context": "",
            "kb_context": "",
            "web_results": [],
            "app_data": {},  # NEW: changed from mcp_data
            "plan": None,
            "plan_approved": False,
            "current_step_index": 0,
            "step_results": [],
            "answer": "",
            "error": None,
            "stream_events": [],
        }
        
        return state, conversation_id
    
    @staticmethod
    def process_message(
        db: Session,
        user: User,
        workspace_id: int,
        conversation_id: Optional[int],
        user_input: str
    ) -> Dict[str, Any]:
        """Process a chat message through LangGraph."""
        # Verify workspace access
        workspace = WorkspaceRepository.get_by_id(db, workspace_id)
        if not workspace or workspace.owner_id != user.id:
            raise ValueError("Workspace not found or access denied")
        
        # Prepare state
        state, conversation_id = ChatService.prepare_state(
            db, user, workspace_id, conversation_id, user_input
        )
        
        # Save user message
        MessageRepository.create(
            db,
            conversation_id=conversation_id,
            sender=MessageSender.USER,
            content=user_input
        )
        
        # Execute graph
        graph = get_graph()
        
        try:
            # Invoke graph
            final_state = graph.invoke(state)
            
            # Get answer
            answer = final_state.get("answer", "Xin lỗi, không thể tạo phản hồi.")
            
            # Save assistant message
            MessageRepository.create(
                db,
                conversation_id=conversation_id,
                sender=MessageSender.ASSISTANT,
                content=answer,
                metadata={
                    "intent": final_state.get("intent"),
                    "plan": final_state.get("plan"),
                    "step_results": final_state.get("step_results"),
                }
            )
            
            return {
                "conversation_id": conversation_id,
                "answer": answer,
                "intent": final_state.get("intent"),
                "plan": final_state.get("plan"),
                "metadata": {
                    "intent": final_state.get("intent"),
                    "needs_plan_approval": bool(final_state.get("plan") and not final_state.get("plan_approved")),
                }
            }
            
        except ValueError as e:
            # Re-raise ValueError (e.g., missing API key) with clear message
            logger.error(f"Configuration error: {str(e)}", exc_info=True)
            raise ValueError(f"Configuration error: {str(e)}")
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}", exc_info=True)
            # Provide more user-friendly error message
            error_msg = str(e)
            
            # Handle specific error cases
            if "api_key" in error_msg.lower() or "OPENAI_API_KEY" in error_msg:
                error_msg = "API key chưa được cấu hình. Vui lòng kiểm tra OPENROUTER_API_KEY trong file .env"
            elif "402" in error_msg or "credits" in error_msg.lower() or "max_tokens" in error_msg.lower():
                error_msg = (
                    "OpenRouter API key của bạn không đủ credits để xử lý request này. "
                    "Vui lòng: 1) Tăng monthly limit tại https://openrouter.ai/settings/keys, "
                    "hoặc 2) Giảm độ dài câu hỏi. "
                    f"Chi tiết: {error_msg}"
                )
            
            raise Exception(f"Failed to process message: {error_msg}")

