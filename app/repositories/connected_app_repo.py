"""Connected app repository for database operations."""
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.connected_app import ConnectedApp, ConnectionStatus
from app.domain.apps.base import AppCategory, ConnectionMethod


class ConnectedAppRepository:
    """Repository for ConnectedApp model operations."""
    
    @staticmethod
    def get_by_id(db: Session, connection_id: int) -> Optional[ConnectedApp]:
        """Get connected app by ID."""
        return db.query(ConnectedApp).filter(ConnectedApp.id == connection_id).first()
    
    @staticmethod
    def get_by_workspace(
        db: Session,
        workspace_id: int,
        app_category: Optional[AppCategory] = None,
        connection_method: Optional[ConnectionMethod] = None
    ) -> List[ConnectedApp]:
        """Get all connected apps for workspace."""
        query = db.query(ConnectedApp).filter(ConnectedApp.workspace_id == workspace_id)
        
        if app_category:
            query = query.filter(ConnectedApp.app_category == app_category)
        
        if connection_method:
            query = query.filter(ConnectedApp.connection_method == connection_method)
        
        return query.order_by(ConnectedApp.created_at.desc()).all()
    
    @staticmethod
    def get_default(db: Session, workspace_id: int) -> Optional[ConnectedApp]:
        """Get default connected app for workspace."""
        return db.query(ConnectedApp).filter(
            ConnectedApp.workspace_id == workspace_id,
            ConnectedApp.is_default == True
        ).first()
    
    @staticmethod
    def get_by_app_id(
        db: Session,
        workspace_id: int,
        app_id: str
    ) -> Optional[ConnectedApp]:
        """Get connected app by app_id."""
        return db.query(ConnectedApp).filter(
            ConnectedApp.workspace_id == workspace_id,
            ConnectedApp.app_id == app_id
        ).first()
    
    @staticmethod
    def create(
        db: Session,
        workspace_id: int,
        name: str,
        app_id: str,
        app_category: AppCategory,
        connection_method: ConnectionMethod,
        client_id: Optional[str] = None,
        client_secret_encrypted: Optional[str] = None,
        retailer: Optional[str] = None,
        mcp_server_url: Optional[str] = None,
        mcp_auth_type: Optional[str] = None,
        mcp_auth_config_encrypted: Optional[str] = None,
        config_json: Optional[dict] = None,
        is_default: bool = False,
    ) -> ConnectedApp:
        """Create a new connected app."""
        # If this is set as default, unset other defaults
        if is_default:
            ConnectedAppRepository.unset_defaults(db, workspace_id)
        
        connected_app = ConnectedApp(
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
            status=ConnectionStatus.INACTIVE,
        )
        db.add(connected_app)
        db.commit()
        db.refresh(connected_app)
        return connected_app
    
    @staticmethod
    def update(
        db: Session,
        connected_app: ConnectedApp,
        name: Optional[str] = None,
        status: Optional[ConnectionStatus] = None,
        client_id: Optional[str] = None,
        client_secret_encrypted: Optional[str] = None,
        retailer: Optional[str] = None,
        mcp_server_url: Optional[str] = None,
        mcp_auth_config_encrypted: Optional[str] = None,
        config_json: Optional[dict] = None,
        is_default: Optional[bool] = None,
    ) -> ConnectedApp:
        """Update connected app."""
        if name is not None:
            connected_app.name = name
        if status is not None:
            connected_app.status = status
        if client_id is not None:
            connected_app.client_id = client_id
        if client_secret_encrypted is not None:
            connected_app.client_secret_encrypted = client_secret_encrypted
        if retailer is not None:
            connected_app.retailer = retailer
        if mcp_server_url is not None:
            connected_app.mcp_server_url = mcp_server_url
        if mcp_auth_config_encrypted is not None:
            connected_app.mcp_auth_config_encrypted = mcp_auth_config_encrypted
        if config_json is not None:
            connected_app.config_json = config_json
        if is_default is not None and is_default:
            # Unset other defaults if setting this as default
            ConnectedAppRepository.unset_defaults(db, connected_app.workspace_id)
            connected_app.is_default = True
        elif is_default is not None and not is_default:
            connected_app.is_default = False
        
        db.commit()
        db.refresh(connected_app)
        return connected_app
    
    @staticmethod
    def delete(db: Session, connected_app: ConnectedApp) -> None:
        """Delete connected app."""
        db.delete(connected_app)
        db.commit()
    
    @staticmethod
    def unset_defaults(db: Session, workspace_id: int) -> None:
        """Unset all default flags for workspace connections."""
        db.query(ConnectedApp).filter(
            ConnectedApp.workspace_id == workspace_id,
            ConnectedApp.is_default == True
        ).update({"is_default": False})
        db.commit()

