"""Workspace service."""
from typing import List
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.workspace import Workspace
from app.repositories.workspace_repo import WorkspaceRepository
from app.schemas.workspace import WorkspaceCreate, WorkspaceUpdate
from app.core.logging import get_logger

logger = get_logger(__name__)


class WorkspaceService:
    """Service for workspace operations."""
    
    @staticmethod
    def create_workspace(db: Session, user: User, workspace_data: WorkspaceCreate) -> Workspace:
        """Create a new workspace."""
        workspace = WorkspaceRepository.create(
            db,
            name=workspace_data.name,
            owner_id=user.id
        )
        logger.info(f"Workspace created: {workspace.name} by user {user.username}")
        return workspace
    
    @staticmethod
    def get_user_workspaces(db: Session, user: User) -> List[Workspace]:
        """Get all workspaces owned by user."""
        return WorkspaceRepository.get_by_owner(db, user.id)
    
    @staticmethod
    def get_workspace(db: Session, workspace_id: int, user: User) -> Workspace:
        """Get workspace by ID, ensuring user owns it."""
        workspace = WorkspaceRepository.get_by_id(db, workspace_id)
        if not workspace:
            raise ValueError("Workspace not found")
        
        if workspace.owner_id != user.id:
            raise ValueError("Access denied")
        
        return workspace
    
    @staticmethod
    def update_workspace(
        db: Session,
        workspace_id: int,
        user: User,
        workspace_data: WorkspaceUpdate
    ) -> Workspace:
        """Update workspace."""
        workspace = WorkspaceService.get_workspace(db, workspace_id, user)
        
        update_data = workspace_data.dict(exclude_unset=True)
        if update_data:
            workspace = WorkspaceRepository.update(db, workspace, **update_data)
            logger.info(f"Workspace updated: {workspace.id}")
        
        return workspace
    
    @staticmethod
    def delete_workspace(db: Session, workspace_id: int, user: User) -> None:
        """Delete workspace and all related data."""
        workspace = WorkspaceService.get_workspace(db, workspace_id, user)
        
        # Delete all related data before deleting workspace
        # This prevents foreign key constraint violations
        
        # Delete connected apps
        from app.repositories.connected_app_repo import ConnectedAppRepository
        connected_apps = ConnectedAppRepository.get_by_workspace(db, workspace_id)
        for app in connected_apps:
            ConnectedAppRepository.delete(db, app)
        if connected_apps:
            logger.info(f"Deleted {len(connected_apps)} connected apps for workspace {workspace_id}")
        
        # Delete conversations and their messages
        from app.repositories.conversation_repo import ConversationRepository
        from app.repositories.message_repo import MessageRepository
        # Get all conversations (no limit to ensure we get all)
        conversations = ConversationRepository.get_by_workspace(db, workspace_id, limit=100000, offset=0)
        total_messages_deleted = 0
        for conv in conversations:
            # Delete all messages in conversation first
            messages = MessageRepository.get_by_conversation(db, conv.id, limit=None)
            for msg in messages:
                MessageRepository.delete(db, msg)
                total_messages_deleted += 1
            # Then delete conversation
            ConversationRepository.delete(db, conv)
        if conversations:
            logger.info(f"Deleted {len(conversations)} conversations and {total_messages_deleted} messages for workspace {workspace_id}")
        
        # Delete deprecated app_connections if any
        from app.repositories.app_connection_repo import AppConnectionRepository
        try:
            app_connections = AppConnectionRepository.get_by_workspace(db, workspace_id)
            for conn in app_connections:
                AppConnectionRepository.delete(db, conn)
            if app_connections:
                logger.info(f"Deleted {len(app_connections)} app connections for workspace {workspace_id}")
        except Exception as e:
            logger.debug(f"No app_connections to delete or error: {e}")
        
        # Delete deprecated mcp_connections if any
        from app.repositories.mcp_connection_repo import MCPConnectionRepository
        try:
            mcp_connections = MCPConnectionRepository.get_by_workspace(db, workspace_id)
            for conn in mcp_connections:
                MCPConnectionRepository.delete(db, conn)
            if mcp_connections:
                logger.info(f"Deleted {len(mcp_connections)} MCP connections for workspace {workspace_id}")
        except Exception as e:
            logger.debug(f"No mcp_connections to delete or error: {e}")
        
        # Now safe to delete workspace
        WorkspaceRepository.delete(db, workspace)
        logger.info(f"Workspace deleted: {workspace_id}")

