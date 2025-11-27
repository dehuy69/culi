"""Supported apps registry."""
from app.models.app_connection import ConnectionType, SupportedAppType
from typing import Dict, Any, List


SUPPORTED_APPS: Dict[str, Dict[str, Any]] = {
    "kiotviet": {
        "id": "kiotviet",
        "name": "KiotViet",
        "type": SupportedAppType.KIOTVIET,
        "connection_type": ConnectionType.SUPPORTED_APP,
        "description": "Phần mềm quản lý bán hàng KiotViet",
        "requires_retailer": True,
        "auth_method": "oauth2",
        "token_url": "https://id.kiotviet.vn/connect/token",
        "api_base_url": "https://public.kiotapi.com",
        "client_class": "KiotVietDirectClient",
        "api_docs": "_prompts/kiotviet-apis.md",
        "required_fields": ["client_id", "client_secret", "retailer"],
        "optional_fields": [],
    },
    # Future supported apps can be added here
    # "misa": {...},
    # "sapo": {...},
}


def get_supported_app(app_id: str) -> Dict[str, Any]:
    """Get supported app configuration by ID."""
    return SUPPORTED_APPS.get(app_id)


def list_supported_apps() -> List[Dict[str, Any]]:
    """List all supported apps."""
    return list(SUPPORTED_APPS.values())


def is_supported_app(app_id: str) -> bool:
    """Check if app ID is a supported app."""
    return app_id in SUPPORTED_APPS

