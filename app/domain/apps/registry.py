"""Adapter registry for managing app adapters."""
from typing import Dict, Optional
from app.domain.apps.base import BaseAppAdapter
from app.domain.apps.unknown.adapter import UnknownAppAdapter
from app.core.logging import get_logger

logger = get_logger(__name__)

# Global registry of adapters
ADAPTER_REGISTRY: Dict[str, BaseAppAdapter] = {}

# Default fallback adapter
_default_adapter: Optional[BaseAppAdapter] = None


def register_adapter(app_id: str, adapter: BaseAppAdapter) -> None:
    """
    Register an adapter for a specific app.
    
    Args:
        app_id: Unique identifier for the app (e.g., "kiotviet")
        adapter: Adapter instance implementing BaseAppAdapter
    """
    ADAPTER_REGISTRY[app_id] = adapter
    logger.info(f"Registered adapter for app: {app_id}")


def get_adapter(app_id: str) -> BaseAppAdapter:
    """
    Get adapter for a specific app.
    Falls back to UnknownAppAdapter if not found.
    
    Args:
        app_id: Unique identifier for the app
        
    Returns:
        Adapter instance
    """
    if app_id in ADAPTER_REGISTRY:
        return ADAPTER_REGISTRY[app_id]
    
    logger.warning(f"Adapter not found for app_id: {app_id}, using UnknownAppAdapter")
    
    # Lazy initialization of default adapter
    global _default_adapter
    if _default_adapter is None:
        _default_adapter = UnknownAppAdapter()
    
    return _default_adapter


def list_registered_adapters() -> list[str]:
    """List all registered app IDs."""
    return list(ADAPTER_REGISTRY.keys())

