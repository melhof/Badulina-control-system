
import serial
import RPi.GPIO as GPIO
import time

size = 8

BAUD_RATE = 9600
TIME_OUT = 0.5            # Default Time Out for RDu Display to respond

DIR_RS485 = 25          # GPIO Pin used for RS485 Driver IC Direction Control (0=Rx, 1=Tx)
DIR_DELAY = 0.005       # Seconds Delay After Setting and Re-setting the Direction GPIO Pin

RX, TX = 0,1

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

rs = serial.Serial("/dev/ttyS0")
def write(cmd):
    GPIO.output(DIR_RS485, TX)                # Set Direction Control to Tx
    time.sleep(DIR_DELAY)                   # 50 mSec Delay to allow last byte of Checksum and character delay
    rs.write(cmd)

def stat(n):
    cmd = bytearray([0xFF, 0xa4, 0x00])

    GPIO.output(DIR_RS485, TX)                # Set Direction Control to Tx

    time.sleep(DIR_DELAY)                   # 10 mSec delay to settle TX Line
    rs.write(cmd)
    time.sleep(DIR_DELAY)                   # 10 mSec delay to settle TX Line

    GPIO.output(DIR_RS485, RX)                # Set Direction Control to Rx
    return rs.read(n)

import minimalmodbus
def mmb(slave):
    instrument = minimalmodbus.Instrument('/dev/ttyS0', slave)
    instrument.serial.baudrate = 9600
    instrument.debug = True
    return instrument
    GPIO.output(DIR_RS485, TX)     # RS485 to transmit mode
    cmd = bytearray([0x01,0x03,0x75,0x31,0x00,0x01,0xCF,0xC9])
    time.sleep(DIR_DELAY)                   # 10 mSec delay to settle TX Line
    instrument.serial.write(cmd)
    time.sleep(DIR_DELAY)                   # 10 mSec delay to settle TX Line
    GPIO.output(DIR_RS485, RX)     # RS485 to transmit mode
    print(instrument.serial.read_all())
    return instrument
    #.serial.read_all()

from pymodbus.client.sync import ModbusSerialClient as ModbusClient
def mb(addr, unit):
    modbus = ModbusClient(method='rtu', port='/dev/ttyS0', baudrate=9600, timeout=1)
    return modbus
    return modbus.read_input_registers(addr, unit=unit)


def read_volts(modbus_id, cmd):
    #cmd = '01 04 00 00 00 02 71 cb'
    #cmd = '01 03 75 31 00 01 CF C9'
    status = [0] * 2
    tx_buf = [int(x,base=16) for x in cmd.split()]

    foo = [
        modbus_id, #slave addr
        4, #fn 
        0,
        0,
        0,
        2,
        0x71, #CRC
        0xcb,
    ]
    
    rs485 = serial.Serial("/dev/ttyS0")

    GPIO.output(DIR_RS485, TX)                # Set Direction Control to Tx

    time.sleep(DIR_DELAY)                   # 10 mSec delay to settle TX Line
    rs485.write(bytearray(tx_buf))
    time.sleep(DIR_DELAY)                   # 50 mSec Delay to allow last byte of Checksum and character delay

    GPIO.output(DIR_RS485, RX)                # Set Direction Control to Rx

    read_bytes = 7                          # Expected return bytes
    rx_buf = []
    for _ in range(read_bytes):
        print(rx_buf)
        rx_buf.append(rs485.read())

    rs485.flushInput()                      # Flush the seriel Input buffer          
    rs485.close()                           # Close the port

    status[0] = _check_receive_buffer(rx_buf, read_bytes)

    if status[0] == 0:                      # Temperature values in Deg C
            status[1] = (rx_buf[3] << 8) + rx_buf[4]
            
    return status

# Calculate CRC16 Checksum
def _crc16(data, no):
    crc = 0xffff
    poly = 0xa001               # Polynomial used for Modbus RS485 applications
    temp = no
    
    while True:
        crc ^= data[temp - no]        

        for i in range(0, 8):
            if crc & 0x0001:
                crc = (crc>>1) ^ poly
            else:
                crc >>= 1
                    
        no -= 1;

        if no == 0:
            break

    return crc & 0xffff                       


def _check_receive_buffer(rx_buf, read_bytes):        

        if len(rx_buf) == 5:                    # Check for "Exception" return from the Display
                return rx_buf[2]                # Returnt he exception value

        if len(rx_buf) != read_bytes:
                return -1                       # Return -1 as a Com Error
        
        if len(rx_buf) == read_bytes:
                # Verify Checksums
                checksum_calc = _crc16(bytearray(rx_buf), (read_bytes - 2))
                checksum_read = (rx_buf[read_bytes-1] << 8) + rx_buf[read_bytes-2]

                if checksum_calc != checksum_read:
                        return -2               # Checksum Error                

        return 0


def check_rs485_error(status):

        if status == -1:
            return "Com Error"

        if status == -2:
            return "Checksum Error"

        if status > 0:
            return "Modbus Exception Error "

        return
    

