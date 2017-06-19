import requests
from multiprocessing import Process, Queue
import os, time
from numpy.random import exponential, choice
import logging


SERVICE_URL = 'http://localhost:5000'


class WLGenerator:
    # http://docs.python-requests.org/en/latest/api/#requests.Response
    # http://docs.python-guide.org/en/latest/writing/logging/
    def __init__(self, host, n_users, think_time):
        self.host = host
        self.n_users = n_users
        self.think_time = think_time

    def run_wg(self):
        ps = []
        for _ in range(self.n_users):
            u = User(self.host, self.think_time)
            u.start()
            ps.append(u)

        for p in ps:
            p.join()


class User(Process):
    def __init__(self, host, think_time, timeout = 2):
        super(Process, self).__init__()
        self.log = logging.getLogger("Process ID {}".format(os.getpid()))
        self.host = host
        self.think_time = think_time
        self.timeout = timeout

    def run(self):
        while True:
            try:
                self.send_request_to_server()
            except requests.exceptions.HTTPError as e:
                self.log = ""
                # Store http errors and try again
                #self.log.error(e)

    def send_request_to_server(self):
        time.sleep(exponential(1.0/self.think_time))

        #Send request for available movies
        r = requests.get(self.host + '/api/v1/movies', timeout = self.timeout)
        r.raise_for_status()

        movie_uri = self.random_choice_movie(r.json())

        r = requests.get(movie_uri, timeout = self.timeout)
        #self.log.info("Requested {} for conversion, response {}".format(my_video, r.status_code))
        r.raise_for_status()

        job_uri = r.headers['location']

        #Poll for status
        while True:
            time.sleep(0.1)
            #self.log.debug("Requesting status after {} seconds of wait".format(self.poll_wait))
            r = requests.get(job_uri, timeout = self.timeout)
            r.raise_for_status()
            status_msg = r.json()

            if status_msg['resolution'] != "null":
                #self.log.info("Requested finished with resolution {}".format(status_msg['resolution']))
                break


    def random_choice_movie(self, movie_list):
        movie_uris = []
        for movie in movie_list:
            movie_uris.append(movie['uri'])

        return choice(movie_uris)



if __name__ == '__main__':
    WG = WLGenerator(SERVICE_URL, 10, 1)
    WG.run_wg()
