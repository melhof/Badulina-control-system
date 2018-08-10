'''
Driver for Digiten Water Flow Sensor
via widgetlords mod8di digital input
'''

import mod8di
from utils import offset

CHANNEL = 0

def flow_rate(sample_hz, n_samples):
    '''get flow rate from by sampling digital imput D1 in L/s'''
    signal = mod8di.build(CHANNEL, sample_hz, n_samples)
    raw = signal_to_freq(signal, sample_hz)
    return raw

def signal_to_freq(signal, hz):
    idx = get_idx(signal)
    return idx_to_freq(idx, hz)

def get_idx(signal):
    '''
    calculate frequency of square wave
    use offset list to find the 0->1 transitions

    equivalent to:
        idx = [i for i, (a,b) in enumerate(offset(signal)) if (a,b) == (0,1)]
    '''
    idx = []
    for i, (a,b) in enumerate(offset(signal)):
        if (a,b) == (0,1):
            idx.append(i)
    return idx

def idx_to_freq(idx, hz):
    ''' compute freq by taking mean period length in sample
    '''
    diff = [b-a for a,b in offset(idx)]
    if diff:
        mean = sum(diff) / len(diff)
        return hz / mean
    else:
        return 0

# NEXT VERSION:
def melchiors_empirical_flowrate(sample_hz, n_samples):
    # TODO melchior, test this for calibration
    signal, actual = mod8di.build_with_timing(CHANNEL, sample_hz, n_samples)
    rate = signal_to_freq_empirical(signal, actual)
    return rate

def signal_to_freq_empirical(signal, actual):
    idx = get_idx(signal)
    return len(idx) / actual
