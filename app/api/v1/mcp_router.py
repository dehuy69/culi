"""MCP connection router."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.repositories.mcp_connection_repo import MCPConnectionRepository
from app.repositories.workspace_repo import WorkspaceRepository
from app.models.mcp_connection import MCPConnectionType, MCPConnectionStatus
from app.utils.crypto import encrypt, decrypt
from app.integrations.kiotviet_oauth import get_access_token, clear_token_cache
from app.api.deps import get_current_user
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/workspaces/{workspace_id}/mcp", tags=["mcp"])


class MCPConnectionCreate(BaseModel):
    """MCP connection creation request."""
    type: str = "kiotviet"
    client_id: str
    client_secret: str
    retailer: Optional[str] = None


class MCPConnectionUpdate(BaseModel):
    """MCP connection update request."""
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    retailer: Optional[str] = None


@router.post("/connect")
def create_mcp_connection(
    workspace_id: int,
    connection_data: MCPConnectionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create or update MCP connection."""
    # Verify workspace ownership
    workspace = WorkspaceRepository.get_by_id(db, workspace_id)
    if not workspace or workspace.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")
    
    # Encrypt client_secret
    encrypted_secret = encrypt(connection_data.client_secret)
    
    # Check if connection exists
    existing = MCPConnectionRepository.get_by_workspace(
        db,
        workspace_id,
        MCPConnectionType.KIOTVIET
    )
    
    if existing:
        # Update existing
        connection = MCPConnectionRepository.update(
            db,
            existing,
            client_id=connection_data.client_id,
            client_secret_encrypted=encrypted_secret,
            retailer=connection_data.retailer,
        )
    else:
        # Create new
        connection = MCPConnectionRepository.create(
            db,
            workspace_id=workspace_id,
            connection_type=MCPConnectionType.KIOTVIET,
            client_id=connection_data.client_id,
            client_secret_encrypted=encrypted_secret,
            retailer=connection_data.retailer,
        )
    
    return {"message": "MCP connection configured", "connection_id": connection.id}


@router.post("/test")
async def test_mcp_connection(
    workspace_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Test MCP connection."""
    # Verify workspace ownership
    workspace = WorkspaceRepository.get_by_id(db, workspace_id)
    if not workspace or workspace.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")
    
    # Get connection
    connection = MCPConnectionRepository.get_by_workspace(
        db,
        workspace_id,
        MCPConnectionType.KIOTVIET
    )
    
    if not connection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="MCP connection not found")
    
    try:
        # Decrypt and test
        client_secret = decrypt(connection.client_secret_encrypted)
        access_token = await get_access_token(connection.client_id, client_secret)
        
        # Update status
        MCPConnectionRepository.update(db, connection, status=MCPConnectionStatus.ACTIVE)
        
        return {"status": "success", "message": "Connection test successful"}
        
    except Exception as e:
        # Update status to error
        MCPConnectionRepository.update(db, connection, status=MCPConnectionStatus.ERROR)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Connection test failed: {str(e)}"
        )


@router.get("/status")
def get_mcp_connection_status(
    workspace_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get MCP connection status."""
    # Verify workspace ownership
    workspace = WorkspaceRepository.get_by_id(db, workspace_id)
    if not workspace or workspace.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")
    
    # Get connection
    connection = MCPConnectionRepository.get_by_workspace(
        db,
        workspace_id,
        MCPConnectionType.KIOTVIET
    )
    
    if not connection:
        return {"connected": False, "status": "not_configured"}
    
    return {
        "connected": connection.status == MCPConnectionStatus.ACTIVE,
        "status": connection.status.value,
        "type": connection.type.value,
        "retailer": connection.retailer,
    }

