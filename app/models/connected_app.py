"""Connected app model for workspace app integrations."""
from sqlalchemy import Column, String, Integer, ForeignKey, Enum as SQLEnum, JSON, Boolean
from sqlalchemy.orm import relationship
import enum
from typing import Optional, TYPE_CHECKING
from app.db.base import BaseModel

# Avoid circular import by using TYPE_CHECKING
if TYPE_CHECKING:
    from app.domain.apps.base import AppCategory, ConnectionMethod
else:
    # Runtime import
    from app.domain.apps.base import AppCategory, ConnectionMethod


class ConnectionStatus(str, enum.Enum):
    """Connection status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"


class ConnectedApp(BaseModel):
    """Connected app configuration per workspace."""
    
    __tablename__ = "connected_apps"
    
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=False, index=True)
    name = Column(String(200), nullable=False)  # User-defined name
    app_id = Column(String(50), nullable=False)  # "kiotviet", "misa_eshop", ...
    app_category = Column(SQLEnum(AppCategory), nullable=False)  # POS_SIMPLE, ACCOUNTING, UNKNOWN
    connection_method = Column(SQLEnum(ConnectionMethod), nullable=False)  # api, mcp
    is_default = Column(Boolean, default=False, nullable=False)  # Default connection for workspace
    
    # For API connections (KiotViet, etc.)
    client_id = Column(String(200), nullable=True)
    client_secret_encrypted = Column(String(500), nullable=True)
    retailer = Column(String(200), nullable=True)  # KiotViet retailer name
    
    # For MCP connections (custom apps)
    mcp_server_url = Column(String(500), nullable=True)
    mcp_auth_type = Column(String(50), nullable=True)  # "none", "api_key", "bearer", "basic"
    mcp_auth_config_encrypted = Column(String(1000), nullable=True)  # Encrypted JSON config
    
    # Metadata
    config_json = Column(JSON, nullable=True)  # Flexible JSON config for app-specific settings
    status = Column(SQLEnum(ConnectionStatus), nullable=False, default=ConnectionStatus.INACTIVE)
    
    # Relationships
    workspace = relationship("Workspace", backref="connected_apps")
    
    def __repr__(self):
        return f"<ConnectedApp(id={self.id}, workspace_id={self.workspace_id}, app_id={self.app_id}, name={self.name})>"

