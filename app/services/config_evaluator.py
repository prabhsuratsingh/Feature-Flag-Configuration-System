from sqlalchemy.orm import Session
import json


from app.models.configuration import Configuration
from app.core.cache import get_cache, set_cache

def evaluate_configs(
    db: Session,
    environment: str,
) -> dict:
    """
    Returns all configs for an environment.
    """

    cache_key = f"configs:{environment}"
    cached = get_cache(cache_key)

    if cached:
        return json.loads(cached)

    configs = (
        db.query(Configuration)
        .filter(Configuration.environment == environment)
        .all()
    )

    result = {c.key: c.value for c in configs}

    set_cache(cache_key, result, ttl=60)
    return result
