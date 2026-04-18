import json
import functools
from db import get_redis

_PRIMITIVE_TYPES = (str, int, float, bool, type(None))


def cache(expire: int = 60):
    """expire — секунди"""

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            redis = await get_redis()

            # Будуємо ключ лише з примітивних kwargs (виключаємо DB-сесії та залежності)
            primitive_kwargs = {
                k: v for k, v in kwargs.items() if isinstance(v, _PRIMITIVE_TYPES)
            }
            cache_key = f"{func.__name__}:{json.dumps(primitive_kwargs, sort_keys=True, default=str)}"

            cached = await redis.get(cache_key)
            if cached:
                return json.loads(cached)

            result = await func(*args, **kwargs)
            await redis.setex(cache_key, expire, json.dumps(result, default=str))
            return result

        return wrapper

    return decorator
