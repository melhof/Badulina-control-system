#! /usr/bin/python3
from time import sleep
from widgetlords.pi_spi_din import *

init()
relays = Mod4KO(ChipEnable.CE3)

def tick():
    relays.write(0x1)
    sleep(1)
    relays.write(0x0)
    sleep(1)
    
def main():
    while True:
        tick()


if __name__ == '__main__':
    main()
