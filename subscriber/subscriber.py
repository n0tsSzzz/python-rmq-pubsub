import asyncio
from aio_pika import connect_robust, ExchangeType
from msgpack import unpackb
from cassandra.cluster import Cluster
import os

EXCHANGE_NAME = "pub/sub"

async def consume():
    cluster = Cluster(['cassandra'])
    session = cluster.connect('pubsub')

    print("Starting consumer")
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
                    content = unpackb(message.body)

                    print(f"Received: {content}")
                    await asyncio.get_event_loop().run_in_executor(
                        None,
                        lambda: session.execute(
                            f"INSERT INTO {os.getenv('MESSAGE_TABLE')} (id, content) VALUES (now(), %s)",
                            (content,)
                        )
                    )

if __name__ == "__main__":
    asyncio.run(consume())