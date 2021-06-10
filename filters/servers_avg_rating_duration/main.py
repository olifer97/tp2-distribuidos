#!/usr/bin/env python3
import pika
import time
import json
from datetime import datetime, timedelta
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

def to_timedelta(string_time):
    if 'days' in string_time:
        time_split = string_time.split(" days, ")
        days, timestamp = time_split
    elif 'day' in string_time:
        time_split = string_time.split(" day, ")
        days, timestamp = time_split
    else:
        days = "0"
        timestamp = string_time
    t = datetime.strptime(timestamp,"%H:%M:%S") + timedelta(days=int(days))
    return timedelta(days=t.day, hours=t.hour, minutes=t.minute, seconds=t.second)

def main():
    connection, channel = connect('rabbitmq')

    output_queue = Queue(connection, channel, output_queue='1')

    def callback(match):
        if 'final' in match:
            output_queue.send_last()
            print("Termine")
            return
        else:
            server = match['server']
            string_avg_rating = match['average_rating']
            avg_rating = 0 if string_avg_rating == '' else float(string_avg_rating)
            duration = to_timedelta(match['duration'])

            if server == 'koreacentral' or server == 'southeastasia' or server == 'eastus':
                if avg_rating >= 2000:
                    if duration > to_timedelta("02:00:00"):
                        logging.info("Found match")
                        output_queue.send_bytes(json.dumps(match))

    input_queue = Queue(connection, channel, input_queue='clone_1_matches', callback=callback)



if __name__ == "__main__":
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S',
    )
    main()