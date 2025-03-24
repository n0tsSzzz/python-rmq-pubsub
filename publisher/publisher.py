import asyncio
from aio_pika import DeliveryMode, ExchangeType, Message, connect_robust
from msgpack import packb

import os

EXCHANGE_NAME = "pub/sub"


async def main():
    print("Starting publisher")
    con = f"amqp://{os.getenv('RABBITMQ_USER')}:{os.getenv('RABBITMQ_PASSWORD')}@{os.getenv('RABBITMQ_HOST')}:{os.getenv('RABBITMQ_PORT')}/"
    connection = await connect_robust(con)
    print("Connected to RabbitMQ")

    async with connection:
        channel = await connection.channel()

        exchange = await channel.declare_exchange(
            EXCHANGE_NAME, ExchangeType.FANOUT,
        )

        with open("input.txt", "r") as file:
            while True:
                for line in file:
                    body = packb(line.strip())
                    message = Message(
                        body=body, delivery_mode=DeliveryMode.PERSISTENT,
                    )

                    await exchange.publish(message, routing_key="text_file")

                    print(f"Sent: {line.strip()}")

                print('--- Sent full file data ---')
                await asyncio.sleep(5)
                file.seek(0)


if __name__ == "__main__":
    asyncio.run(main())