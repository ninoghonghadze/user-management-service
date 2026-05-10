import json
from datetime import datetime

import aio_pika

from app.core.config import settings


async def publish_password_reset(email: str, reset_link: str):
    connection = await aio_pika.connect_robust(settings.rabbitmq_url)
    async with connection:
        channel = await connection.channel()
        queue = await channel.declare_queue("reset-password-stream", durable=True)
        message_body = {
            "email": email,
            "subject": "Password Reset Request",
            "body": f"Click the link to reset your password: {reset_link}",
            "datetime": datetime.utcnow().isoformat(),
        }
        await channel.default_exchange.publish(
            aio_pika.Message(
                body=json.dumps(message_body).encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            ),
            routing_key=queue.name,
        )
