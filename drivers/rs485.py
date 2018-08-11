'''
encapsulate the rs485 electrical interface
as provided to the raspberry pi UART pins
via the widgetlords SPI-DIN board
'''

import serial
import time
import RPi.GPIO as GPIO

DIR_RS485 = 25
DIR_DELAY = 0.005       # Seconds Delay After Setting and Re-setting the Direction GPIO Pin
RX, TX = 0,1

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)         # Use RPi GPIO numbers
GPIO.setup(DIR_RS485,GPIO.OUT) # RS485 DIR bit

timeout = .1

rs = serial.Serial('/dev/ttyS0', timeout=timeout)

def write(buf, delay=None):
    GPIO.output(DIR_RS485, TX)     # RS485 to transmit mode
    time.sleep(DIR_DELAY)
    rs.write(buf)
    if delay is None:
        delay = len(buf)
    time.sleep(DIR_DELAY * delay)

def read(n_bytes):
    GPIO.output(DIR_RS485, RX)  # Set Direction Control to Rx
    response = rs.read(n_bytes)
    return response

