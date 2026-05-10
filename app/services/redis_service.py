import redis.asyncio as aioredis

from app.core.config import settings

redis_client = aioredis.from_url(settings.redis_url, decode_responses=True)


async def blacklist_token(token: str, expires_in_seconds: int):
    await redis_client.setex(f"blacklist:{token}", expires_in_seconds, "1")


async def is_token_blacklisted(token: str) -> bool:
    result = await redis_client.get(f"blacklist:{token}")
    return result is not None
