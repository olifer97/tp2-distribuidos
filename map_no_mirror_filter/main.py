#!/usr/bin/env python3
import pika
import time
import json
from datetime import datetime, timedelta
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
    connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='rabbitmq'))

    channel = connection.channel()
    channel.queue_declare(queue=config['input_queue'])
    channel.queue_declare(queue=config['output_queue'])

    def callback(ch, method, properties, body):
        #print("[x] Received %r" % body)
        match = json.loads(body.decode('utf-8'))

        if 'final' in match:
            channel.basic_publish(exchange='', routing_key=config['output_queue'], body=body)
        else:
            if match['map'] == config['map']:
                if not config['no_mirror'] or (config['no_mirror'] and match['mirror'] == 'False'):
                    channel.basic_publish(exchange='', routing_key=config['output_queue'], body=body)
                    

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