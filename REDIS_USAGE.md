# Redis Usage trong Culi Backend

## Trạng thái hiện tại

**Redis hiện tại CHƯA được sử dụng trong code.**

Redis được setup trong `local_dev/docker-compose.yml` nhưng chỉ là **optional service** để chuẩn bị cho các tính năng trong tương lai.

## Use cases tiềm năng

### 1. OAuth Token Caching (Ưu tiên cao)

**Vấn đề hiện tại:**
- KiotViet OAuth tokens đang được cache trong **memory** (`app/integrations/kiotviet_oauth.py`)
- Cache này sẽ mất khi server restart hoặc với multiple workers

**Giải pháp với Redis:**
```python
# Thay thế in-memory cache bằng Redis
# Cấu trúc key: "kv_token:{client_id}:{client_secret}"
# TTL: 24 hours (thời gian expire của token)
```

**Lợi ích:**
- Persist across server restarts
- Shared cache giữa multiple workers/instances
- Tự động expire với TTL

### 2. Rate Limiting

**Use case:**
- Giới hạn số request API per user/workspace
- Giới hạn số chat messages per minute
- Giới hạn số MCP calls per connection

**Implementation với Redis:**
```python
# Sử dụng sliding window hoặc fixed window
# Key: "rate_limit:chat:{user_id}"
# Counter với TTL
```

### 3. API Response Caching

**Use case:**
- Cache responses từ KiotViet API (products, invoices, customers)
- Giảm số lượng API calls
- Tăng tốc độ response

**Cấu trúc:**
```python
# Key: "api_cache:kiotviet:{endpoint}:{params_hash}"
# TTL: 5-10 phút cho data tĩnh, 30 giây cho data động
```

**Lưu ý:**
- Cần invalidate cache khi có updates
- Cẩn thận với sensitive data

### 4. Session Storage

**Use case:**
- Lưu conversation state tạm thời
- Lưu plan execution state
- Temporary data không cần persist vào database

### 5. Distributed Locking

**Use case:**
- Đảm bảo plan execution không bị duplicate
- Concurrent access control

## Cách enable Redis

### 1. Start Redis service:

```bash
cd local_dev
docker-compose --profile optional up redis -d
```

### 2. Add Redis configuration:

Trong `app/core/config.py`:
```python
# Redis Configuration
redis_url: str = "redis://localhost:6379/0"
redis_enabled: bool = False  # Enable khi cần
```

### 3. Install Redis client:

```bash
pip install redis
```

### 4. Create Redis utility:

Tạo `app/core/redis_client.py`:
```python
import redis
from app.core.config import settings

redis_client = None

def get_redis():
    if settings.redis_enabled:
        if redis_client is None:
            redis_client = redis.from_url(settings.redis_url)
        return redis_client
    return None
```

### 5. Implement token caching với Redis:

Update `app/integrations/kiotviet_oauth.py`:
```python
from app.core.redis_client import get_redis

async def get_access_token(client_id: str, client_secret: str) -> str:
    redis = get_redis()
    if redis:
        cache_key = f"kv_token:{client_id}:{hash(client_secret)}"
        cached = redis.get(cache_key)
        if cached:
            return cached.decode()
    
    # ... existing token fetch logic ...
    
    if redis:
        redis.setex(cache_key, expires_in, access_token)
    
    return access_token
```

## Khi nào cần Redis?

### Không cần ngay nếu:
- ✅ Chạy single worker/instance
- ✅ Không có vấn đề về performance
- ✅ Token cache trong memory đủ dùng

### Nên dùng Redis khi:
- ❌ Multiple workers/instances
- ❌ Cần rate limiting
- ❌ Cần cache API responses
- ❌ Server restart thường xuyên (mất memory cache)
- ❌ Cần distributed locking

## Migration path

1. **Phase 1**: Implement Redis token caching (thay thế in-memory)
2. **Phase 2**: Add rate limiting
3. **Phase 3**: Add API response caching
4. **Phase 4**: Add session storage nếu cần

## Monitoring

Khi implement Redis, nên monitor:
- Memory usage
- Connection pool
- Cache hit rate
- TTL effectiveness

