#!/usr/bin/env python3
import pika
import time
import json
import os

from custom_queue import Queue, connect

import logging

def parse_config_params():
    config_params = {}
    try:
        config_params["input_queue"] = os.environ["INPUT_QUEUE"]
        config_params["queue_1"] = os.environ["QUEUE_1"]
        config_params["queue_2"] = os.environ["QUEUE_2"]
        config_params["queue_filtered"] = os.environ["QUEUE_FILTERED"]
        config_params["columns_1"] = os.environ["COLUMNS_1"].split(",")
        config_params["columns_2"] = os.environ["COLUMNS_2"].split(",")
        config_params["columns_filtered"] = os.environ["COLUMNS_FILTERED"].split(",")
        config_params["rating_field"] = os.environ["RATING_FIELD"]
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

    queue_1 = Queue(connection, channel, output_queue=config['queue_1'])
    queue_2 = Queue(connection, channel, output_queue=config['queue_2'])
    queue_greater_2000 = Queue(connection, channel, output_queue=config['queue_filtered'])
        
    def callback(body):
        if 'final' in body:
            queue_1.send_with_last()
            queue_2.send_with_last()
            queue_greater_2000.send_with_last()
        else:
            rating_field = config["rating_field"]
            player2_reduce = { your_key: body[your_key] for your_key in config['columns_2'] }
            queue_2.send(player2_reduce)
            player_reduce = { your_key: body[your_key] for your_key in config['columns_1'] }
            queue_1.send(player_reduce)
            string_rating = body[rating_field] if rating_field in body else ''
            rating = 0 if not string_rating or not string_rating.isdecimal() else float(string_rating)
            if rating > 2000:
                pro_players_reduce = { your_key: body[your_key] for your_key in config['columns_filtered'] }
                queue_greater_2000.send(body)

    input_queue = Queue(connection, channel, input_queue=config['input_queue'], callback=callback)


if __name__ == "__main__":
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S',
    )
    main()