"""App connection router for managing workspace app connections."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.app_connection import AppConnection, ConnectionType
from app.repositories.app_connection_repo import AppConnectionRepository
from app.services.app_connection_service import AppConnectionService
from app.repositories.workspace_repo import WorkspaceRepository

router = APIRouter(prefix="/workspaces/{workspace_id}/apps", tags=["app-connections"])


# ========== Schemas ==========

class SupportedAppResponse(BaseModel):
    """Supported app information."""
    id: str
    name: str
    description: str
    requires_retailer: bool
    auth_method: str
    required_fields: List[str]
    
    class Config:
        from_attributes = True


class SupportedAppConnectionCreate(BaseModel):
    """Request to create supported app connection."""
    app_type: str  # "kiotviet", etc.
    name: str
    client_id: str
    client_secret: str
    retailer: Optional[str] = None
    is_default: bool = False


class CustomMCPConnectionCreate(BaseModel):
    """Request to create custom MCP connection."""
    name: str
    mcp_server_url: str
    auth_type: str = "none"  # "none", "api_key", "bearer", "basic"
    auth_config: Optional[dict] = None
    is_default: bool = False


class AppConnectionResponse(BaseModel):
    """App connection response."""
    id: int
    workspace_id: int
    name: str
    connection_type: str
    supported_app_type: Optional[str] = None
    mcp_server_url: Optional[str] = None
    retailer: Optional[str] = None
    status: str
    is_default: bool
    
    class Config:
        from_attributes = True


class ConnectionUpdate(BaseModel):
    """Request to update connection."""
    name: Optional[str] = None
    status: Optional[str] = None


class TestConnectionResponse(BaseModel):
    """Connection test result."""
    status: str
    message: str
    data: Optional[dict] = None


# ========== Endpoints ==========

@router.get("/supported", response_model=List[SupportedAppResponse])
def list_supported_apps(
    workspace_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all supported apps."""
    # Verify workspace access
    workspace = WorkspaceRepository.get_by_id(db, workspace_id)
    if not workspace or workspace.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )
    
    apps = AppConnectionService.get_supported_apps()
    return apps


@router.post("/connect", response_model=AppConnectionResponse)
def create_supported_app_connection(
    workspace_id: int,
    connection_data: SupportedAppConnectionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create connection for supported app."""
    # Verify workspace access
    workspace = WorkspaceRepository.get_by_id(db, workspace_id)
    if not workspace or workspace.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )
    
    try:
        connection = AppConnectionService.create_supported_app_connection(
            db=db,
            workspace_id=workspace_id,
            app_type=connection_data.app_type,
            name=connection_data.name,
            client_id=connection_data.client_id,
            client_secret=connection_data.client_secret,
            retailer=connection_data.retailer,
            is_default=connection_data.is_default,
        )
        return connection
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/connect-custom", response_model=AppConnectionResponse)
def create_custom_mcp_connection(
    workspace_id: int,
    connection_data: CustomMCPConnectionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create connection for custom MCP server."""
    # Verify workspace access
    workspace = WorkspaceRepository.get_by_id(db, workspace_id)
    if not workspace or workspace.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )
    
    try:
        connection = AppConnectionService.create_custom_mcp_connection(
            db=db,
            workspace_id=workspace_id,
            name=connection_data.name,
            mcp_server_url=connection_data.mcp_server_url,
            auth_type=connection_data.auth_type,
            auth_config=connection_data.auth_config,
            is_default=connection_data.is_default,
        )
        return connection
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/connections", response_model=List[AppConnectionResponse])
def list_connections(
    workspace_id: int,
    connection_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all connections for workspace."""
    # Verify workspace access
    workspace = WorkspaceRepository.get_by_id(db, workspace_id)
    if not workspace or workspace.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )
    
    # Filter by type if provided
    conn_type = None
    if connection_type:
        try:
            conn_type = ConnectionType(connection_type)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid connection_type: {connection_type}"
            )
    
    connections = AppConnectionRepository.get_by_workspace(
        db, workspace_id, conn_type
    )
    return connections


@router.get("/connections/{connection_id}", response_model=AppConnectionResponse)
def get_connection(
    workspace_id: int,
    connection_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get connection details."""
    # Verify workspace access
    workspace = WorkspaceRepository.get_by_id(db, workspace_id)
    if not workspace or workspace.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )
    
    connection = AppConnectionRepository.get_by_id(db, connection_id)
    if not connection or connection.workspace_id != workspace_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connection not found"
        )
    
    return connection


@router.put("/connections/{connection_id}", response_model=AppConnectionResponse)
def update_connection(
    workspace_id: int,
    connection_id: int,
    update_data: ConnectionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update connection."""
    # Verify workspace access
    workspace = WorkspaceRepository.get_by_id(db, workspace_id)
    if not workspace or workspace.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )
    
    connection = AppConnectionRepository.get_by_id(db, connection_id)
    if not connection or connection.workspace_id != workspace_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connection not found"
        )
    
    from app.models.app_connection import ConnectionStatus
    status_enum = None
    if update_data.status:
        try:
            status_enum = ConnectionStatus(update_data.status)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {update_data.status}"
            )
    
    updated = AppConnectionRepository.update(
        db=db,
        connection=connection,
        name=update_data.name,
        status=status_enum,
    )
    return updated


@router.delete("/connections/{connection_id}")
def delete_connection(
    workspace_id: int,
    connection_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete connection."""
    # Verify workspace access
    workspace = WorkspaceRepository.get_by_id(db, workspace_id)
    if not workspace or workspace.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )
    
    connection = AppConnectionRepository.get_by_id(db, connection_id)
    if not connection or connection.workspace_id != workspace_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connection not found"
        )
    
    AppConnectionRepository.delete(db, connection)
    return {"message": "Connection deleted"}


@router.post("/connections/{connection_id}/test", response_model=TestConnectionResponse)
async def test_connection(
    workspace_id: int,
    connection_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Test app connection."""
    # Verify workspace access
    workspace = WorkspaceRepository.get_by_id(db, workspace_id)
    if not workspace or workspace.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )
    
    connection = AppConnectionRepository.get_by_id(db, connection_id)
    if not connection or connection.workspace_id != workspace_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connection not found"
        )
    
    try:
        result = await AppConnectionService.test_connection(db, connection_id)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/connections/{connection_id}/set-default", response_model=AppConnectionResponse)
def set_default_connection(
    workspace_id: int,
    connection_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Set connection as default for workspace."""
    # Verify workspace access
    workspace = WorkspaceRepository.get_by_id(db, workspace_id)
    if not workspace or workspace.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )
    
    try:
        connection = AppConnectionService.set_default_connection(
            db=db,
            workspace_id=workspace_id,
            connection_id=connection_id
        )
        return connection
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

