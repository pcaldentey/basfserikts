import logging
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
queue_name = None

conn = psycopg2.connect(
           host="postgresql",
           database=DB_NAME,
           user=DB_USER,
           password=DB_PASS)
conn.autocommit = True

nlp = spacy.load("en_core_web_sm")
logging.basicConfig(level=logging.INFO)


def on_message(channel, method_frame, header_frame, body):
    global counter
    global conn
    channel.basic_ack(delivery_tag=method_frame.delivery_tag)
    lines = body.decode()
    pln = Pipeline(lines, conn, nlp)
    pln.run()
    counter = counter + 1
    if counter % 50 == 0:
        logging.info("consumer {}: {} messages consumed ".format(queue_name, counter))


def consume(queue_number=1):
    global queue_name
    queue_name = "{}{}".format(QUEUE_NAME, queue_number)
    while True:

        connection = pika.BlockingConnection(pika.ConnectionParameters('rabbit'))
        channel = connection.channel()
        logging.info("{}:Start consuming...".format(queue_name))  # will not print anything

        try:
            channel.basic_consume(queue_name, on_message)
            channel.start_consuming()
        except KeyboardInterrupt:
            channel.stop_consuming()
        except pika.exceptions.StreamLostError as e:
            logging.error(e)
        except pika.exceptions.ChannelClosedByBroker as e:
            logging.error(e)
        except pika.exceptions.ConnectionWrongStateError as e:
            logging.error(e)
        except PipelineError as e:
            logging.error(e)
        except psycopg2.InterfaceError:
            # reload connection
            global conn
            conn = psycopg2.connect(
                            host="postgresql",
                            database=DB_NAME,
                            user=DB_USER,
                            password=DB_PASS)
            conn.autocommit = True

        logging.info("{}:sleeping".format(queue_name))
        time.sleep(3)

    connection.close()
