import pika

_queue = 'timer_amqp'
print(' Connecting to server ...')

try:
    credentials = pika.PlainCredentials('user', 'password')
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq", credentials=credentials))

except pika.exceptions.AMQPConnectionError as exc:
    print("Failed to connect to RabbitMQ service. Message wont be sent.")
    exit(0)

channel = connection.channel()
channel.queue_declare(queue=_queue, durable=True)

print(' Waiting for messages...')


def callback(ch, method, properties, body):
    print(" Received a message!")
    print("%s" % body.decode())
    print(" Done")

    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue=_queue, on_message_callback=callback)
channel.start_consuming()