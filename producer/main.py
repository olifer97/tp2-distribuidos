#!/usr/bin/env python3
import pika
import time

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

    for i in range(100):
        msg = ""
        if i%2:
            msg = "team"
        else:
            msg = "1v1"
        channel.basic_publish(exchange='', routing_key='matches', body=msg)
        print(" [x] Sent {}".format(msg))
        time.sleep(1)

    connection.close()
            



if __name__ == "__main__":
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S',
    )
    main()
