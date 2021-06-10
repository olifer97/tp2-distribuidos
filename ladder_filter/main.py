#!/usr/bin/env python3
import pika
import time
import json

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

    return config_params

def main():
    config = parse_config_params()
    connection, channel = connect('rabbitmq')

    vteam_queue = Queue(connection, channel, output_queue='team_matches')
    v1_queue = Queue(connection, channel, output_queue='1v1_matches')

    matches = {}

    def callback(match):
        if 'final' in match:
            vteam_queue.send_with_last()
            v1_queue.send_with_last()
        else:
            if match['ladder'] == 'RM_TEAM':
                del match['ladder']
                vteam_queue.send(match)
            elif match['ladder'] == 'RM_1v1':
                del match['ladder']
                v1_queue.send(match)
    input_queue = Queue(connection, channel, input_queue='clone_2_matches', callback=callback)



if __name__ == "__main__":
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S',
    )
    main()