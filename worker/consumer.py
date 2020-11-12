import os
import pika
import psycopg2
import spacy
import time

from pipeline import PipelineError
from pipeline import Pipeline


QUEUE_NAME = os.getenv('QUEUE_NAME')
DB_USER = os.getenv('POSTGRES_USER')
DB_PASS = os.getenv('POSTGRES_PASSWORD')
DB_NAME = os.getenv('POSTGRES_DB')

counter = 0


conn = psycopg2.connect(
           host="postgresql",
           database=DB_NAME,
           user=DB_USER,
           password=DB_PASS)
conn.autocommit = True

nlp = spacy.load("en_core_web_sm")


def on_message(channel, method_frame, header_frame, body):
    global counter
    global conn
    channel.basic_ack(delivery_tag=method_frame.delivery_tag)
    lines = body.decode()
    pln = Pipeline(lines, conn, nlp)
    pln.run()
    counter = counter + 1
    print(counter)


def consume(queue_number=1):
    queue_name = "{}{}".format(QUEUE_NAME, queue_number)
    while True:

        print("consuming...{}".format(queue_name))
        connection = pika.BlockingConnection(pika.ConnectionParameters('rabbit'))
        channel = connection.channel()
        try:
            channel.basic_consume(queue_name, on_message)
            channel.start_consuming()
        except KeyboardInterrupt:
            channel.stop_consuming()
        except pika.exceptions.StreamLostError as e:
            print(e)
        except pika.exceptions.ChannelClosedByBroker as e:
            print(e)
        except pika.exceptions.ConnectionWrongStateError as e:
            print(e)
        except PipelineError as e:
            print(e)
        except psycopg2.InterfaceError:
            # reload connection
            global conn
            conn = psycopg2.connect(
                            host="postgresql",
                            database=DB_NAME,
                            user=DB_USER,
                            password=DB_PASS)
            conn.autocommit = True

        print("sleeping")
        time.sleep(3)

    connection.close()
