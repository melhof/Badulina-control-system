
import time

import serial
import RPi.GPIO as GPIO

size = 8 # no. valves

# pi config

DIR_RS485 = 25
DIR_DELAY = 0.005       # Seconds Delay After Setting and Re-setting the Direction GPIO Pin
RX, TX = 0,1

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)         # Use RPi GPIO numbers
GPIO.setup(DIR_RS485,GPIO.OUT) # RS485 DIR bit

GPIO.output(DIR_RS485, TX)     # RS485 to transmit mode

# kmt config
ID = 4 # id select switch config
stat_byte = 0xA0

byte1 = 0xFF

def status():
    rs = serial.Serial('/dev/ttyS0')
    rs.timeout = 1

    byte2 = stat_byte + ID
    byte3 = 0x00

    cmd = bytearray([byte1, byte2, byte3])
    rs.write(cmd)
    time.sleep(DIR_DELAY)  # delay to settle TX Line

    GPIO.output(DIR_RS485, RX)  # Set Direction Control to Rx
    response = rs.read(8)

    GPIO.output(DIR_RS485, TX)  # default RS485 to transmit mode
    return response

def send(idx, relay_on):
    rs = serial.Serial('/dev/ttyS0')

    id_offset = (ID - 1) * 8
    byte2 = idx + 1 + id_offset
    byte3 = relay_on

    cmd = bytearray([byte1, byte2, byte3])
    rs.write(cmd)
    
def turn_on(idx):
    send(idx, True)

def turn_off(idx):
    send(idx, False)

def reset():
    for i in range(size):
        turn_off(i)
