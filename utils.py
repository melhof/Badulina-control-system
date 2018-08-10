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
