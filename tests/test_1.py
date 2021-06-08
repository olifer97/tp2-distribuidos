#!/usr/bin/env python3
import pika
import time
import json
import csv
import threading

import logging

import sys
sys.path.append('../')

from common.custom_queue import Queue, connect
from utils import load

SOLUTION = set(["YES_1", "YES_2", "YES_3"])

def main():
    load('1.csv', 'matches')

    received = []

    def callback(body):
        print("[x] Received %r" % body)
        match = json.loads(body.decode('utf-8'))
        if 'final' in match:
            print("Test Success" if set(received) == SOLUTION else "Test Error")
            exit()
        received.append(match["token"])
        if match['token'] not in SOLUTION:
            print('Test Error received {} not expected'.format(match))

    connection, channel = connect('localhost')
    queue = Queue(connection, channel, input_queue='1', callback=callback, iterate=False)

if __name__ == "__main__":
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S',
    )
    main()