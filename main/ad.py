from .models import Task

import time
import random


def get_time():
    a1 = (2016, 1, 1, 0, 0, 0, 0, 0, 0)
    a2 = (2018, 12, 31, 23, 59, 59, 0, 0, 0)

    start = time.mktime(a1)
    end = time.mktime(a2)

    t = random.randint(start, end)
    date_touple = time.localtime(t)
    return time.strftime('%Y-%m-%d %H:%M', date_touple)


def setup():
    for i in range(100):
        Task.objects.create(start_point='/', end_point='/',
                            start_time=get_time(), end_time=get_time())
