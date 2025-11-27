"""App adapters domain layer."""
from app.domain.apps.kiotviet.adapter import KiotVietAdapter
from app.domain.apps.unknown.adapter import UnknownAppAdapter
from app.domain.apps.registry import register_adapter

# Register all adapters on module import
register_adapter("kiotviet", KiotVietAdapter())
register_adapter("unknown", UnknownAppAdapter())
