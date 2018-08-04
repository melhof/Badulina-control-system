'''
This module provides miscelaneous utility funtions
'''

import datetime
import pytz

def now():
    '''get current spanish time
    '''
    return datetime.datetime.now().replace(tzinfo=pytz.timezone('Europe/Madrid'))

def offset(lst):
    '''eg:
        >>> list(offset([1,2,3,4])) == [(1,2), (2,3), (3,4)]
    '''
    return zip(lst, lst[1:])

def freq(signal, hz):
    '''calculate frequency of square wave
    '''
    idx = [i for i, (a,b) in enumerate(offset(signal)) if (a,b) == (0,1)]
    diff = [b-a for a,b in offset(idx)]
    if diff:
        mean = sum(diff) / len(diff)
        return hz / mean
    else:
        return 0


