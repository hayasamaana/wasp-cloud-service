#!/usr/bin/env python3

#https://stackoverflow.com/questions/9383014/cant-import-my-own-modules-in-python
import sys
sys.path.append("../")

from flask import Flask, jsonify, abort
from flask import make_response, request, url_for, render_template
from werkzeug import secure_filename
import uuid
from datetime import datetime
from copy import copy
from swiftwrapper.wrapper import SwiftWrapper, ServiceDefaults
from dbwrp import postJob
import pika
import ConfigParser
config = ConfigParser.RawConfigParser()
config.read('../rabbitMQcred.txt')

#Connection to the Queue
rabbitServer=config.get('rabbit', 'server');
rabbitPort=int(config.get('rabbit', 'port'));
rabbitUser=config.get('user1', 'username');
rabbitPassword=config.get('user1', 'password');

#Deciding which qeue we will publish too
rabbitQueue=config.get('rabbit', 'queue');
credentials = pika.PlainCredentials(rabbitUser, rabbitPassword)
connection = pika.BlockingConnection(pika.ConnectionParameters(rabbitServer,rabbitPort,'/',credentials))
channel = connection.channel()
channel.queue_declare(queue=str(rabbitQueue))


app = Flask(__name__)

ALLOWED_EXTENSIONS = set(['mkv'])

'''
movies = [{'title':'movie1'},
            {'title':'movie2'},
            {'title':'movie3'},
            {'title':'movie4'}]
'''
jobs_id = {}

swift_cl = SwiftWrapper()

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def make_public_movie(movie):
    new_movie = copy(movie)
    if 'uri' not in movie.keys():
        new_movie['uri'] = url_for('get_encoded_movie', movie=movie['title'], _external=True)

    return new_movie


@app.route('/api/v1/movies', methods=['POST', 'PUT', 'GET'])
def get_movies():
    if request.method == ['POST', 'PUT']: # or request.method == 'PUT':
        f = request.files['file']

        if f and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            f.save(filename)  # File appears in the directory, should be put on SWIFT
            return jsonify({"message": "file uploaded!"})
        return redirect(url_for('get_movies'))

        # Double checking, this below is indented as "else" to the first if? So, the GET response?
    print("Is this called?")
    movies = swift_cl.list_container(container=ServiceDefaults.DEFAULT_VIDEO_CONTAINER)
    return jsonify([make_public_movie(movie) for movie in movies])


@app.route('/api/v1/movies/<movie>', methods=['GET'])
def get_encoded_movie(movie):

    movie_exist = False
    movies = swift_cl.list_container(container=ServiceDefaults.DEFAULT_VIDEO_CONTAINER)
    print(movies)
    
    #identfying if the specified movie exists
    for entry in movies:
        if entry['title'] == movie:
            movie_exist = True
            break

    if not movie_exist:
        not_found()

    
    # ELSE, the movie exists

    # Create a job
    id = uuid.uuid4().hex
    job = {"input": url_for("get_encoded_movie", movie = movie),
           "status": "PENDING",
           "start": datetime.now()}
    jobs_id[id] = job

    # We post the job to the mongo DB with it's initial status
    dabaseTask = job
    dabaseTask['id'] = id
    postJob(dabaseTask)

    #also, we publish the job in the RabbitMQ queue
    channel.basic_publish(exchange='',
                      routing_key=str(rabbitQueue),
                      body=str(id))

    print("Published: ", str(id))

    #URI to the newly created job
    resp = make_response(("", 201))
    resp.headers['location'] = url_for("get_job_status", id = id)
    #connection.close() #closing the connection to the queue
    return resp


@app.route('/api/v1/jobs/<id>', methods=['GET'])
def get_job_status(id):
    job = jobs_id[id]
    if '_id' in job:
        del job['_id']
    print("Got Job: ", job)

    # This should propably be its own Process/Worker
    delta = datetime.now() - job["start"]
    if delta.total_seconds() > 20:
        job["status"] = "DONE"

    status_dict = copy(job) # what is this copy job? Why? 
    status_dict["resource"] = "null"
    status_dict["resolution"] = "success" if job["status"] == "DONE" else "null"

    return make_response(jsonify(status_dict))


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
