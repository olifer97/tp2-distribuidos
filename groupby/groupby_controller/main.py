#!/usr/bin/env python3
import pika
import time
import json
import os

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
    try:
        config_params["reducers"] = int(os.environ["K_REDUCERS"])
        config_params['input_queue'] = os.environ['INPUT_QUEUE']
        config_params['output_queues_suffix'] = os.environ['OUTPUT_QUEUES_SUFFIX']
        config_params["group_by"] = os.environ["GROUP_BY"]
        config_params['sentinels'] = int(os.environ["SENTINELS"])
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
    
    for i in range(config['reducers']):
        output_queues.append(Queue(connection, channel, output_queue='{}{}'.format(config['output_queues_suffix'],i)))

    sentinels = 0

    def callback(msg):
        if 'final' in msg:
            nonlocal sentinels
            sentinels += 1
            if sentinels == config['sentinels']:
                sentinels = 0
                for output_queue in output_queues:
                    output_queue.send_with_last()
        else:
            key = msg[config['group_by']]
            index_queue = hash(key) % config['reducers']
            output_queues[index_queue].send(msg)

    input_queue = Queue(connection, channel, input_queue=config['input_queue'], callback=callback)



if __name__ == "__main__":
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S',
    )
    main()