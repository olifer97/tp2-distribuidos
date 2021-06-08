from common.custom_queue import Queue, connect
import csv

def load(csv_name, queue_name, total_rows = 0, size_msg = 1 ):
    connection, channel = connect('localhost')
    queue = Queue(connection, channel, output_queue=queue_name, size_msg=size_msg)

    with open(csv_name, encoding='utf-8') as csvf:
        csvReader = csv.DictReader(csvf)
        j = 0
        for rows in csvReader:
            j += 1
            queue.send(rows)
            if total_rows > 0 and j==total_rows:break
    queue.send_with_last()