import redis
import json
import hashlib
import os
from dotenv import load_dotenv

load_dotenv()

# Upstash Redis connection with TLS
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    password=os.getenv("REDIS_PASSWORD"),
    ssl=True,
    decode_responses=True,
    socket_connect_timeout=5,
)


def get_cached_query(query):
    try:
        cache_key = f"query:{hashlib.md5(query.encode()).hexdigest()}"
        cached = redis_client.get(cache_key)
        if cached:
            return json.loads(cached)
        return None
    except Exception as e:
        print(f"Redis get error: {e}")
        return None


def cache_query_result(query, result, ttl=3600):
    try:
        cache_key = f"query:{hashlib.md5(query.encode()).hexdigest()}"
        redis_client.setex(cache_key, ttl, json.dumps(result))
        return True
    except Exception as e:
        print(f"Redis set error: {e}")
        return False
