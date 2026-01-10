from sqlalchemy.orm import Session
import json

from app.models.feature import Feature
from app.models.feature_override import FeatureOverride
from app.core.cache import get_cache, set_cache


def evaluate_flags(
    db: Session,
    environment: str,
) -> dict[str, bool]:
    """
    Returns all feature flags for an environment.
    Cache-first, DB-backed.
    """

    cache_key = f"flags:{environment}"
    cached = get_cache(cache_key)

    if cached:
        return json.loads(cached)

    # Fetch all features
    features = db.query(Feature).all()

    # Fetch overrides for env
    overrides = (
        db.query(FeatureOverride)
        .filter(FeatureOverride.environment == environment)
        .all()
    )

    override_map = {
        o.feature_id: o.enabled for o in overrides
    }

    result = {}

    for feature in features:
        if feature.id in override_map:
            result[feature.key] = override_map[feature.id]
        else:
            result[feature.key] = feature.default_enabled

    set_cache(cache_key, result, ttl=60)
    return result
