'''
SPI-DIN-Mod4KO relay driver
'''

from widgetlords import pi_spi_din as psd

size = 4

psd.init()
relays = psd.Mod4KO(psd.ChipEnable.CE3)

def send(idx, relay_on):
    relays.write_single(idx, relay_on)

def turn_on(idx):
    send(idx, True)

def turn_off(idx):
    send(idx, False)

def reset():
    relays.write(0)
