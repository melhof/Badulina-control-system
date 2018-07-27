import time

from widgetlords.pi_spi_din import init, Mod8DI, ChipEnable

init()
inputs = Mod8DI(ChipEnable.CE2)


def sample(i):
    return inputs.read_single(i)


def build(channel, hz, n_samples):
    '''sample channel at freq (in hz), and return array of n_samples
    '''
    ret = []
    interval = 1 / hz
    start = time.perf_counter()
    for _ in range(n_samples):
        ret.append(inputs.read_single(channel))
        time.sleep(interval)
    end = time.perf_counter()
    actual = n_samples / (end - start)
    print('attempted hz: {}, actual hz: {}, ratio: {}'.format(hz, actual, actual/hz))
    return ret
