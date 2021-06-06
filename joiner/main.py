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
            for r in rigth:
                joined = {**l, **r}
                print(joined)
                callback(joined)

def main():
    config = parse_config_params()
    connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='rabbitmq'))

    channel = connection.channel()
    channel.queue_declare(queue=config['input_queue'])
    channel.queue_declare(queue=config['output_queue'])

    matches = {}

    def callback(ch, method, properties, body):
        print("[x] Received %r" % body)
        msg = json.loads(body.decode('utf-8'))
        if 'final' in msg:
            def send(data):
                channel.basic_publish(exchange='', routing_key=config['output_queue'], body=json.dumps(data))
            join(matches, send)
                
        else:
            side = "left_by" if msg['side'] == "left" else "right_by"
            data = msg['data']
            key = data[config[side]]

            if key not in matches:
                matches[key] = {"left_by": [], "right_by": []}
                
            matches[key][side].append(data)
            
        

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