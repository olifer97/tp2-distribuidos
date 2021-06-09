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
    except KeyError as e:
        raise KeyError(
            "Key was not found. Error: {} .Aborting server".format(e))
    except ValueError as e:
        raise ValueError(
            "Key could not be parsed. Error: {}. Aborting server".format(e))

    return config_params

def groupby_and_filter(matches, callback):
    for match_token, players in matches.items():
        if len(players) != 2: continue
        
        player_0_is_winner, player_1_is_winner = (players[0]['winner'] == 'True',players[1]['winner'] == 'True')
        if [player_0_is_winner, player_1_is_winner].count(True) == 1:
            winner, loser = (players[0], players[1]) if player_0_is_winner else (players[1], players[0])
            match = {
                "match": match_token,
                "rtg_winner": winner['rating'],
                "rtg_loser": loser['rating']
            }
            callback(match)
                
            

def main():
    config = parse_config_params()
    connection, channel = connect('rabbitmq')

    output_queue = Queue(connection, channel, output_queue=config['output_queue'], size_msg=50000)

    matches = {}

    def callback(msg):
        #print("[x] Received %r" % body)
        #msg = json.loads(body.decode('utf-8'))
        #print("recibo {}".format(msg))
        if 'final' in msg:
            #print("recibi final!")
            def send(data):
                output_queue.send(data)
            groupby_and_filter(matches, send)
            output_queue.send_with_last()
                
        else:
            match_token = msg['match']
            if match_token not in matches:
                matches[match_token] = [msg]
            else:
                matches[match_token].append(msg)
            
    input_queue = Queue(connection, channel, input_queue=config['input_queue'], callback=callback)



if __name__ == "__main__":
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S',
    )
    main()