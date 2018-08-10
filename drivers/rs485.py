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

ID = 4 # id-select-switches currently toggled for ID4

stat_byte = 0xA0
byte1 = 0xFF

timeout = 1

def write(buf):
    rs = serial.Serial('/dev/ttyS0', timeout=timeout)
    GPIO.output(DIR_RS485, TX)     # RS485 to transmit mode
    rs.write(buf)

def read(n_bytes):
    rs = serial.Serial('/dev/ttyS0', timeout=timeout)
    GPIO.output(DIR_RS485, RX)  # Set Direction Control to Rx
    response = rs.read(n_bytes)
    return response

from drivers.xtm import crc

def status():
    GPIO.output(DIR_RS485, TX)     # RS485 to transmit mode
    rs = serial.Serial('/dev/ttyS0', timeout=timeout)
    time.sleep(DIR_DELAY)

    stat_byte = 0xA0
    cmd = [0] * 6
    cmd[0] = 0xFF
    cmd[1] = stat_byte + ID
    cmd[2] = 0x00

    errc = crc(bytearray(cmd)) 
    for bit in errc:
        cmd.append(bit)

    cmd = bytearray(cmd)

    rs.write(cmd)
    time.sleep(DIR_DELAY)

    GPIO.output(DIR_RS485, RX)  # Set Direction Control to Rx
    response = rs.read(8)
    return response

