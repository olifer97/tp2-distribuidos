#!/usr/bin/env python3
import pika
import time
import json
import csv
import threading

import logging


def loadMatches(channel):
    # Open a csv reader called DictReader
    with open('matches.csv', encoding='utf-8') as csvf:
        csvReader = csv.DictReader(csvf)
        for rows in csvReader:
            channel.basic_publish(exchange='', routing_key='matches', body=json.dumps(rows))
    

def loadPlayers(channel):
    # Open a csv reader called DictReader
    with open('match_players.csv', encoding='utf-8') as csvf:
        csvReader = csv.DictReader(csvf)
        for rows in csvReader:
            channel.basic_publish(exchange='', routing_key='match_players', body=json.dumps(rows))

def main():
    connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='matches')
    channel.queue_declare(queue='match_players')

    #channel.basic_publish(exchange='', routing_key='matches', body=msg)

    matches_loader = threading.Thread(target=loadMatches, args=(channel,))
    #match_players_loader = threading.Thread(target=loadPlayers, args=(channel,))
    matches_loader.start()
    #match_players_loader.start()

    matches_loader.join()
    #match_players_loader.join()

    print(" hola")

    #connection.close()
            



if __name__ == "__main__":
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S',
    )
    main()
