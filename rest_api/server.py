#!/usr/bin/env python3
from flask import Flask, jsonify, abort
from flask import make_response, request, url_for, render_template
from werkzeug import secure_filename
import uuid
from datetime import datetime
from copy import copy

app = Flask(__name__)

ALLOWED_EXTENSIONS = set(['mkv'])

movies = [{'title':'movie1'},
            {'title':'movie2'},
            {'title':'movie3'},
            {'title':'movie4'}]
jobs_id = {}

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
    #return jsonify([make_public_movie(movie) for movie in movies])
    return render_template('upload.html')


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
