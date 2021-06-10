#!/usr/bin/env python3
import pika
import time
import json
import os

import logging

from custom_queue import Queue, connect

def parse_config_params():
    """ Parse env variables to find program config params

    Function that search and parse program configuration parameters in the
    program environment variables. If at least one of the config parameters
    is not found a KeyError exception is thrown. If a parameter could not
    be parsed, a ValueError is thrown. If parsing succeeded, the function
    returns a map with the env variables
    """
    config_params = {}
    try:
        config_params['left_input_queue'] = os.environ['LEFT_INPUT_QUEUE']
        config_params['right_input_queue'] = os.environ['RIGHT_INPUT_QUEUE']
        config_params['output_queues_suffix'] = os.environ['OUTPUT_QUEUES_SUFFIX']
        config_params["joiners"] = int(os.environ["K_JOINERS"])
        config_params["left_by"] = os.environ["LEFT_BY"]
        config_params["right_by"] = os.environ["RIGHT_BY"]
    except KeyError as e:
        raise KeyError(
            "Key was not found. Error: {} .Aborting server".format(e))
    except ValueError as e:
        raise ValueError(
            "Key could not be parsed. Error: {}. Aborting server".format(e))

    return config_params

def main():
    config = parse_config_params()
    connection, channel = connect('rabbitmq')

    output_queues = []
    for i in range(config['joiners']):
        output_queues.append(Queue(connection, channel, output_queue='{}{}'.format(config['output_queues_suffix'],i)))


    sentinels = 0

    def left_callback(data):
        if 'final' in data:
            nonlocal sentinels
            sentinels += 1
            if sentinels == 2:
                for output_queue in output_queues:
                    output_queue.send_with_last()
        else:
            token = data[config['left_by']]
            index_queue = hash(token) % config['joiners']
            message = {"side": "left", "data": data}
            output_queues[index_queue].send(message)

    def right_callback(data):
        if 'final' in data:
            nonlocal sentinels
            sentinels += 1
            if sentinels == 2:
                for output_queue in output_queues:
                    output_queue.send_with_last()
        else:
            token = data[config['right_by']]
            index_queue = hash(token) % config['joiners']
            message = {"side": "right", "data": data}
            output_queues[index_queue].send(message)
    

    left_input_queue = Queue(connection, channel, input_queue=config['left_input_queue'], callback=left_callback, start_consuming=False)
    right_input_queue = Queue(connection, channel, input_queue=config['right_input_queue'], callback=right_callback)

if __name__ == "__main__":
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S',
    )
    main()