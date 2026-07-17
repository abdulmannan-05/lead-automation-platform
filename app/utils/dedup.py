import redis
from app.core.config import settings

_redis_client = redis.Redis.from_url(settings.redis_url, decode_responses=True)

DEDUP_KEY_PREFIX = "lead_seen:"


def is_duplicate(domain_key: str | None) -> bool:
    """
    Checks if we've already processed a lead with this domain_key.
    Returns False (not a duplicate) if domain_key is None - we can't dedupe
    businesses without a website using this method.
    """
    if not domain_key:
        return False

    redis_key = f"{DEDUP_KEY_PREFIX}{domain_key}"
    return _redis_client.exists(redis_key) == 1


def mark_as_seen(domain_key: str | None) -> None:
    """
    Marks a domain_key as processed so future duplicate checks catch it.
    """
    if not domain_key:
        return

    redis_key = f"{DEDUP_KEY_PREFIX}{domain_key}"
    _redis_client.set(redis_key, "1")