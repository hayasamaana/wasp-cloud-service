import requests
from multiprocessing import Process, Queue
import os, time, signal, sys
from random import choice, expovariate
import logging
import shutil


SERVICE_URL = 'http://localhost:5000'


def signal_handler(signal, frame):
        print('Process {} You pressed Ctrl+C! Quitting simulation.'.format(os.getpid()))
        sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)


class WLGenerator:

    def __init__(self, host, n_users, think_time, poll_time = 1., timeout = 2.):
        self.host = host
        self.n_users = n_users
        self.think_time = think_time
        self.poll_time = poll_time
        self.timeout = timeout

    def run_wg(self):
        ps = []
        for _ in range(self.n_users):
            p = Process(target=User, args=(self.host, self.think_time, self.poll_time, self.timeout))
            p.start()
            ps.append(p)

        for p in ps:
            p.join()


class User:
    # http://docs.python-requests.org/en/latest/api/#requests.Response
    # http://docs.python-guide.org/en/latest/writing/logging/
    # https://docs.python.org/3.6/library/logging.html
    # https://stackoverflow.com/questions/303200/how-do-i-remove-delete-a-folder-that-is-not-empty-with-python#303225

    def __init__(self, host, think_time, poll_time = 1., timeout = 2.):
        self.pid = os.getpid()
        self._set_up_logger(self.pid)
        self.host = host
        self.think_time = think_time
        self.poll_time = poll_time
        self.timeout = timeout
        self.log.info('{}'.format(self.pid))
        self.run()

    def _set_up_logger(self, pid):
        self.log = logging.getLogger("Process{}".format(self.pid))

        formatter = logging.Formatter(
        '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')

        file_handle = logging.FileHandler('logs/process{}.log'.format(self.pid))
        handler = logging.StreamHandler()

        handler.setFormatter(formatter)
        file_handle.setFormatter(formatter)

        self.log.addHandler(handler)
        self.log.addHandler(file_handle)
        self.log.setLevel(logging.DEBUG)

    def run(self):
        while True:
            try:
                t = expovariate(1.0/self.think_time)
                self.log.info('sleeping for {} seconds'.format(t))
                time.sleep(t)

                self.send_request_to_server()

            except requests.exceptions.HTTPError as e:
                self.log.error(e)

    def send_request_to_server(self):
        #Send request for available movies
        r = requests.get(self.host + '/api/v1/movies', timeout = self.timeout)
        r.raise_for_status()

        movie_uri = self.random_choice_movie(r.json())

        r = requests.get(movie_uri, timeout = self.timeout)
        self.log.info("Requested {} for conversion, response {}".format(movie_uri, r.status_code))
        r.raise_for_status()

        job_uri = r.headers['location']

        #Poll job status
        while True:
            time.sleep(self.poll_time)
            self.log.debug('Polling job status')
            r = requests.get(job_uri, timeout = self.timeout)
            r.raise_for_status()
            status_msg = r.json()

            if status_msg['resolution'] != "null":
                self.log.info("Requested finished : resolution {}".format(status_msg['resolution']))
                break


    def random_choice_movie(self, movie_list):
        movie_uris = []
        for movie in movie_list:
            movie_uris.append(movie['uri'])

        return choice(movie_uris)


if __name__ == '__main__':

    log_path = 'logs'
    if os.path.exists(log_path):
        shutil.rmtree(log_path, ignore_errors=True)

    os.mkdir(log_path)

    WG = WLGenerator(SERVICE_URL, 2, 1)
    WG.run_wg()
