import pika

from config import MQ_HOST, MQ_USER, MQ_PASS, MQ_QUEUE

class Consumer:
    def __init__(self, _callback):
        credentials = pika.PlainCredentials(MQ_USER, MQ_PASS)
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=MQ_HOST, credentials=credentials))

        channel = connection.channel()
        channel.queue_declare(queue=MQ_QUEUE, durable=True)

        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue=MQ_QUEUE, on_message_callback=_callback)
        channel.start_consuming()

        print(' Waiting for messages...')