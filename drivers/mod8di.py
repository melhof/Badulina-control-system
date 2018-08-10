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
    for _ in range(n_samples):
        ret.append(inputs.read_single(channel))
        time.sleep(interval)
    return ret

def build_with_timing(channel, hz, n_samples):
    '''sample channel at freq (in hz), and return turn of (n_samples, total time taken)
    '''
    start = time.perf_counter()
    ret = build(channel, hz, n_samples)
    end = time.perf_counter()

    total_time = end - start
    actual_hz = n_samples / total_time
    print('attempted hz: {}, actual hz: {}, ratio: {}'.format(hz, actual_hz, actual_hz/hz))

    return ret, total_time
