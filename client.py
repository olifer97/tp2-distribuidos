#!/usr/bin/env python3
import pika
import time
import json
import csv
import threading

import logging


def loadMatches():
    connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='matches')
    # Open a csv reader called DictReader
    with open('matches.csv', encoding='utf-8') as csvf:
        csvReader = csv.DictReader(csvf)
        j = 0
        for rows in csvReader:
            j += 1
            channel.basic_publish(exchange='', routing_key='matches', body=json.dumps(rows))
            if j==200000:break
    connection.close()
    
def loadPlayers():
    connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='match_players')
    # Open a csv reader called DictReader
    with open('match_players.csv', encoding='utf-8') as csvf:
        csvReader = csv.DictReader(csvf)
        i = 0
        for rows in csvReader:
            i += 1
            channel.basic_publish(exchange='', routing_key='match_players', body=json.dumps(rows))
            if i==200000:break
        channel.basic_publish(exchange='', routing_key='match_players', body=json.dumps({"final": True}))
    connection.close()

def main():
    matches_loader = threading.Thread(target=loadMatches)
    match_players_loader = threading.Thread(target=loadPlayers)
    matches_loader.start()
    match_players_loader.start()

    matches_loader.join()
    match_players_loader.join()
            



if __name__ == "__main__":
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S',
    )
    main()
