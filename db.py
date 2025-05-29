"""
Redis is being used as the primary database.
Our use case is extremely simple. We are dealing with a single entity, i.e a FilePath, and store the extracted text content.
Hence, a Key-Value data store suffices.
We do not want to get into the complexity of setting up a Relational Database or a Document database which has more administrative overhead.
"""
import os
import redis


# We want to reuse the Redis connection across the application lifecycle,
# and shouldn't create a connection for every request.
# Global variable, pollutes the namespace.
# Okay, for a side project
# We could refactor it to use a Singleton pattern.
redis_connection = None


def get_connection():
    global redis_connection
    if redis_connection is None:
        REDIS_CONNECTION_STRING = os.environ['REDIS_CONNECTION_STRING']
        redis_connection = redis.Redis(host=REDIS_CONNECTION_STRING)
    return redis_connection


def get_value(key: str) -> str:
    connection = get_connection()
    value = connection.get(key)
    if value is None:
        return value
    # Redis stores bytes.
    # Application encodes the strings to utf-8 before putting in Redis.
    # Hence decode to utf-8 on read.
    value = value.decode('utf-8')
    return value


def set_value(key: str, value: str):
    connection = get_connection()
    value = value.encode('utf-8')
    connection.set(key, value)