# pylint: disable=broad-exception-caught, unused-argument, missing-module-docstring
import json
from pprint import PrettyPrinter
import requests

from consumer import Consumer
from models import DiceRecording
from config import API_URL

# Callback for incoming MQ messages
def mq_callback(channel, method, properties, body):
    """ Process incoming RMQ Messages """
    print(" Received a message!")

    # Convert XML Message into Dice Recording object
    try:
        dice_recording:object = DiceRecording(body.decode())

    except Exception as ex:
        print(f"Failed to parse XML message! {ex}")
        channel.basic_nack(delivery_tag=method.delivery_tag)
        return

    print(json.dumps(dice_recording.__dict__))

    # POST to Web API
    uri = API_URL + '/recording'
    try:
        response = requests.post(uri, json=json.dumps(dice_recording.__dict__), timeout=30)
    except requests.Timeout:
        channel.basic_nack(delivery_tag=method.delivery_tag)
    except requests.ConnectionError:
        channel.basic_nack(delivery_tag=method.delivery_tag)

    pp.pprint(response.status_code)
    if response.status_code != 200:
        pp.pprint(response.text)
        channel.basic_nack(delivery_tag=method.delivery_tag)
        return

    if response.apparent_encoding != 'application/json':
        pp.pprint(response.text)
        channel.basic_nack(delivery_tag=method.delivery_tag)
        return

    pp.pprint(response.json())
    channel.basic_ack(delivery_tag=method.delivery_tag)

if __name__ == "__main__":
    pp = PrettyPrinter(indent=4)

    consumer = Consumer(mq_callback)
    consumer.run()
