"""Connected app service for business logic."""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.connected_app import ConnectedApp
from app.models.workspace import Workspace
from app.repositories.connected_app_repo import ConnectedAppRepository
from app.repositories.workspace_repo import WorkspaceRepository
from app.domain.apps.base import ConnectedAppConfig, AppCategory, ConnectionMethod
from app.domain.apps.registry import get_adapter
from app.utils.crypto import encrypt, decrypt
from app.core.logging import get_logger

logger = get_logger(__name__)


class ConnectedAppService:
    """Service for managing connected apps."""
    
    @staticmethod
    def get_supported_apps() -> List[Dict[str, Any]]:
        """Get list of all supported apps."""
        # Hardcoded for now - can be moved to registry later
        return [
            {
                "id": "kiotviet",
                "name": "KiotViet",
                "category": "POS_SIMPLE",
                "connection_method": "api",
                "description": "Hệ thống quản lý bán hàng KiotViet",
                "requires_retailer": True,
                "auth_method": "oauth2",
                "required_fields": ["client_id", "client_secret", "retailer"],
            },
            # Future apps can be added here
        ]
    
    @staticmethod
    def create_connected_app(
        db: Session,
        workspace_id: int,
        app_id: str,
        name: str,
        app_category: AppCategory,
        connection_method: ConnectionMethod,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        retailer: Optional[str] = None,
        mcp_server_url: Optional[str] = None,
        mcp_auth_type: Optional[str] = None,
        mcp_auth_config: Optional[dict] = None,
        config_json: Optional[dict] = None,
        is_default: bool = False,
    ) -> ConnectedApp:
        """
        Create a new connected app.
        
        Args:
            db: Database session
            workspace_id: Workspace ID
            app_id: App identifier (e.g., "kiotviet")
            name: User-defined name
            app_category: App category (POS_SIMPLE, ACCOUNTING, UNKNOWN)
            connection_method: Connection method (API, MCP)
            client_id: OAuth client ID (for API connections)
            client_secret: OAuth client secret (will be encrypted)
            retailer: Retailer name (for KiotViet)
            mcp_server_url: MCP server URL (for MCP connections)
            mcp_auth_type: MCP auth type
            mcp_auth_config: MCP auth config (will be encrypted)
            config_json: Additional config
            is_default: Set as default connection
            
        Returns:
            Created ConnectedApp instance
        """
        # Verify workspace exists
        workspace = WorkspaceRepository.get_by_id(db, workspace_id)
        if not workspace:
            raise ValueError(f"Workspace {workspace_id} not found")
        
        # Validate required fields based on connection method
        if connection_method == ConnectionMethod.API:
            if not client_id or not client_secret:
                raise ValueError("API connections require client_id and client_secret")
            # Encrypt client secret
            client_secret_encrypted = encrypt(client_secret)
        else:
            client_secret_encrypted = None
        
        if connection_method == ConnectionMethod.MCP:
            if not mcp_server_url:
                raise ValueError("MCP connections require mcp_server_url")
            # Encrypt MCP auth config if provided
            mcp_auth_config_encrypted = None
            if mcp_auth_config:
                import json
                mcp_auth_config_encrypted = encrypt(json.dumps(mcp_auth_config))
        else:
            mcp_auth_config_encrypted = None
        
        # Create connection
        connected_app = ConnectedAppRepository.create(
            db=db,
            workspace_id=workspace_id,
            name=name,
            app_id=app_id,
            app_category=app_category,
            connection_method=connection_method,
            client_id=client_id,
            client_secret_encrypted=client_secret_encrypted,
            retailer=retailer,
            mcp_server_url=mcp_server_url,
            mcp_auth_type=mcp_auth_type,
            mcp_auth_config_encrypted=mcp_auth_config_encrypted,
            config_json=config_json,
            is_default=is_default,
        )
        
        logger.info(f"Created connected app: {connected_app.id} ({app_id})")
        return connected_app
    
    @staticmethod
    async def test_connection(db: Session, connection_id: int) -> Dict[str, Any]:
        """
        Test connected app connection.
        
        Args:
            db: Database session
            connection_id: Connection ID to test
            
        Returns:
            Test result with status and message
        """
        connected_app = ConnectedAppRepository.get_by_id(db, connection_id)
        if not connected_app:
            raise ValueError(f"Connected app {connection_id} not found")
        
        try:
            # Build ConnectedAppConfig
            credentials = {}
            if connected_app.connection_method == ConnectionMethod.API:
                if connected_app.client_id and connected_app.client_secret_encrypted:
                    credentials["client_id"] = connected_app.client_id
                    credentials["client_secret"] = decrypt(connected_app.client_secret_encrypted)
                if connected_app.retailer:
                    credentials["retailer"] = connected_app.retailer
            
            app_config = ConnectedAppConfig(
                app_id=connected_app.app_id,
                name=connected_app.name,
                category=connected_app.app_category,
                connection_method=connected_app.connection_method,
                credentials=credentials,
                extra={},
            )
            
            # Test using adapter
            adapter = get_adapter(connected_app.app_id)
            
            # For KiotViet, test by getting branches (simple API call)
            if connected_app.app_id == "kiotviet" and connected_app.connection_method == ConnectionMethod.API:
                from app.domain.apps.base import AppReadIntent
                result = adapter.read(
                    AppReadIntent(kind="LIST_BRANCHES", params={}),
                    app_config
                )
                return {
                    "status": "success",
                    "message": "Connection successful",
                    "data": {"branches_count": len(result.get("branches", []))}
                }
            else:
                return {
                    "status": "success",
                    "message": "Connection configuration valid"
                }
        
        except Exception as e:
            logger.error(f"Connection test failed: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    @staticmethod
    def set_default_connection(
        db: Session,
        workspace_id: int,
        connection_id: int
    ) -> ConnectedApp:
        """
        Set connection as default for workspace.
        
        Args:
            db: Database session
            workspace_id: Workspace ID
            connection_id: Connection ID to set as default
            
        Returns:
            Updated ConnectedApp instance
        """
        connected_app = ConnectedAppRepository.get_by_id(db, connection_id)
        if not connected_app:
            raise ValueError(f"Connected app {connection_id} not found")
        
        if connected_app.workspace_id != workspace_id:
            raise ValueError("Connected app does not belong to workspace")
        
        # Update connection to be default (repo will unset others)
        return ConnectedAppRepository.update(
            db=db,
            connected_app=connected_app,
            is_default=True
        )

