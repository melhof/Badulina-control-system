
import time

from widgetlords.pi_spi_din import *
from widgetlords import *

init()
inputs = Mod8AI(ChipEnable.CE0)

def sample(i):
    counts = inputs.read_single(i)
    voltage = counts_to_value(counts, 0, 4095, 0, 6.6 )
    print("Input %s = %4d AD Counts, %0.2f VDC" % (i, counts, voltage))
    return voltage

def poll():
    while True:
        for i in range(8):
            sample(i)
        time.sleep(0.1)
        print(chr(27) + "[2J")

