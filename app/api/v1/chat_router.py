"""Chat router."""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.services.chat_service import ChatService
from app.repositories.conversation_repo import ConversationRepository
from app.repositories.message_repo import MessageRepository
from app.schemas.chat import ChatRequest, ChatMessage, ConversationOut, ConversationListResponse
from app.api.deps import get_current_user

router = APIRouter(prefix="/workspaces/{workspace_id}/chat", tags=["chat"])


@router.post("")
def send_message(
    workspace_id: int,
    chat_request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a chat message and get response."""
    try:
        result = ChatService.process_message(
            db,
            current_user,
            workspace_id,
            chat_request.conversation_id,
            chat_request.message
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/conversations", response_model=ConversationListResponse)
def list_conversations(
    workspace_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List conversations in a workspace."""
    conversations = ConversationRepository.get_by_workspace(db, workspace_id, limit=50, offset=0)
    return ConversationListResponse(
        conversations=[ConversationOut.from_orm(c) for c in conversations],
        total=len(conversations)
    )


@router.get("/conversations/{conversation_id}/messages", response_model=List[ChatMessage])
def get_messages(
    workspace_id: int,
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get messages from a conversation."""
    # Verify conversation belongs to workspace
    if not ConversationRepository.belongs_to_workspace(db, conversation_id, workspace_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    
    messages = MessageRepository.get_by_conversation(db, conversation_id)
    return [ChatMessage.from_orm(m) for m in messages]

