#!/usr/bin/env python3
import pika
import time
import json
import csv
import threading
from utils import load
import sys

import logging

def main():
    lines = 0 if len(sys.argv) < 2 else int(sys.argv[1])
    matches_loader = threading.Thread(target=load, args=('matches.csv', 'matches', lines, 100000 ))
    match_players_loader = threading.Thread(target=load, args=('match_players.csv', 'match_players', lines, 10000))
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
