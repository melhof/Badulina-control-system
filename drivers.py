'''
ON
FF 01 01
FF 02 01
FF 03 01
FF 04 01
FF 05 01
FF 06 01
FF 07 01
FF 08 01

OFF
FF 01 00
FF 02 00
FF 03 00
FF 04 00
FF 05 00
FF 06 00
FF 07 00
FF 08 00

stat
FF A1 00
'''


import RPi.GPIO as GPIO
import time
import sys
import serial

from widgetlords import pi_spi_din as psd

class Mod4KO:
    def __init__(self):
        psd.init()
        self.relays = psd.Mod4KO(psd.ChipEnable.CE3)
        self.size = 4
        self.state = [False] * self.size

    def _send(self, idx, relay_on):
        self.state[idx] = relay_on
        msg = 0
        for i,r in enumerate(self.state):
            msg |= r << i
        self.relays.write(msg)

    def on(self, idx):
        self._send(idx, True)

    def off(self, idx):
        self._send(idx, False)

def tick():
    relays.write(0x1)


DIR_RS485 = 25
DIR_DELAY = 0.005

RX, TX = 0,1

class KMTronic:
    def __init__(self):
        self.size = 8
        GPIO.setmode(GPIO.BCM)  # Use RPi GPIO numbers
        GPIO.setup(DIR_RS485,GPIO.OUT)     # RS485 DIR bit

    def _send(self, idx, relay_on):
        rs = serial.Serial("/dev/ttyS0")
        GPIO.output(DIR_RS485, TX)
        time.sleep(DIR_DELAY) # let TX settle
        cmd = bytearray([0xff, idx+1, relay_on])
        rs.write(cmd)
        rs.close()

    def on(self, idx):
        self._send(idx, True)

    def off(self, idx):
        self._send(idx, False)


