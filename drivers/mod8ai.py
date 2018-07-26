
from time import sleep
from widgetlords.pi_spi_din import *

init()
inputs = Mod8AI(ChipEnable.CE0)

def sample():
    return inputs.read_single(0)

def poll()
    while True:
        print(sample())
        sleep(0.5)
