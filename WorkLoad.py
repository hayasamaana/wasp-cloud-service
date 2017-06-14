import requests
from numpy.random import exponential

SERVICE_URL = 'http://localhost:5000'


class State:
    THINKING = 0
    WAITING = 1


class WLGenerator:
    # http://docs.python-requests.org/en/latest/api/#requests.Response
    def __init__(self, n, t):
        self.users = [User(t) for _ in range(n)]
        print(self.get_video_list())
        self.request_convertion(1)

    def run_wg(self):
        return None

    def get_video_list(self):
        r = requests.get(SERVICE_URL + u'/api/v1/movies')
        return r.status_code

    def request_convertion(self, video_id):
        r = requests.get(SERVICE_URL + u'/api/v1/movies/' + str(video_id))
        print(r.url)


class User:
    def __init__(self, think_time_constant):
        self.think_time_constant = think_time_constant
        self.think_time = exponential(1.0/self.think_time_constant)
        self.STATE = State.THINKING

    def get_new_think_time(self):
        if self.STATE == State.THINKING:
            self.think_time = exponential(1.0/self.think_time_constant)

        return self.think_time

    def set_state(self, state):
        self.STATE = state


if __name__ == '__main__':
    WG = WLGenerator(10, 1)
    WG.run_wg()
