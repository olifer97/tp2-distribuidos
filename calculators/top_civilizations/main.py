#!/usr/bin/env python3
import pika
import time
import json
import os
import heapq

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
        config_params['top_n'] = int(os.environ["TOP_N"])
        config_params['sentinels'] = int(os.environ["SENTINELS"])
    except KeyError as e:
        raise KeyError(
            "Key was not found. Error: {} .Aborting server".format(e))
    except ValueError as e:
        raise ValueError(
            "Key could not be parsed. Error: {}. Aborting server".format(e))

    return config_params

def top_n(top_civ, n, callback):
    top = heapq.nlargest(n, top_civ)
    for amount, civ in top:
        civ = {
            "civ": civ,
            "amount": amount,
        }
        callback(civ)

def main():
    config = parse_config_params()
    connection, channel = connect('rabbitmq')

    output_queue = Queue(connection, channel, output_queue=config['output_queue'])

    top_civ = []
    sentinels = 0

    def callback(msg):
        if 'final' in msg:
            nonlocal sentinels, top_civ
            sentinels += 1
            if sentinels == config['sentinels']:
                def send(data):
                    output_queue.send_bytes(json.dumps(data))
                top_n(top_civ, config['top_n'], send)
                output_queue.send_last()
                print("Termine")
                top_civ = []
                sentinels = 0
                
        else:
            civ = msg['civ']
            amount = msg['count']
            heapq.heappush(top_civ, (amount, civ)) 
            
    input_queue = Queue(connection, channel, input_queue=config['input_queue'], callback=callback)



if __name__ == "__main__":
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S',
    )
    main()