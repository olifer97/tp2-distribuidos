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

    queue_1 = Queue(connection, channel, output_queue='players_clone_1')
    queue_2 = Queue(connection, channel, output_queue='players_clone_2')
    queue_greater_2000 = Queue(connection, channel, output_queue='players_greater_2000')
        
    def callback(body):
        if 'final' in body:
            queue_1.send_with_last()
            queue_2.send_with_last()
            queue_greater_2000.send_with_last()
        else:
            player2_reduce = { your_key: body[your_key] for your_key in ['match','civ','token', 'winner'] }
            queue_2.send(player2_reduce)
            player_reduce = { your_key: body[your_key] for your_key in ['match','rating','token', 'winner'] }
            queue_1.send(player_reduce)
            string_rating = body['rating'] if 'rating' in body else ''
            rating = 0 if not string_rating or not string_rating.isdecimal() else float(string_rating)
            if rating > 2000:
                pro_players_reduce = { your_key: body[your_key] for your_key in ['match','token','civ'] }
                queue_greater_2000.send(body)

    input_queue = Queue(connection, channel, input_queue='match_players', callback=callback)


if __name__ == "__main__":
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S',
    )
    main()