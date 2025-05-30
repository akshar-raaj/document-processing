"""
Redis is being used as the primary database.
Our use case is extremely simple.
- We want an identifier for a file.
- And need to associate the extracted content from this file and map it with the identifier.

Hence, a Key-Value data store suffices.
We do not want to get into the complexity of setting up a Relational Database with and manage the schema nor deal with a Document database which has more administrative overhead.
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
    """
    `key` is the file identifier. In our case a hash created using the file path.
    """
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
    """
    `key` is the file identifier. In our case a hash created using the file path.
    `value` is the extracted text content after performing the Optical Character Recognition.
    """
    connection = get_connection()
    value = value.encode('utf-8')
    connection.set(key, value)
