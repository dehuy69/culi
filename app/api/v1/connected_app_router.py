"""Connected app router for managing workspace connected apps."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.connected_app import ConnectedApp
from app.repositories.connected_app_repo import ConnectedAppRepository
from app.repositories.workspace_repo import WorkspaceRepository
from app.services.connected_app_service import ConnectedAppService
from app.domain.apps.base import AppCategory, ConnectionMethod
from app.schemas.connected_app import (
    ConnectedAppCreate,
    ConnectedAppUpdate,
    ConnectedAppResponse,
    SupportedAppResponse,
    TestConnectionResponse,
)
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/workspaces/{workspace_id}/connected-apps", tags=["connected-apps"])


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
    
    apps = ConnectedAppService.get_supported_apps()
    return apps


@router.post("/connect", response_model=ConnectedAppResponse)
def create_connected_app(
    workspace_id: int,
    connection_data: ConnectedAppCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create connection for app."""
    # Verify workspace access
    workspace = WorkspaceRepository.get_by_id(db, workspace_id)
    if not workspace or workspace.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found"
        )
    
    try:
        connected_app = ConnectedAppService.create_connected_app(
            db=db,
            workspace_id=workspace_id,
            app_id=connection_data.app_id,
            name=connection_data.name,
            app_category=connection_data.app_category,
            connection_method=connection_data.connection_method,
            client_id=connection_data.client_id,
            client_secret=connection_data.client_secret,
            retailer=connection_data.retailer,
            mcp_server_url=connection_data.mcp_server_url,
            mcp_auth_type=connection_data.mcp_auth_type,
            mcp_auth_config=connection_data.mcp_auth_config,
            config_json=connection_data.config_json,
            is_default=connection_data.is_default,
        )
        return ConnectedAppResponse(
            id=connected_app.id,
            workspace_id=connected_app.workspace_id,
            name=connected_app.name,
            app_id=connected_app.app_id,
            app_category=connected_app.app_category.value,
            connection_method=connected_app.connection_method.value,
            retailer=connected_app.retailer,
            status=connected_app.status.value,
            is_default=connected_app.is_default,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/connections", response_model=List[ConnectedAppResponse])
def list_connections(
    workspace_id: int,
    app_category: Optional[str] = None,
    connection_method: Optional[str] = None,
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
    
    # Filter by category/method if provided
    category_enum = None
    if app_category:
        try:
            category_enum = AppCategory(app_category)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid app_category: {app_category}"
            )
    
    method_enum = None
    if connection_method:
        try:
            method_enum = ConnectionMethod(connection_method)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid connection_method: {connection_method}"
            )
    
    connections = ConnectedAppRepository.get_by_workspace(
        db, workspace_id, category_enum, method_enum
    )
    
    return [
        ConnectedAppResponse(
            id=conn.id,
            workspace_id=conn.workspace_id,
            name=conn.name,
            app_id=conn.app_id,
            app_category=conn.app_category.value,
            connection_method=conn.connection_method.value,
            retailer=conn.retailer,
            status=conn.status.value,
            is_default=conn.is_default,
        )
        for conn in connections
    ]


@router.get("/connections/{connection_id}", response_model=ConnectedAppResponse)
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
    
    connection = ConnectedAppRepository.get_by_id(db, connection_id)
    if not connection or connection.workspace_id != workspace_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connection not found"
        )
    
    return ConnectedAppResponse(
        id=connection.id,
        workspace_id=connection.workspace_id,
        name=connection.name,
        app_id=connection.app_id,
        app_category=connection.app_category.value,
        connection_method=connection.connection_method.value,
        retailer=connection.retailer,
        status=connection.status.value,
        is_default=connection.is_default,
    )


@router.put("/connections/{connection_id}", response_model=ConnectedAppResponse)
def update_connection(
    workspace_id: int,
    connection_id: int,
    update_data: ConnectedAppUpdate,
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
    
    connection = ConnectedAppRepository.get_by_id(db, connection_id)
    if not connection or connection.workspace_id != workspace_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connection not found"
        )
    
    from app.models.connected_app import ConnectionStatus
    from app.utils.crypto import encrypt
    import json
    
    # Encrypt secrets if provided
    client_secret_encrypted = None
    if update_data.client_secret:
        client_secret_encrypted = encrypt(update_data.client_secret)
    
    mcp_auth_config_encrypted = None
    if update_data.mcp_auth_config:
        mcp_auth_config_encrypted = encrypt(json.dumps(update_data.mcp_auth_config))
    
    status_enum = None
    if update_data.status:
        try:
            status_enum = ConnectionStatus(update_data.status)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {update_data.status}"
            )
    
    updated = ConnectedAppRepository.update(
        db=db,
        connected_app=connection,
        name=update_data.name,
        status=status_enum,
        client_id=update_data.client_id,
        client_secret_encrypted=client_secret_encrypted,
        retailer=update_data.retailer,
        mcp_server_url=update_data.mcp_server_url,
        mcp_auth_config_encrypted=mcp_auth_config_encrypted,
        config_json=update_data.config_json,
    )
    
    return ConnectedAppResponse(
        id=updated.id,
        workspace_id=updated.workspace_id,
        name=updated.name,
        app_id=updated.app_id,
        app_category=updated.app_category.value,
        connection_method=updated.connection_method.value,
        retailer=updated.retailer,
        status=updated.status.value,
        is_default=updated.is_default,
    )


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
    
    connection = ConnectedAppRepository.get_by_id(db, connection_id)
    if not connection or connection.workspace_id != workspace_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connection not found"
        )
    
    ConnectedAppRepository.delete(db, connection)
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
    
    connection = ConnectedAppRepository.get_by_id(db, connection_id)
    if not connection or connection.workspace_id != workspace_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connection not found"
        )
    
    try:
        result = await ConnectedAppService.test_connection(db, connection_id)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/connections/{connection_id}/set-default", response_model=ConnectedAppResponse)
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
        connection = ConnectedAppService.set_default_connection(
            db=db,
            workspace_id=workspace_id,
            connection_id=connection_id
        )
        return ConnectedAppResponse(
            id=connection.id,
            workspace_id=connection.workspace_id,
            name=connection.name,
            app_id=connection.app_id,
            app_category=connection.app_category.value,
            connection_method=connection.connection_method.value,
            retailer=connection.retailer,
            status=connection.status.value,
            is_default=connection.is_default,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

