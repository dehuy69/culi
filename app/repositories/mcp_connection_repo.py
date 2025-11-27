"""MCP connection repository for database operations."""
from typing import Optional
from sqlalchemy.orm import Session
from app.models.mcp_connection import MCPConnection, MCPConnectionStatus, MCPConnectionType


class MCPConnectionRepository:
    """Repository for MCPConnection model operations."""
    
    @staticmethod
    def get_by_id(db: Session, connection_id: int) -> Optional[MCPConnection]:
        """Get MCP connection by ID."""
        return db.query(MCPConnection).filter(MCPConnection.id == connection_id).first()
    
    @staticmethod
    def get_by_workspace(
        db: Session,
        workspace_id: int,
        connection_type: Optional[MCPConnectionType] = None
    ) -> Optional[MCPConnection]:
        """Get MCP connection by workspace."""
        query = db.query(MCPConnection).filter(MCPConnection.workspace_id == workspace_id)
        
        if connection_type:
            query = query.filter(MCPConnection.type == connection_type)
        
        return query.first()
    
    @staticmethod
    def create(
        db: Session,
        workspace_id: int,
        connection_type: MCPConnectionType,
        client_id: str,
        client_secret_encrypted: str,
        retailer: Optional[str] = None
    ) -> MCPConnection:
        """Create a new MCP connection."""
        connection = MCPConnection(
            workspace_id=workspace_id,
            type=connection_type,
            client_id=client_id,
            client_secret_encrypted=client_secret_encrypted,
            retailer=retailer,
            status=MCPConnectionStatus.INACTIVE
        )
        db.add(connection)
        db.commit()
        db.refresh(connection)
        return connection
    
    @staticmethod
    def update(
        db: Session,
        connection: MCPConnection,
        client_id: Optional[str] = None,
        client_secret_encrypted: Optional[str] = None,
        retailer: Optional[str] = None,
        status: Optional[MCPConnectionStatus] = None
    ) -> MCPConnection:
        """Update MCP connection."""
        if client_id is not None:
            connection.client_id = client_id
        if client_secret_encrypted is not None:
            connection.client_secret_encrypted = client_secret_encrypted
        if retailer is not None:
            connection.retailer = retailer
        if status is not None:
            connection.status = status
        
        db.commit()
        db.refresh(connection)
        return connection
    
    @staticmethod
    def delete(db: Session, connection: MCPConnection) -> None:
        """Delete MCP connection."""
        db.delete(connection)
        db.commit()

