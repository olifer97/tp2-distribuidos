#!/usr/bin/env python3
import pika
import time
import json
import csv
import threading

import logging

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

def loadMatches():
    connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='matches')
    # Open a csv reader called DictReader
    with open('3_4_matches.csv', encoding='utf-8') as csvf:
        csvReader = csv.DictReader(csvf)
        for rows in csvReader:
            channel.basic_publish(exchange='', routing_key='matches', body=json.dumps(rows))
        channel.basic_publish(exchange='', routing_key='matches', body=json.dumps({"final": True}))
    connection.close()
    
def loadPlayers():
    connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='match_players')
    # Open a csv reader called DictReader
    with open('3_4_players.csv', encoding='utf-8') as csvf:
        csvReader = csv.DictReader(csvf)
        for rows in csvReader:
            channel.basic_publish(exchange='', routing_key='match_players', body=json.dumps(rows))
        channel.basic_publish(exchange='', routing_key='match_players', body=json.dumps({"final": True}))
    connection.close()

def main():

    matches_loader = threading.Thread(target=loadMatches)
    match_players_loader = threading.Thread(target=loadPlayers)
    matches_loader.start()
    match_players_loader.start()

    matches_loader.join()
    match_players_loader.join()

    connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='3')
    channel.queue_declare(queue='4')

    state = {'3_finished': False, '4_finished': False}

    received_3 = {}

    def callback_3(ch, method, properties, body):
        print("[x] Received_3 %r" % body)
        civ = json.loads(body.decode('utf-8'))
        if 'final' in civ:
            state['3_finished'] = True
            print("Test 3 Success" if received_3 == SOLUTION_3 else "Test 3 Error")
            if state['4_finished']:exit()
        else:
            received_3[civ['civ']] = int(civ['victory_percentaje'])
            if civ['civ'] not in SOLUTION_3:
                print('Test 3 Error received_3 {} not expected'.format(match))

    channel.basic_consume(
        queue='3', on_message_callback=callback_3, auto_ack=True)

    received_4 = {}
        
    def callback_4(ch, method, properties, body):
        print("[x] Received %r" % body)
        civ = json.loads(body.decode('utf-8'))
        if 'final' in civ:
            state['4_finished'] = True
            print("Test 4 Success" if received_4 == SOLUTION_4 else "Test 4 Error")
            if state['3_finished']:exit()
        else:
            received_4[civ['civ']] = int(civ['amount'])
            if civ['civ'] not in SOLUTION_4:
                print('Test 4 Error received_4 {} not expected'.format(civ))

    
    channel.basic_consume(
        queue='4', on_message_callback=callback_4, auto_ack=True)

    channel.start_consuming()




if __name__ == "__main__":
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S',
    )
    main()