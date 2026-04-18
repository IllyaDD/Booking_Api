import redis.asyncio as aioredis
from common.settings import Settings

redis_client: aioredis.Redis | None = None


async def get_redis() -> aioredis.Redis:
    return redis_client


async def init_redis():
    global redis_client
    redis_client = aioredis.from_url(
        Settings().redis.get_url(),
        encoding="utf-8",
        decode_responses=True,
    )


async def close_redis():
    if redis_client:
        await redis_client.aclose()
