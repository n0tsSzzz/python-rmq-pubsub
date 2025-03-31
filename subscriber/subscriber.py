import asyncio
import hashlib
import os

import orjson
from aio_pika import ExchangeType, connect_robust
from aioredlock import Aioredlock, LockError
from cassandra.cluster import Cluster
from msgpack import unpackb
from redis.asyncio import Redis

EXCHANGE_NAME = "pub/sub"

async def save_to_db(session, result: str):
    print(f"SAVING TO DB: {result}")
    query = f"INSERT INTO {os.getenv('MESSAGE_TABLE')} (id, content) VALUES (now(), %s)"
    future = session.execute_async(query, (result,))
    await asyncio.get_event_loop().run_in_executor(None, lambda: future.result())

async def consume():
    print("Starting consumer")

    cluster = Cluster(['cassandra'])
    session = cluster.connect('pubsub')
    print("Connected to cassandra")

    redis = await Redis.from_url(f"redis://{os.getenv('REDIS_HOST')}", encoding="utf-8", decode_responses=True)
    lock_manager = Aioredlock([{"host": "redis"}])
    print("Connected to redis")

    con = f"amqp://{os.getenv('RABBITMQ_USER')}:{os.getenv('RABBITMQ_PASSWORD')}@{os.getenv('RABBITMQ_HOST')}:{os.getenv('RABBITMQ_PORT')}/"
    connection = await connect_robust(con)
    print("Connected to RabbitMQ")

    async with connection:
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=1)

        exchange = await channel.declare_exchange(
            EXCHANGE_NAME, ExchangeType.FANOUT,
        )

        queue = await channel.declare_queue(exclusive=True)
        await queue.bind(exchange)

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    try:
                        content = message.body
                        content_hash = hashlib.sha256(content).hexdigest()
                        cache_key = f"msg:{content_hash}"
                        lock_key = f"lock:{content_hash}"

                        try:
                            lock = await lock_manager.lock(lock_key, lock_timeout=5)
                        except LockError:
                            print(f"Lock failed for {content_hash}")
                            await message.reject(requeue=False)
                            continue

                        try:
                            cached = await redis.get(cache_key)
                            if cached:
                                print(f"Using cached result for {content_hash}")
                                await save_to_db(session, cached)
                                continue

                            content = unpackb(content)
                            print(f"Received: {content}")

                            await save_to_db(session, content)
                            await redis.setex(
                                cache_key,
                                3600 * 24,  # TTL 24 часа
                                orjson.dumps(content)
                            )

                            print(f"Processed new message: {content_hash}")

                        finally:
                            await lock_manager.unlock(lock)

                    except Exception as e:
                        print(f"Error processing message: {str(e)}")
                        await message.reject(requeue=False)
                        raise

if __name__ == "__main__":
    asyncio.run(consume())