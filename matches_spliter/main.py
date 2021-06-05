#!/usr/bin/env python3
import pika
import time
import json

import logging

def parse_config_params():
    """ Parse env variables to find program config params

    Function that search and parse program configuration parameters in the
    program environment variables. If at least one of the config parameters
    is not found a KeyError exception is thrown. If a parameter could not
    be parsed, a ValueError is thrown. If parsing succeeded, the function
    returns a map with the env variables
    """
    config_params = {}

    return config_params

def main():
    connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='rabbitmq'))

    channel = connection.channel()
    channel.queue_declare(queue='matches')
    channel.queue_declare(queue='clone_1_matches')
    channel.queue_declare(queue='clone_2_matches')


    def callback(ch, method, properties, body):
        #print("[x] Received %r" % body)
        channel.basic_publish(exchange='', routing_key='clone_1_matches', body=body)
        channel.basic_publish(exchange='', routing_key='clone_2_matches', body=body)

    channel.basic_consume(
        queue='matches', on_message_callback=callback, auto_ack=True)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()



if __name__ == "__main__":
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S',
    )
    main()