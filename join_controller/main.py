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
        config_params['left_input_queue'] = os.environ['LEFT_INPUT_QUEUE']
        config_params['right_input_queue'] = os.environ['RIGHT_INPUT_QUEUE']
        config_params['output_queues_suffix'] = os.environ['OUTPUT_QUEUES_SUFFIX']
        config_params["joiners"] = int(os.environ["K_JOINERS"])
        config_params["left_by"] = os.environ["LEFT_BY"]
        config_params["right_by"] = os.environ["RIGHT_BY"]
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
    channel.queue_declare(queue=config['left_input_queue'])
    channel.queue_declare(queue=config['right_input_queue'])
    for i in range(config['joiners']):
        channel.queue_declare(queue='{}{}'.format(config['output_queues_suffix'],i))


    def left_callback(ch, method, properties, body):
        #print("[x] Received %r" % body)
        #print("[x] Received left")
        data = json.loads(body.decode('utf-8'))
        if 'final' in data:
            for i in range(config['joiners']):
                channel.basic_publish(exchange='', routing_key='{}{}'.format(config['output_queues_suffix'],i), body=body)
        else:
            token = data[config['left_by']]
            queue = hash(token) % config['joiners']
            message = json.dumps({"side": "left", "data": data})
            channel.basic_publish(exchange='', routing_key='{}{}'.format(config['output_queues_suffix'],queue), body=message)

    def right_callback(ch, method, properties, body):
        #print("[x] Received right")
        data = json.loads(body.decode('utf-8'))
        if 'final' in data:
            for i in range(config['joiners']):
                channel.basic_publish(exchange='', routing_key='{}{}'.format(config['output_queues_suffix'],i), body=body)
        else:
            token = data[config['right_by']]
            queue = hash(token) % config['joiners']
            message = json.dumps({"side": "right", "data": data})
            channel.basic_publish(exchange='', routing_key='{}{}'.format(config['output_queues_suffix'],queue), body=message)
    
    channel.basic_consume(
        queue=config['left_input_queue'], on_message_callback=left_callback, auto_ack=True)
    channel.basic_consume(
        queue=config['right_input_queue'], on_message_callback=right_callback, auto_ack=True)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == "__main__":
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S',
    )
    main()