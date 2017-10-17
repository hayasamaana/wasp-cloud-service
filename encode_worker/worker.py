#!/usr/bin/env python
import pika
from optparse import OptionParser
import ConfigParser
import shlex
from subprocess import call, STDOUT
import os


def callback(ch, method, properties, movieId):
	print(" [x] Received %r" % movieId)
	
	# Query the Mongo Database for information about the new movie
	# Update the statust to PROCESSING of the correct movie
	# Download the movie from the SWIFT object storage and save it as source 

	cmd = """mencoder %s -ovc lavc -lavcopts vcodec=mpeg4:vbitrate=3000
             -oac copy -o %s""" % (source, dest)
	print("Converting video file")
	
	call(shlex.split(cmd), stdout=os.devnull, stderr=STDOUT)

	

	# upload converted video to SWIFT 
	# Update the statust to DONE


def receive(connection_info=None):
	qname = connection_info["queue"]
	credentials = pika.PlainCredentials(connection_info["username"], connection_info["password"])
	connection = pika.BlockingConnection(pika.ConnectionParameters(connection_info["server"],connection_info["port"],'/',credentials))
	channel = connection.channel()

	channel.queue_declare(queue=qname)
	channel.basic_consume(callback, queue=qname, no_ack=True)
	print(' [*] Waiting for videos to encode. To exit press CTRL+C')
	channel.start_consuming()


if __name__=="__main__":
	parser = OptionParser()
	parser.add_option('-c', '--credential', dest='credentialFile', help='Path to CREDENTIAL file', metavar='CREDENTIALFILE')
	(options, args) = parser.parse_args()

	if options.credentialFile:
		config = ConfigParser.RawConfigParser()
		config.read(options.credentialFile)
		connection = {}
		connection["server"] = config.get('rabbit', 'server')
		connection["port"] = int(config.get('rabbit', 'port'))
		connection["queue"] = config.get('rabbit', 'queue')
		connection["username"] = config.get('user1', 'username')
		connection["password"] = config.get('user1', 'password')
		receive(connection_info=connection)
	else:
		# e.g. python backend.py -c credentials.txt
		print("Syntax: 'python worker.py -h' | '--help' for help")
