"""App connection model for workspace app integrations."""
from sqlalchemy import Column, String, Integer, ForeignKey, Enum as SQLEnum, JSON, Boolean
from sqlalchemy.orm import relationship
import enum
from typing import Optional
from app.db.base import BaseModel


class ConnectionStatus(str, enum.Enum):
    """Connection status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"


class ConnectionType(str, enum.Enum):
    """Connection type."""
    SUPPORTED_APP = "supported_app"  # KiotViet, MISA, Sapo...
    CUSTOM_MCP = "custom_mcp"


class SupportedAppType(str, enum.Enum):
    """Supported application types."""
    KIOTVIET = "kiotviet"
    # Future: MISA = "misa"
    # Future: SAPO = "sapo"


class MCPAuthType(str, enum.Enum):
    """MCP authentication types for custom MCP servers."""
    NONE = "none"
    API_KEY = "api_key"
    BEARER = "bearer"
    BASIC = "basic"


class AppConnection(BaseModel):
    """App connection configuration per workspace."""
    
    __tablename__ = "app_connections"
    
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=False, index=True)
    name = Column(String(200), nullable=False)  # User-defined name
    connection_type = Column(SQLEnum(ConnectionType), nullable=False)
    is_default = Column(Boolean, default=False, nullable=False)  # Default connection for workspace
    
    # For supported apps
    supported_app_type = Column(SQLEnum(SupportedAppType), nullable=True)
    
    # For custom MCP
    mcp_server_url = Column(String(500), nullable=True)
    mcp_auth_type = Column(SQLEnum(MCPAuthType), nullable=True, default=MCPAuthType.NONE)
    mcp_auth_config_encrypted = Column(String(1000), nullable=True)  # Encrypted JSON config
    
    # Common fields for supported apps (KiotViet, etc.)
    client_id = Column(String(200), nullable=True)
    client_secret_encrypted = Column(String(500), nullable=True)
    retailer = Column(String(200), nullable=True)  # KiotViet retailer name
    
    # Metadata
    config_json = Column(JSON, nullable=True)  # Flexible JSON config for app-specific settings
    status = Column(SQLEnum(ConnectionStatus), nullable=False, default=ConnectionStatus.INACTIVE)
    
    # Relationships
    workspace = relationship("Workspace", backref="app_connections")
    
    def __repr__(self):
        return f"<AppConnection(id={self.id}, workspace_id={self.workspace_id}, type={self.connection_type}, name={self.name})>"

