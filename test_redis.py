# test_redis.py

import redis

try:
    r = redis.Redis(host='localhost', port=6379, db=0)
    response = r.ping()
    print(f"Redis connection successful: {response}")
except redis.exceptions.ConnectionError as e:
    print(f"Redis connection failed: {e}")
