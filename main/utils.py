import os
import random
import string
import datetime
from django.utils.crypto import get_random_string

class Tools(object):

    @staticmethod
    def get_code():
        return ''.join(random.sample(string.ascii_letters + string.digits, 4))

    @staticmethod
    def get_year():
        YEAR_CHOICES = []
        for r in range(2000, (datetime.datetime.now().year + 1)):
            YEAR_CHOICES.append((r, r))

        return YEAR_CHOICES

    @staticmethod
    def get_nickname():
        return '用户' + get_random_string(length=6, allowed_chars='0123456789')

    
    @staticmethod
    def my_round(value, max):
        if value == 0:
            return 0
        if value > max :
            return 1.0
        else:
            return 0.5

    @staticmethod
    def convert_timedelta(duration,format):
        # days, seconds = duration.days, duration.seconds
        # hours = (days * format + seconds // 3600) % format
        # minutes = (seconds % 3600) // 60
        # seconds = (seconds % 60)

        days, seconds = duration.days, duration.seconds
        hours = Tools.my_round((seconds // 3600) % 24 , 5)
        return days + hours