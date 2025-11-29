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
                    try:
                        credentials["client_secret"] = decrypt(connected_app_model.client_secret_encrypted)
                    except Exception as e:
                        logger.error(f"Failed to decrypt client_secret: {str(e)}", exc_info=True)
                        raise ValueError(f"Failed to decrypt client_secret: {str(e)}")
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
            error_msg = str(e) if str(e) else f"{type(e).__name__}: {repr(e)}"
            logger.error(f"Error processing message: {error_msg}", exc_info=True)
            # Provide more user-friendly error message
            
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
    
    @staticmethod
    def stream_message(
        db: Session,
        user: User,
        workspace_id: int,
        conversation_id: Optional[int],
        user_input: str
    ):
        """
        Stream chat message processing through LangGraph.
        Yields events as they occur during graph execution.
        """
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
        
        # Get graph
        graph = get_graph()
        
        try:
            # Stream graph execution
            final_state = None
            for event in graph.stream(state):
                # Process each event (event is a dict: {node_name: state_update})
                for node_name, state_update in event.items():
                    # state_update is the updated state after node execution
                    current_state = state_update if isinstance(state_update, dict) else {}
                    
                    # Emit node start event
                    yield {
                        "event": "node_start",
                        "data": {
                            "node": node_name,
                            "timestamp": None  # Will be set by router
                        }
                    }
                    
                    # Emit specific events based on node and state
                    if node_name == "intent_router":
                        intent = current_state.get("intent", "")
                        if intent:
                            yield {
                                "event": "intent",
                                "data": {
                                    "intent": intent,
                                    "node": node_name
                                }
                            }
                    
                    elif node_name == "app_plan":
                        plan = current_state.get("plan")
                        if plan:
                            yield {
                                "event": "plan",
                                "data": {
                                    "plan": plan,
                                    "node": node_name
                                }
                            }
                    
                    elif node_name == "execute_plan":
                        step_results = current_state.get("step_results", [])
                        current_step_index = current_state.get("current_step_index", 0)
                        plan = current_state.get("plan", {})
                        steps = plan.get("steps", [])
                        
                        if step_results:
                            latest_step = step_results[-1]
                            yield {
                                "event": "step",
                                "data": {
                                    "step": latest_step,
                                    "current_step": current_step_index,
                                    "total_steps": len(steps),
                                    "node": node_name
                                }
                            }
                    
                    elif node_name == "web_search":
                        web_results = current_state.get("web_results", [])
                        if web_results:
                            yield {
                                "event": "web_search",
                                "data": {
                                    "results_count": len(web_results),
                                    "node": node_name
                                }
                            }
                    
                    elif node_name == "app_read":
                        app_data = current_state.get("app_data", {})
                        if app_data:
                            yield {
                                "event": "app_data",
                                "data": {
                                    "has_data": bool(app_data),
                                    "node": node_name
                                }
                            }
                    
                    elif node_name == "answer":
                        answer = current_state.get("answer", "")
                        error = current_state.get("error")
                        
                        # Always emit answer event when answer node completes
                        # This ensures frontend receives the answer even if it's empty (will be handled in done event)
                        if answer:
                            yield {
                                "event": "answer",
                                "data": {
                                    "content": answer,
                                    "node": node_name
                                }
                            }
                        elif error:
                            # If answer node hasn't generated answer yet but there's an error,
                            # emit error info so frontend can show it
                            yield {
                                "event": "answer",
                                "data": {
                                    "content": f"Đang xử lý lỗi: {error}",
                                    "node": node_name,
                                    "has_error": True
                                }
                            }
                        else:
                            # Even if answer is empty, emit event so frontend knows answer node completed
                            # The done event will provide the final answer
                            yield {
                                "event": "answer",
                                "data": {
                                    "content": "",
                                    "node": node_name,
                                    "pending": True
                                }
                            }
                    
                    # Emit node end event
                    yield {
                        "event": "node_end",
                        "data": {
                            "node": node_name,
                            "timestamp": None
                        }
                    }
                    
                    # Keep track of final state
                    final_state = current_state
            
            # Save assistant message if we have an answer
            if final_state:
                answer = final_state.get("answer", "")
                error = final_state.get("error")
                
                # If no answer but there's an error, create error message
                if not answer and error:
                    answer = f"Xin lỗi, đã xảy ra lỗi: {error}"
                    final_state["answer"] = answer
                
                # If still no answer, create default message
                if not answer:
                    answer = "Xin lỗi, không thể tạo phản hồi. Vui lòng thử lại."
                    final_state["answer"] = answer
                
                # Always save message (even if it's an error message)
                MessageRepository.create(
                    db,
                    conversation_id=conversation_id,
                    sender=MessageSender.ASSISTANT,
                    content=answer,
                    metadata={
                        "intent": final_state.get("intent"),
                        "plan": final_state.get("plan"),
                        "step_results": final_state.get("step_results"),
                        "error": error,
                    }
                )
                
                # Always emit completion event (even if answer is error message)
                yield {
                    "event": "done",
                    "data": {
                        "conversation_id": conversation_id,
                        "answer": answer,
                        "intent": final_state.get("intent"),
                        "plan": final_state.get("plan"),
                        "error": error,
                    }
                }
            
        except ValueError as e:
            logger.error(f"Configuration error in stream: {str(e)}", exc_info=True)
            yield {
                "event": "error",
                "data": {
                    "error": f"Configuration error: {str(e)}",
                    "type": "configuration"
                }
            }
        except Exception as e:
            error_msg = str(e) if str(e) else f"{type(e).__name__}: {repr(e)}"
            logger.error(f"Error streaming message: {error_msg}", exc_info=True)
            
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
            
            yield {
                "event": "error",
                "data": {
                    "error": f"Failed to process message: {error_msg}",
                    "type": "processing"
                }
            }

