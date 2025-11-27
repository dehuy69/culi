"""App connection service for business logic."""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.app_connection import (
    AppConnection,
    ConnectionType,
    SupportedAppType,
    ConnectionStatus,
)
from app.models.workspace import Workspace
from app.repositories.app_connection_repo import AppConnectionRepository
from app.repositories.workspace_repo import WorkspaceRepository
from app.integrations.supported_apps import get_supported_app, list_supported_apps
from app.integrations.connection_factory import create_app_client
from app.utils.crypto import encrypt, decrypt
from app.core.logging import get_logger

logger = get_logger(__name__)


class AppConnectionService:
    """Service for managing app connections."""
    
    @staticmethod
    def get_supported_apps() -> List[Dict[str, Any]]:
        """Get list of all supported apps."""
        apps = list_supported_apps()
        # Format for API response
        return [
            {
                "id": app["id"],
                "name": app["name"],
                "description": app.get("description", ""),
                "requires_retailer": app.get("requires_retailer", False),
                "auth_method": app.get("auth_method", ""),
                "required_fields": app.get("required_fields", []),
            }
            for app in apps
        ]
    
    @staticmethod
    def create_supported_app_connection(
        db: Session,
        workspace_id: int,
        app_type: str,
        name: str,
        client_id: str,
        client_secret: str,
        retailer: Optional[str] = None,
        config_json: Optional[dict] = None,
        is_default: bool = False,
    ) -> AppConnection:
        """
        Create connection for supported app.
        
        Args:
            db: Database session
            workspace_id: Workspace ID
            app_type: Supported app type (e.g., "kiotviet")
            name: User-defined name for connection
            client_id: OAuth client ID
            client_secret: OAuth client secret (will be encrypted)
            retailer: Retailer name (required for KiotViet)
            config_json: Additional config
            is_default: Set as default connection
            
        Returns:
            Created AppConnection instance
        """
        # Verify workspace exists
        workspace = WorkspaceRepository.get_by_id(db, workspace_id)
        if not workspace:
            raise ValueError(f"Workspace {workspace_id} not found")
        
        # Verify app type is supported
        app_config = get_supported_app(app_type)
        if not app_config:
            raise ValueError(f"Unsupported app type: {app_type}")
        
        # Validate required fields
        if app_config.get("requires_retailer") and not retailer:
            raise ValueError(f"{app_config['name']} requires retailer name")
        
        # Encrypt client secret
        encrypted_secret = encrypt(client_secret)
        
        # Create connection
        connection = AppConnectionRepository.create(
            db=db,
            workspace_id=workspace_id,
            name=name,
            connection_type=ConnectionType.SUPPORTED_APP,
            supported_app_type=SupportedAppType[app_type.upper()],
            client_id=client_id,
            client_secret_encrypted=encrypted_secret,
            retailer=retailer,
            config_json=config_json,
            is_default=is_default,
        )
        
        logger.info(f"Created supported app connection: {connection.id} ({app_type})")
        return connection
    
    @staticmethod
    def create_custom_mcp_connection(
        db: Session,
        workspace_id: int,
        name: str,
        mcp_server_url: str,
        auth_type: str = "none",
        auth_config: Optional[dict] = None,
        config_json: Optional[dict] = None,
        is_default: bool = False,
    ) -> AppConnection:
        """
        Create connection for custom MCP server.
        
        Args:
            db: Database session
            workspace_id: Workspace ID
            name: User-defined name for connection
            mcp_server_url: MCP server URL
            auth_type: Authentication type ("none", "api_key", "bearer", "basic")
            auth_config: Authentication configuration (will be encrypted)
            config_json: Additional config
            is_default: Set as default connection
            
        Returns:
            Created AppConnection instance
        """
        # Verify workspace exists
        workspace = WorkspaceRepository.get_by_id(db, workspace_id)
        if not workspace:
            raise ValueError(f"Workspace {workspace_id} not found")
        
        # Encrypt auth config if provided
        encrypted_auth_config = None
        if auth_config:
            import json
            encrypted_auth_config = encrypt(json.dumps(auth_config))
        
        # Create connection
        connection = AppConnectionRepository.create(
            db=db,
            workspace_id=workspace_id,
            name=name,
            connection_type=ConnectionType.CUSTOM_MCP,
            mcp_server_url=mcp_server_url,
            mcp_auth_type=auth_type,
            mcp_auth_config_encrypted=encrypted_auth_config,
            config_json=config_json,
            is_default=is_default,
        )
        
        logger.info(f"Created custom MCP connection: {connection.id}")
        return connection
    
    @staticmethod
    async def test_connection(db: Session, connection_id: int) -> Dict[str, Any]:
        """
        Test app connection.
        
        Args:
            db: Database session
            connection_id: Connection ID to test
            
        Returns:
            Test result with status and message
        """
        connection = AppConnectionRepository.get_by_id(db, connection_id)
        if not connection:
            raise ValueError(f"Connection {connection_id} not found")
        
        try:
            # Create client
            client = create_app_client(connection)
            
            # Test connection based on type
            if connection.connection_type == ConnectionType.SUPPORTED_APP:
                if connection.supported_app_type == SupportedAppType.KIOTVIET:
                    # Test by getting branches (simple API call)
                    result = await client.get_branches()
                    return {
                        "status": "success",
                        "message": "Connection successful",
                        "data": {"branches_count": len(result.get("data", []))}
                    }
            
            elif connection.connection_type == ConnectionType.CUSTOM_MCP:
                # TODO: Test MCP connection in Phase 3
                return {
                    "status": "error",
                    "message": "Custom MCP testing not yet implemented"
                }
            
            return {
                "status": "error",
                "message": "Unknown connection type"
            }
            
        except Exception as e:
            logger.error(f"Connection test failed: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    @staticmethod
    def get_connection_client(connection: AppConnection) -> Any:
        """
        Get client instance for connection.
        
        Args:
            connection: AppConnection instance
            
        Returns:
            Client instance
        """
        return create_app_client(connection)
    
    @staticmethod
    def set_default_connection(
        db: Session,
        workspace_id: int,
        connection_id: int
    ) -> AppConnection:
        """
        Set connection as default for workspace.
        
        Args:
            db: Database session
            workspace_id: Workspace ID
            connection_id: Connection ID to set as default
            
        Returns:
            Updated AppConnection instance
        """
        connection = AppConnectionRepository.get_by_id(db, connection_id)
        if not connection:
            raise ValueError(f"Connection {connection_id} not found")
        
        if connection.workspace_id != workspace_id:
            raise ValueError("Connection does not belong to workspace")
        
        # Update connection to be default (repo will unset others)
        return AppConnectionRepository.update(
            db=db,
            connection=connection,
            is_default=True
        )

