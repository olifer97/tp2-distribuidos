import pika
import logging
import json

def connect(host):
    connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=host))

    channel = connection.channel()
    return (connection, channel)

class Queue:
    def __init__(self, connection, channel, input_queue=None, iterate=True, callback=None, output_queue=None, size_msg=100000):
        self.connection = connection
        self.channel = channel

        if input_queue:
            self.input_queue = input_queue
            self.callback = callback
            self.iterate = iterate
            self.channel.queue_declare(queue=self.input_queue)
            self.channel.basic_consume(queue=self.input_queue, on_message_callback=self.__callback, auto_ack=True)
            self.channel.start_consuming()
        if output_queue:
            self.output_queue = output_queue
            self.size_msg = size_msg
            self.msg = { 'records': [] }
            self.msg_so_far = 0
            self.channel.queue_declare(queue=self.output_queue) 

    def __callback(self, ch, method, properties, body):
        if self.iterate:
            msg = json.loads(body.decode('utf-8'))
            for record in msg['records']:
                self.callback(record)
        else:
            self.callback(body)

    def send(self, record):
        self.msg['records'].append(record)
        self.msg_so_far +=1
        if self.msg_so_far == self.size_msg:
            self.channel.basic_publish(exchange='', routing_key=self.output_queue, body=json.dumps(self.msg))
            self.msg_so_far = 0
            self.msg['records'] = []

    def send_with_last(self):
        self.msg['records'].append({'final': True})
        self.channel.basic_publish(exchange='', routing_key=self.output_queue, body=json.dumps(self.msg))
        self.msg_so_far = 0
        self.msg['records'] = []
    
    def send_bytes(self, body):
        self.channel.basic_publish(exchange='', routing_key=self.output_queue, body=body)

    def send_last(self):
        self.channel.basic_publish(exchange='', routing_key=self.output_queue, body=json.dumps({'final': True}))


     

    