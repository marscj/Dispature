import os
import random
import string
import datetime

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
