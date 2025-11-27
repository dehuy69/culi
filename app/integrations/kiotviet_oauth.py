"""KiotViet OAuth2 token management."""
import httpx
from typing import Optional
from app.core.config import settings
from app.core.logging import get_logger
import time

logger = get_logger(__name__)


class TokenCache:
    """Simple in-memory token cache with expiration."""
    
    def __init__(self):
        self._cache: dict[str, tuple[str, float]] = {}  # {key: (token, expires_at)}
    
    def get(self, key: str) -> Optional[str]:
        """Get cached token if still valid."""
        if key in self._cache:
            token, expires_at = self._cache[key]
            if time.time() < expires_at:
                return token
            else:
                del self._cache[key]
        return None
    
    def set(self, key: str, token: str, expires_in: int):
        """Cache token with expiration."""
        expires_at = time.time() + expires_in - 60  # Subtract 60s for safety
        self._cache[key] = (token, expires_at)
    
    def clear(self, key: str):
        """Clear cached token."""
        if key in self._cache:
            del self._cache[key]


_token_cache = TokenCache()


async def get_access_token(client_id: str, client_secret: str) -> str:
    """
    Get KiotViet OAuth2 access token.
    
    Args:
        client_id: KiotViet client ID
        client_secret: KiotViet client secret
        
    Returns:
        Access token string
        
    Raises:
        Exception: If token request fails
    """
    # Check cache
    cache_key = f"{client_id}:{client_secret}"
    cached_token = _token_cache.get(cache_key)
    if cached_token:
        return cached_token
    
    # Request new token
    data = {
        "scopes": "PublicApi.Access",
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.kiotviet_token_url,
                data=data,
                headers=headers,
                timeout=30.0
            )
            response.raise_for_status()
            token_data = response.json()
            
            access_token = token_data["access_token"]
            expires_in = token_data.get("expires_in", 3600)
            
            # Cache token
            _token_cache.set(cache_key, access_token, expires_in)
            
            logger.info("KiotViet access token obtained successfully")
            return access_token
            
    except httpx.HTTPStatusError as e:
        logger.error(f"KiotViet token request failed: {e.response.status_code} - {e.response.text}")
        raise Exception(f"Failed to get KiotViet access token: {e.response.status_code}")
    except Exception as e:
        logger.error(f"KiotViet token request error: {str(e)}")
        raise


def clear_token_cache(client_id: str, client_secret: str):
    """Clear cached token for given credentials."""
    cache_key = f"{client_id}:{client_secret}"
    _token_cache.clear(cache_key)

