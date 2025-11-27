"""Workspace repository for database operations."""
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.workspace import Workspace


class WorkspaceRepository:
    """Repository for Workspace model operations."""
    
    @staticmethod
    def get_by_id(db: Session, workspace_id: int) -> Optional[Workspace]:
        """Get workspace by ID."""
        return db.query(Workspace).filter(Workspace.id == workspace_id).first()
    
    @staticmethod
    def get_by_owner(db: Session, owner_id: int) -> List[Workspace]:
        """Get all workspaces owned by a user."""
        return db.query(Workspace).filter(Workspace.owner_id == owner_id).all()
    
    @staticmethod
    def create(db: Session, name: str, owner_id: int) -> Workspace:
        """Create a new workspace."""
        workspace = Workspace(name=name, owner_id=owner_id)
        db.add(workspace)
        db.commit()
        db.refresh(workspace)
        return workspace
    
    @staticmethod
    def update(db: Session, workspace: Workspace, name: Optional[str] = None) -> Workspace:
        """Update workspace."""
        if name is not None:
            workspace.name = name
        db.commit()
        db.refresh(workspace)
        return workspace
    
    @staticmethod
    def delete(db: Session, workspace: Workspace) -> None:
        """Delete workspace."""
        db.delete(workspace)
        db.commit()
    
    @staticmethod
    def is_owner(db: Session, workspace_id: int, user_id: int) -> bool:
        """Check if user owns the workspace."""
        workspace = db.query(Workspace).filter(
            Workspace.id == workspace_id,
            Workspace.owner_id == user_id
        ).first()
        return workspace is not None

