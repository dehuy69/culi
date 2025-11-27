"""App connection repository for database operations."""
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.app_connection import (
    AppConnection,
    ConnectionType,
    SupportedAppType,
    ConnectionStatus,
)


class AppConnectionRepository:
    """Repository for AppConnection model operations."""
    
    @staticmethod
    def get_by_id(db: Session, connection_id: int) -> Optional[AppConnection]:
        """Get app connection by ID."""
        return db.query(AppConnection).filter(AppConnection.id == connection_id).first()
    
    @staticmethod
    def get_by_workspace(
        db: Session,
        workspace_id: int,
        connection_type: Optional[ConnectionType] = None
    ) -> List[AppConnection]:
        """Get all app connections for workspace."""
        query = db.query(AppConnection).filter(AppConnection.workspace_id == workspace_id)
        
        if connection_type:
            query = query.filter(AppConnection.connection_type == connection_type)
        
        return query.order_by(AppConnection.created_at.desc()).all()
    
    @staticmethod
    def get_default(db: Session, workspace_id: int) -> Optional[AppConnection]:
        """Get default connection for workspace."""
        return db.query(AppConnection).filter(
            AppConnection.workspace_id == workspace_id,
            AppConnection.is_default == True
        ).first()
    
    @staticmethod
    def create(
        db: Session,
        workspace_id: int,
        name: str,
        connection_type: ConnectionType,
        supported_app_type: Optional[SupportedAppType] = None,
        mcp_server_url: Optional[str] = None,
        mcp_auth_type: Optional[str] = None,
        mcp_auth_config_encrypted: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret_encrypted: Optional[str] = None,
        retailer: Optional[str] = None,
        config_json: Optional[dict] = None,
        is_default: bool = False,
    ) -> AppConnection:
        """Create a new app connection."""
        # If this is set as default, unset other defaults
        if is_default:
            AppConnectionRepository.unset_defaults(db, workspace_id)
        
        connection = AppConnection(
            workspace_id=workspace_id,
            name=name,
            connection_type=connection_type,
            supported_app_type=supported_app_type,
            mcp_server_url=mcp_server_url,
            mcp_auth_type=mcp_auth_type,
            mcp_auth_config_encrypted=mcp_auth_config_encrypted,
            client_id=client_id,
            client_secret_encrypted=client_secret_encrypted,
            retailer=retailer,
            config_json=config_json,
            is_default=is_default,
            status=ConnectionStatus.INACTIVE,
        )
        db.add(connection)
        db.commit()
        db.refresh(connection)
        return connection
    
    @staticmethod
    def update(
        db: Session,
        connection: AppConnection,
        name: Optional[str] = None,
        status: Optional[ConnectionStatus] = None,
        client_id: Optional[str] = None,
        client_secret_encrypted: Optional[str] = None,
        retailer: Optional[str] = None,
        mcp_server_url: Optional[str] = None,
        mcp_auth_config_encrypted: Optional[str] = None,
        config_json: Optional[dict] = None,
        is_default: Optional[bool] = None,
    ) -> AppConnection:
        """Update app connection."""
        if name is not None:
            connection.name = name
        if status is not None:
            connection.status = status
        if client_id is not None:
            connection.client_id = client_id
        if client_secret_encrypted is not None:
            connection.client_secret_encrypted = client_secret_encrypted
        if retailer is not None:
            connection.retailer = retailer
        if mcp_server_url is not None:
            connection.mcp_server_url = mcp_server_url
        if mcp_auth_config_encrypted is not None:
            connection.mcp_auth_config_encrypted = mcp_auth_config_encrypted
        if config_json is not None:
            connection.config_json = config_json
        if is_default is not None and is_default:
            # Unset other defaults if setting this as default
            AppConnectionRepository.unset_defaults(db, connection.workspace_id)
            connection.is_default = True
        elif is_default is not None and not is_default:
            connection.is_default = False
        
        db.commit()
        db.refresh(connection)
        return connection
    
    @staticmethod
    def delete(db: Session, connection: AppConnection) -> None:
        """Delete app connection."""
        db.delete(connection)
        db.commit()
    
    @staticmethod
    def unset_defaults(db: Session, workspace_id: int) -> None:
        """Unset all default flags for workspace connections."""
        db.query(AppConnection).filter(
            AppConnection.workspace_id == workspace_id,
            AppConnection.is_default == True
        ).update({"is_default": False})
        db.commit()

