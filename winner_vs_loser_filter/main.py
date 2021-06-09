#!/usr/bin/env python3
import pika
import time
import json
from datetime import datetime, timedelta
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
    output_queue = Queue(connection, channel, output_queue=config['output_queue'])

    sentinels = 0

    def callback(players):
        #print("lo que me llega {}".format(players))
        if 'final' in players:
            nonlocal sentinels
            sentinels += 1
            if sentinels == config['sentinels']:
                output_queue.send_last()
        else:
            winner_string_rating = players['rtg_winner']
            winner_rating = 0 if winner_string_rating == '' else float(winner_string_rating)

            loser_string_rating = players['rtg_loser']
            loser_rating = 0 if loser_string_rating == '' else float(loser_string_rating)

            if winner_rating > 1000 and (loser_rating-winner_rating)*100/winner_rating > 30:
                #print("con lo que me quedo {}".format(players))
                output_queue.send_bytes(json.dumps(players))

    input_queue = Queue(connection, channel, input_queue=config['input_queue'], callback=callback)                



if __name__ == "__main__":
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S',
    )
    main()