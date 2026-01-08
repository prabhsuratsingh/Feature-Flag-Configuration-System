import json
import redis

redis_client = redis.Redis(host='redis', port=6379, db=0)

FLAG_CACHE_TTL = 60
CONFIG_CACHE_TTL = 60


def get_cache(key: str):
    return redis_client.get(key)


def set_cache(key: str, value: dict, ttl: int):
    redis_client.setex(key, ttl, json.dumps(value))


def delete_cache(key: str):
    redis_client.delete(key)
