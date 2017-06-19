#!flask/bin/python
from flask import Flask, jsonify, abort
from flask import make_response, request, url_for
import uuid
from datetime import datetime
from copy import copy

app = Flask(__name__)

movies = [{'title':'movie1'},
            {'title':'movie2'},
            {'title':'movie3'},
            {'title':'movie4'}]
jobs_id = {}

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


def make_public_movie(movie):
    new_movie = copy(movie)
    if 'uri' not in movie.keys():
        new_movie['uri'] = url_for('get_encoded_movie', movie=movie['title'], _external=True)

    return new_movie


@app.route('/api/v1/movies', methods=['GET'])
def get_movies():
    return jsonify([make_public_movie(movie) for movie in movies])


@app.route('/api/v1/movies/<movie>', methods=['GET'])
def get_encoded_movie(movie):

    movie_exist = False
    for entry in movies:
        if entry['title'] == movie:
            movie_exist = True
            break

    if not movie_exist:
        not_found()

    # Create job
    id = uuid.uuid4().hex
    job = {"input": url_for("get_encoded_movie", movie = movie),
           "status": "PENDING",
           "start": datetime.now()}
    jobs_id[id] = job

    #TODO:Post to queue

    #URI to the newly created job
    resp = make_response(("", 201))
    resp.headers['location'] = url_for("get_job_status", id = id)
    return resp


@app.route('/api/v1/jobs/<id>', methods=['GET'])
def get_job_status(id):
    job = jobs_id[id]

    # This should propably be its own Process/Worker
    delta = datetime.now() - job["start"]
    if delta.total_seconds() > 2:
        job["status"] = "DONE"

    job = jobs_id[id]

    status_dict = copy(job)
    status_dict["resource"] = "null"
    status_dict["resolution"] = "success" if job["status"] == "DONE" else "null"

    return make_response(jsonify(status_dict))


if __name__ == '__main__':
    app.run(debug=True)
