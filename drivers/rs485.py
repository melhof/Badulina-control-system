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

def write(buf):
    GPIO.output(DIR_RS485, TX)     # RS485 to transmit mode
    rs = serial.Serial('/dev/ttyS0', timeout=1)

    rs.write(buf)

    delay = DIR_DELAY * len(buf) # TODO: this is arbitrary. may need configuration with longer bus
    time.sleep(delay)
    rs.close()

def read(n_bytes):
    GPIO.output(DIR_RS485, RX)  # Set Direction Control to Rx
    rs = serial.Serial('/dev/ttyS0', timeout=1)

    response = rs.read(n_bytes)
    rs.close()

    return response


