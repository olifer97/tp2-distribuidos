#!/usr/bin/env python3
import pika
import time
import json
from custom_queue import Queue, connect

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

    connection, channel = connect('rabbitmq')

    queue_1 = Queue(connection, channel, output_queue='clone_1_matches')
    queue_2 = Queue(connection, channel, output_queue='clone_2_matches')
        
    def callback(body):
        if 'final' in body:
            queue_1.send_with_last()
            queue_2.send_with_last()
        else:
            match1_reduce = { your_key: body[your_key] for your_key in ['token','average_rating','duration', 'server'] }
            queue_1.send(match1_reduce)
            match2_reduce = { your_key: body[your_key] for your_key in ['token', 'ladder', 'map', 'mirror'] }
            queue_2.send(match2_reduce)

    queue = Queue(connection, channel, input_queue='matches', callback=callback)
    

if __name__ == "__main__":
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S',
    )
    main()