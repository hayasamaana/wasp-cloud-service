#!/usr/bin/env python
import pika
from optparse import OptionParser
import ConfigParser
import shlex
from subprocess import call, STDOUT
import sys
import os

# Importing mongodb & Swift wrapper
sys.path.append("../")
sys.path.append('../mongodb')
import dbwrp
from swiftwrapper.wrapper import SwiftWrapper, ServiceDefaults


def callback(ch, method, properties, movieId):
	print(" [x] Received %r for encoding" % movieId)
	# Query the Mongo Database for information about the new movie
	doc = dbwrp.getDocumentById(movieId)

	if doc:
		print("Got document: ", doc)
		# Update the statust to CONVERTING of the correct movie
		dbwrp.updateDocumentStatus(movieId, "CONVERTING")

		# Download the Video from the Storage. The vide file name is saved in the title parameter of the document with the given id
		sw = SwiftWrapper()
		source = sw.download_item(doc["title"])

		destSplit = source.split(".")
		dest = destSplit[0] + "CONVERTED" + "." + destSplit[1]

		print("SOURCE: ", source)
		print("DEST: ", dest)

		cmd = """mencoder %s -ovc lavc -lavcopts vcodec=mpeg4:vbitrate=3000 -oac copy -o %s""" % (
			source, dest)
		print("Converting video file")

		FNULL = open(os.devnull, 'w')

		call(shlex.split(cmd), stdout=FNULL, stderr=STDOUT)

		# upload converted video to SWIFT container
		print("Uploading Converted Video")
		movies = container=ServiceDefaults.DEFAULT_VIDEO_CONTAINER
		sw.upload_item(movies,dest)

		# Update the statust to DONE
		dbwrp.updateDocumentStatus(movieId, "DONE")

		# Add the path to the converted file
		dbwrp.updateDocument(movieId,"convertedTitle",dest)
	else:
		print("No document found, skipping ", movieId)


def receive(connection_info=None):
	qname = connection_info["queue"]
	credentials = pika.PlainCredentials(
		connection_info["username"], connection_info["password"])
	connection = pika.BlockingConnection(pika.ConnectionParameters(
		connection_info["server"], connection_info["port"], '/', credentials))
	channel = connection.channel()

	channel.queue_declare(queue=qname)
	channel.basic_consume(callback, queue=qname, no_ack=True)
	print(' [*] Waiting for videos to encode. To exit press CTRL+C')
	channel.start_consuming()


if __name__ == "__main__":
	parser = OptionParser()
	parser.add_option('-c', '--credential', dest='credentialFile',
					help='Path to CREDENTIAL file', metavar='CREDENTIALFILE')
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
