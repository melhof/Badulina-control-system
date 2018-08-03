'''
This module provides miscelaneous utility funtions
'''

import datetime
import pytz

def now():
    return datetime.datetime.utcnow().replace(tzinfo=pytz.utc)

def time_from_str(string):
    return datetime.time(*map(int, string.split(':')))


