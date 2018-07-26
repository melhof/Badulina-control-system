
import time

from widgetlords.pi_spi_din import *
from widgetlords import *

init()
inputs = Mod8DI(ChipEnable.CE2)

def sample(i):
    return inputs.read_single(i)

def build(channel, hz, n_samples):
    '''sample channel at freq (in hz), and return array of n_samples
    '''
    ret = []
    interval = 1 / hz
    for _ in range(n_samples):
        ret.append(inputs.read_single(channel))
        time.sleep(interval)
    return ret

