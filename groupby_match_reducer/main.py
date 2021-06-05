#!/usr/bin/env python3
import pika
import time
import json
import os

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
    #result = []
    for match_token, players in matches.items():
        if len(players) != 2:
            continue
        winner, looser = (players[0], players[1]) if players[0]['winner'] else (players[1], players[0])
        match = {
            "match": match_token,
            "rtg_winner": winner['rating'],
            "rtg_loser": looser['rating']
        }
        callback(match)
        #result.append(match)
    #return result

def main():
    config = parse_config_params()
    connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='rabbitmq'))

    channel = connection.channel()
    channel.queue_declare(queue=config['input_queue'])
    channel.queue_declare(queue=config['output_queue'])

    matches = {}

    def callback(ch, method, properties, body):
        #print("[x] Received %r" % body)
        msg = json.loads(body.decode('utf-8'))
        if 'final' in msg:
            def send(data):
                channel.basic_publish(exchange='', routing_key=config['output_queue'], body=json.dumps(data))
            groupby_and_filter(matches, send)
                
        else:
            match_token = msg['match']
            if match_token not in matches:
                matches[match_token] = [msg]
            else:
                matches[match_token].append(msg)
            
        

    channel.basic_consume(
        queue=config['input_queue'], on_message_callback=callback, auto_ack=True)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()



if __name__ == "__main__":
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S',
    )
    main()