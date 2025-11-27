"""Schemas for connected app API."""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from app.domain.apps.base import AppCategory, ConnectionMethod


class ConnectedAppCreate(BaseModel):
    """Request to create connected app."""
    app_id: str = Field(..., description="App identifier (e.g., 'kiotviet')")
    name: str = Field(..., description="User-defined name for the connection")
    app_category: AppCategory = Field(..., description="App category")
    connection_method: ConnectionMethod = Field(..., description="Connection method")
    
    # For API connections
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    retailer: Optional[str] = None
    
    # For MCP connections
    mcp_server_url: Optional[str] = None
    mcp_auth_type: Optional[str] = None
    mcp_auth_config: Optional[Dict[str, Any]] = None
    
    # Optional
    config_json: Optional[Dict[str, Any]] = None
    is_default: bool = False


class ConnectedAppUpdate(BaseModel):
    """Request to update connected app."""
    name: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    retailer: Optional[str] = None
    mcp_server_url: Optional[str] = None
    mcp_auth_config: Optional[Dict[str, Any]] = None
    config_json: Optional[Dict[str, Any]] = None
    status: Optional[str] = None


class ConnectedAppResponse(BaseModel):
    """Connected app response."""
    id: int
    workspace_id: int
    name: str
    app_id: str
    app_category: str
    connection_method: str
    retailer: Optional[str] = None
    status: str
    is_default: bool
    
    class Config:
        from_attributes = True


class SupportedAppResponse(BaseModel):
    """Supported app information."""
    id: str
    name: str
    category: str
    connection_method: str
    description: str
    requires_retailer: bool
    auth_method: str
    required_fields: list[str]


class TestConnectionResponse(BaseModel):
    """Connection test result."""
    status: str
    message: str
    data: Optional[Dict[str, Any]] = None

