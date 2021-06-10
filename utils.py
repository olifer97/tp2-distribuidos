from common.custom_queue import Queue, connect
import csv

def proccessChunk(header, chunk, callback):
    for row in chunk:
        dict_row = {}
        for i in range(len(header)):
            dict_row[header[i]] = row[i]
        callback(dict_row)

def load(csv_name, queue_name, total_rows = 0, size_msg = 1 ):
    connection, channel = connect('localhost')
    queue = Queue(connection, channel, output_queue=queue_name, size_msg=size_msg)
    def send(data):
        queue.send(data)
    reader = csv.reader(open(csv_name))
    headers = next(reader, None)
    chunk = []

    for i, line in enumerate(reader):
        if total_rows > 0 and i==total_rows:break
        if (i % size_msg == 0 and i > 0):
            
            proccessChunk(headers, chunk, send)
            del chunk[:]  # or: chunk = []
        chunk.append(line)
    proccessChunk(headers, chunk, send)
    queue.send_with_last()
    '''
    with open(csv_name, encoding='utf-8') as csvf:
        csvReader = csv.DictReader(csvf)
        j = 0
        for rows in csvReader:
            j += 1
            queue.send(rows)
            if total_rows > 0 and j==total_rows:break
    queue.send_with_last()
    '''
    