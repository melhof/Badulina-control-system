'''
This module provides miscelaneous utility funtions
'''

import datetime
import pytz

def now():
    return datetime.datetime.now().replace(tzinfo=pytz.timezone('Europe/Madrid'))

def time_from_str(string):
    return datetime.time(*map(int, string.split(':')))

def offset(lst):
    return zip(lst, lst[1:])

def freq(signal, hz):
    idx = [i for i, (a,b) in enumerate(offset(signal)) if (a,b) == (0,1)]
    diff = [b-a for a,b in offset(idx)]
    if diff:
        mean = sum(diff) / len(diff)
        return hz / mean
    else:
        return 0


