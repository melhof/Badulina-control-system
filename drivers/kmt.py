'''
relay drivers

stat
FF A1 00
'''

import time
import serial

import RPi.GPIO as GPIO

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
    cmd = bytearray([0xFF, idx+1, relay_on])
    rs.write(cmd)
    rs.close()
    
def status():
    rs = serial.Serial('/dev/ttyS0')
    GPIO.output(DIR_RS485, TX)
    time.sleep(DIR_DELAY) # let TX settle
    cmd = bytearray([0xFF, 0xA1, 0x00])
    rs.write(cmd)
    time.sleep(DIR_DELAY*10) # let TX settle
    GPIO.output(DIR_RS485, RX)
    stat = rs.read(1)
    rs.close()
    return stat
    
print(status())

def turn_on(idx):
    send(idx, True)

def turn_off(idx):
    send(idx, False)

def reset():
    for i in range(size):
        turn_off(i)
