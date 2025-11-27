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
        """Delete workspace."""
        workspace = WorkspaceService.get_workspace(db, workspace_id, user)
        WorkspaceRepository.delete(db, workspace)
        logger.info(f"Workspace deleted: {workspace_id}")

