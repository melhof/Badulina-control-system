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

def signal_to_freq(signal, hz):
    idx = get_idx(signal)
    return idx2freq1(idx, hz)

def get_idx(signal):
    '''calculate frequency of square wave
    '''
    #idx = [i for i, (a,b) in enumerate(offset(signal)) if (a,b) == (0,1)]
    idx = []
    for i, (a,b) in enumerate(offset(signal)):
        if (a,b) == (0,1):
            idx.append(i)
    return idx

def idx2freq1(idx, hz):
    diff = [b-a for a,b in offset(idx)]
    if diff:
        mean = sum(diff) / len(diff)
        return hz / mean
    else:
        return 0

def signal_to_freq_empirical(signal, actual):
    idx = get_idx(signal)
    return len(idx) / actual

