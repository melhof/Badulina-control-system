
import serial

import RPi.GPIO as GPIO

DIR_RS485 = 25
RX, TX = 0,1

size = 8

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)         # Use RPi GPIO numbers
GPIO.setup(DIR_RS485,GPIO.OUT) # RS485 DIR bit
GPIO.output(DIR_RS485, TX)     # RS485 to transmit mode

rs = serial.Serial('/dev/ttyS0')

def send(idx, relay_on):
    cmd = bytearray([0xFF, idx+1, relay_on])
    rs.write(cmd)
    
def turn_on(idx):
    send(idx, True)

def turn_off(idx):
    send(idx, False)

def reset():
    for i in range(size):
        turn_off(i)
