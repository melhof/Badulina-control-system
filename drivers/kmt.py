'''
relay drivers

stat
FF A1 00
'''

import RPi.GPIO as GPIO
import time
import serial

DIR_RS485 = 25
DIR_DELAY = 0.005
RX, TX = 0,1

size = 8

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)         # Use RPi GPIO numbers
GPIO.setup(DIR_RS485,GPIO.OUT) # RS485 DIR bit

def send(idx, relay_on):
    rs = serial.Serial('/dev/ttyS0')
    GPIO.output(DIR_RS485, TX)
    time.sleep(DIR_DELAY) # let TX settle
    cmd = bytearray([0xff, idx+1, relay_on])
    rs.write(cmd)
    rs.close()

def turn_on(idx):
    send(idx, True)

def turn_off(idx):
    send(idx, False)

def reset():
    for i in range(size):
        turn_off(i)
