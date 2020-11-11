import os
import pika
import time

from pipeline import Pipeline


QUEUE_NAME = os.getenv('QUEUE_NAME')
counter = 0


def on_message(channel, method_frame, header_frame, body):
    global counter

    channel.basic_ack(delivery_tag=method_frame.delivery_tag)
    lines = body.decode()
    pln = Pipeline(lines)
    pln.run()
    counter = counter + 1
    print(counter)
    raise Exception("carajo")


while True:

    print("consuming...")
    connection = pika.BlockingConnection(pika.ConnectionParameters('rabbit'))
    channel = connection.channel()
    try:
        channel.basic_consume(QUEUE_NAME, on_message)
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()
    except pika.exceptions.ChannelClosedByBroker as e:
        print(e)

    connection.close()

    print("sleeping")
    time.sleep(10)
