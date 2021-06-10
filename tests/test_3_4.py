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

SOLUTION_3 = {
    'Aztecs' : 0,
    'Indians': 100,
    'Persians': 100,
    'Khmer': 0
}

SOLUTION_4 = {
    'Tatars': 1,
    'Franks': 1,
    'Indians': 4,
    'Khmer': 1
}

def main():

    matches_loader = threading.Thread(target=load, args=('3_4_matches.csv', 'matches', 0, 50000 ))
    match_players_loader = threading.Thread(target=load, args=('3_4_players.csv', 'match_players', 0, 10000))
    matches_loader.start()
    match_players_loader.start()

    matches_loader.join()
    match_players_loader.join()

    connection, channel = connect('localhost')

    state = {'3_finished': False, '4_finished': False}

    received_3 = {}

    def callback_3(body):
        civ = json.loads(body.decode('utf-8'))
        if 'final' in civ:
            state['3_finished'] = True
            print("Test 3 Success" if received_3 == SOLUTION_3 else "Test 3 Error")
            if state['4_finished']:exit()
        else:
            received_3[civ['civ']] = int(civ['victory_percentaje'])
            if civ['civ'] not in SOLUTION_3:
                print('Test 3 Error received_3 {} not expected'.format(match))

    queue = Queue(connection, channel, input_queue='3', callback=callback_3, iterate=False, start_consuming=False)

    received_4 = {}
        
    def callback_4(body):
        civ = json.loads(body.decode('utf-8'))
        if 'final' in civ:
            state['4_finished'] = True
            print("Test 4 Success" if received_4 == SOLUTION_4 else "Test 4 Error")
            if state['3_finished']:exit()
        else:
            received_4[civ['civ']] = int(civ['amount'])
            if civ['civ'] not in SOLUTION_4:
                print('Test 4 Error received_4 {} not expected'.format(civ))

    
    queue = Queue(connection, channel, input_queue='4', callback=callback_4, iterate=False)

if __name__ == "__main__":
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S',
    )
    main()