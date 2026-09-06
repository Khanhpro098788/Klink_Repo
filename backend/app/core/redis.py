import time
import logging
import redis.asyncio as aioredis
from app.config import settings

logger = logging.getLogger(__name__)

# Initialize connection pool for Redis
redis_pool = aioredis.ConnectionPool(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    password=settings.REDIS_PASSWORD or None,
    decode_responses=True,
    max_connections=50  # limits connections to prevent resource exhaustion
)
redis_client = aioredis.Redis(connection_pool=redis_pool)

# Fail-safe local in-memory fallback cache
memory_cache = {}
MAX_CACHE_SIZE = 10000

async def is_rate_limited(key: str, limit: int, period_seconds: int) -> bool:
    """
    Checks if a key has exceeded a rate limit.
    Performs atomic increments in Redis, falling back to local memory if Redis is down.
    """
    try:
        async with redis_client.pipeline(transaction=True) as pipe:
            pipe.incr(key)
            pipe.expire(key, period_seconds)
            results = await pipe.execute()
            count = results[0]
            if count > limit:
                return True
            return False
    except Exception as e:
        logger.warning(f"Redis rate limiter failed: {e}. Falling back to in-memory rate limiting.")
        
        # In-memory fallback logic
        now = time.time()
        
        # Clean expired keys from memory cache to release memory
        expired_keys = [k for k, v in memory_cache.items() if v["expires_at"] < now]
        for k in expired_keys:
            memory_cache.pop(k, None)
            
        # Hard limit to prevent memory exhaustion
        if len(memory_cache) >= MAX_CACHE_SIZE:
            logger.warning("Memory cache limit reached. Aggressive eviction triggered.")
            # Keep only the newest 50% of elements (simplistic eviction)
            sorted_items = sorted(memory_cache.items(), key=lambda item: item[1]["expires_at"], reverse=True)
            memory_cache.clear()
            memory_cache.update(dict(sorted_items[:MAX_CACHE_SIZE // 2]))
            
        if key not in memory_cache:
            memory_cache[key] = {"count": 1, "expires_at": now + period_seconds}
            return False
        else:
            data = memory_cache[key]
            data["count"] += 1
            if data["count"] > limit:
                return True
            return False
