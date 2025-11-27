"""MCP connection model."""
from sqlalchemy import Column, String, Integer, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum
from app.db.base import BaseModel


class MCPConnectionStatus(str, enum.Enum):
    """MCP connection status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"


class MCPConnectionType(str, enum.Enum):
    """MCP connection type."""
    KIOTVIET = "kiotviet"


class MCPConnection(BaseModel):
    """MCP connection configuration per workspace."""
    
    __tablename__ = "mcp_connections"
    
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=False, index=True)
    type = Column(SQLEnum(MCPConnectionType), nullable=False, default=MCPConnectionType.KIOTVIET)
    client_id = Column(String(200), nullable=False)
    client_secret_encrypted = Column(String(500), nullable=False)
    retailer = Column(String(200), nullable=True)  # KiotViet retailer name
    status = Column(SQLEnum(MCPConnectionStatus), nullable=False, default=MCPConnectionStatus.INACTIVE)
    
    # Relationships
    workspace = relationship("Workspace", backref="mcp_connections")
    
    def __repr__(self):
        return f"<MCPConnection(id={self.id}, workspace_id={self.workspace_id}, type={self.type})>"

