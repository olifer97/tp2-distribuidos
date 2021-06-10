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
        config_params["input_queue"] = os.environ["INPUT_QUEUE"]
        config_params["output_queue"] = os.environ["OUTPUT_QUEUE"]
        config_params['group_by'] = os.environ["GROUP_BY"]
    except KeyError as e:
        raise KeyError(
            "Key was not found. Error: {} .Aborting server".format(e))
    except ValueError as e:
        raise ValueError(
            "Key could not be parsed. Error: {}. Aborting server".format(e))

    return config_params

def groupby(data, groupby_key, callback):
    for key, aggregation in data.items():
        grouped_rows = {
            groupby_key: key,
            'count': aggregation['count'],
            'victories': aggregation['victories']
        }
        callback(grouped_rows)

def main():
    config = parse_config_params()

    connection, channel = connect('rabbitmq')

    output_queue = Queue(connection, channel, output_queue=config['output_queue'], size_msg=50000)

    data = {}

    def callback(msg):
        if 'final' in msg:
            nonlocal data
            def send(output):
                output_queue.send(output)
            groupby(data, config['group_by'], send)
            output_queue.send_with_last()
            data = {}
                
        else:
            key = msg[config['group_by']]
            if key not in data:
                data[key] = {'count': 1, 'victories': 1 if msg['winner'] == 'True' else 0}
            else:
                data[key]['count'] += 1
                data[key]['victories'] += 1 if msg['winner'] == 'True' else 0
        
    input_queue = Queue(connection, channel, input_queue=config['input_queue'], callback=callback)



if __name__ == "__main__":
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S',
    )
    main()