import time

# simple in-memory cache
_cache = {}

# seconds (e.g., 10 minutes)
DEFAULT_TTL = 600


def get_cache(key: str):
    data = _cache.get(key)

    if not data:
        return None

    value, expiry = data

    if time.time() > expiry:
        # expired → remove
        del _cache[key]
        return None

    return value


def set_cache(key: str, value, ttl: int = DEFAULT_TTL):
    expiry = time.time() + ttl
    _cache[key] = (value, expiry)