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
        config_params["input_queue"] = os.environ["INPUT_QUEUE"]
        config_params["output_queue"] = os.environ["OUTPUT_QUEUE"]
        config_params["left_by"] = os.environ["LEFT_BY"]
        config_params["right_by"] = os.environ["RIGHT_BY"]
    except KeyError as e:
        raise KeyError(
            "Key was not found. Error: {} .Aborting server".format(e))
    except ValueError as e:
        raise ValueError(
            "Key could not be parsed. Error: {}. Aborting server".format(e))

    return config_params

def join(matches, callback):
    for key, left_and_right in matches.items():
        left = left_and_right["left_by"]
        right = left_and_right["right_by"]
        if len(left) == 0 or len(right) == 0:
            continue
        for l in left:
            for r in right:
                joined = {**l, **r}
                callback(joined)

def main():
    config = parse_config_params()
    connection, channel = connect('rabbitmq')

    output_queue = Queue(connection, channel, output_queue=config['output_queue'], size_msg=50000)

    matches = {}

    def callback(row):
        if 'final' in row:
            nonlocal matches
            def send(data):
                output_queue.send(data)
            join(matches, send)
            output_queue.send_with_last()
            matches = {}
                
        else:
            side = "left_by" if row['side'] == "left" else "right_by"
            data = row['data']
            key = data[config[side]]

            if key not in matches:
                matches[key] = {"left_by": [], "right_by": []}
                
            matches[key][side].append(data)
            
    input_queue = Queue(connection, channel, input_queue=config['input_queue'], callback=callback)



if __name__ == "__main__":
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S',
    )
    main()