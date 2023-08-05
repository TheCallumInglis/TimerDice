import pika

from config import MQ_HOST, MQ_USER, MQ_PASS, MQ_QUEUE

class Consumer:
    channel = None
    callback = None

    def __init__(self, _callback):
        credentials = pika.PlainCredentials(MQ_USER, MQ_PASS)
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=MQ_HOST, credentials=credentials))

        self.channel = connection.channel()
        self.channel.queue_declare(queue=MQ_QUEUE, durable=True)
        self.channel.basic_qos(prefetch_count=1)

        self.callback = _callback

    def run(self):
        self.channel.basic_consume(queue=MQ_QUEUE, on_message_callback=self.callback)
        self.channel.start_consuming()

        print(' Waiting for messages...')
        