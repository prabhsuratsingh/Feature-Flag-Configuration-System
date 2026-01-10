from app.core.cache import delete_cache


def invalidate_flag_cache(environment: str):
    delete_cache(f"flags:{environment}")


def invalidate_config_cache(environment: str):
    delete_cache(f"configs:{environment}")
