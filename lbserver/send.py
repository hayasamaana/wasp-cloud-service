#!/usr/bin/env python
import pika


credentials = pika.PlainCredentials('test','test')
connection = pika.BlockingConnection(pika.ConnectionParameters('172.16.0.8',int('5672'),'/',credentials))
channel = connection.channel()

channel.queue_declare(queue='lb_queue')



channel.basic_publish(exchange='',
                      routing_key='lb_queue',
                      body='1170.0.0.0')
print(" [x] Add a VM")
connection.close()
