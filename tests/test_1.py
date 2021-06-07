#!/usr/bin/env python3
import pika
import time
import json
import csv
import threading

import logging

SOLUTION = set(["YES_1", "YES_2", "YES_3"])

def main():
    connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='matches')

    channel.queue_declare(queue='1')
    # Open a csv reader called DictReader
    with open('1.csv', encoding='utf-8') as csvf:
        csvReader = csv.DictReader(csvf)
        for rows in csvReader:
            channel.basic_publish(exchange='', routing_key='matches', body=json.dumps(rows))
        channel.basic_publish(exchange='', routing_key='matches', body=json.dumps({"final": True}))

    received = []

    def callback(ch, method, properties, body):
        print("[x] Received %r" % body)
        match = json.loads(body.decode('utf-8'))
        if 'final' in match:
            print("Test Success" if set(received) == SOLUTION else "Test Error")
            exit()
        received.append(match["token"])
        if match['token'] not in SOLUTION:
            print('Test Error received {} not expected'.format(match))

    channel.basic_consume(
        queue='1', on_message_callback=callback, auto_ack=True)

    channel.start_consuming()




if __name__ == "__main__":
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S',
    )
    main()