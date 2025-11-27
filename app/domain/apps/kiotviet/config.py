"""KiotViet configuration model."""
from typing import Optional
from pydantic import BaseModel
from app.domain.apps.base import ConnectedAppConfig


class KiotVietConfig(BaseModel):
    """KiotViet-specific configuration."""
    base_url: str = "https://public.kiotapi.com"
    token_url: str = "https://id.kiotviet.vn/connect/token"
    client_id: str
    client_secret: str
    retailer: str  # Shop/retailer name (tên gian hàng)
    
    @classmethod
    def from_connected_app_config(cls, config: ConnectedAppConfig) -> "KiotVietConfig":
        """
        Create KiotVietConfig from ConnectedAppConfig.
        
        Args:
            config: ConnectedAppConfig instance
            
        Returns:
            KiotVietConfig instance
            
        Raises:
            ValueError: If required credentials are missing
        """
        credentials = config.credentials
        if not credentials.get("client_id"):
            raise ValueError("KiotViet requires client_id in credentials")
        if not credentials.get("client_secret"):
            raise ValueError("KiotViet requires client_secret in credentials")
        if not credentials.get("retailer"):
            raise ValueError("KiotViet requires retailer in credentials")
        
        return cls(
            base_url=credentials.get("base_url", "https://public.kiotapi.com"),
            token_url=credentials.get("token_url", "https://id.kiotviet.vn/connect/token"),
            client_id=credentials["client_id"],
            client_secret=credentials["client_secret"],
            retailer=credentials["retailer"],
        )

