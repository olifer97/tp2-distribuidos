#!/usr/bin/env python3
import pika
import time
import json
from datetime import datetime, timedelta
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
        config_params['map'] = os.environ["MAP"]
        config_params['no_mirror'] = True if os.environ["NO_MIRROR"]=='true' else False
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

    output_queue = Queue(connection, channel, output_queue=config['output_queue'])

    def callback(match):
        if 'final' in match:
            output_queue.send_with_last()
            #channel.basic_publish(exchange='', routing_key=config['output_queue'], body=body)
        else:
            if match['map'] == config['map']:
                if not config['no_mirror'] or (config['no_mirror'] and match['mirror'] == 'False'):
                    output_queue.send(match)
                    #channel.basic_publish(exchange='', routing_key=config['output_queue'], body=body)

    input_queue = Queue(connection, channel, input_queue=config['input_queue'], callback=callback)


if __name__ == "__main__":
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S',
    )
    main()