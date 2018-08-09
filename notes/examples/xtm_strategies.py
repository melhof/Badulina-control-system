
import time
import struct

import serial
import RPi.GPIO as GPIO
import minimalmodbus
from pymodbus.client.sync import ModbusSerialClient

size = 8

BAUD_RATE = 9600
TIME_OUT = 0.5  # Default Time Out for RDu Display to respond

DIR_RS485 = 25  # GPIO Pin used for RS485 Driver IC Direction Control (0=Rx, 1=Tx)
DIR_DELAY = 0.005  # Seconds Delay After Setting and Re-setting the Direction GPIO Pin

RX, TX = 0, 1

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)  # Use RPi GPIO numbers
GPIO.setup(DIR_RS485, GPIO.OUT)  # RS485 DIR bit
GPIO.output(DIR_RS485, TX)  # RS485 to transmit mode

class PiSerial(serial.Serial):
    def write(self, *args, **kwargs):
        super().write(*args, **kwargs)
    def read(self, *args, **kwargs):
        super().read(*args, **kwargs)

class ModbusClient(ModbusSerialClient):
    #TODO try gpio pinsetting here to see if it works
    def _send(self, *args, **kwargs):
        GPIO.output(DIR_RS485, TX)
        time.sleep(DIR_DELAY)
        super()._send(*args, **kwargs)

    def _recv(self, *args, **kwargs):
        time.sleep(
            DIR_DELAY*10
        )
        time.sleep(DIR_DELAY)
        GPIO.output(DIR_RS485, RX)
        super()._recv(*args, **kwargs)


def test_all(addr=30001):
    cmd = '01 04 00 00 00 02 71 cb'  # read 30001
    #'01 03 75 31 00 01 CF C9'

    #print(read_volts(1, cmd))

    try:
        print(mmb(1).read_float(addr))
    except Exception as err:
        print(err)

    time.sleep(1)
    try:
        print(mmb_serial(1, cmd))
    except Exception as err:
        print(err)

    time.sleep(1)
    print(mb().read_input_registers(addr, unit=1))


def mmb(slave):
    print('minimalmodbus')
    instrument = minimalmodbus.Instrument('/dev/ttyS0', slave)
    instrument.serial.baudrate = 9600
    instrument.debug = True
    return instrument


def mmb_serial(slave, cmd):
    instrument = mmb(slave)

    GPIO.output(DIR_RS485, TX)

    tx_buf = parse_cmd(cmd)

    time.sleep(DIR_DELAY)
    instrument.serial.write(tx_buf)
    time.sleep(DIR_DELAY)
    GPIO.output(DIR_RS485, RX)

    return instrument.serial.read_all()


def mb():
    print('pymodbus:')
    modbus = ModbusClient(
        method='rtu', port='/dev/ttyS0', baudrate=9600, timeout=1)
    modbus.connect()
    return modbus


def parse_cmd(cmd):
    return [int(x, base=16) for x in cmd.split()]

def resp_to_float(resp):
    buf = bytearray(resp[3:7])
    floats = struct.unpack('>f', buf)
    return floats[0]

def getr(hi, low):
    base = '01 04 {} {} 00 02'
    high = hexify(hi)
    low = hexify(low)
    return read_float(base.format(high, low))

def hexify(n):
    return ("0x%0.2X" % n)[2:]

def scan():
    ret = []
    for idx in range(0, 0xff, 2):
         val = getr(idx)
         if val != 0.0:
             ret.append((idx, val)) 
    return ret

def sample(name):
    ''' get param from electrical meter 1
    '''
    low = {
        'volts' : 0 ,
        'amps'  : 8 ,
        'watts' : 18,
        'pf'    : 42,
        'hz'    : 54,
    }
    high = {
        'kwh'   : 0 ,
    }
    if name in low:
        value = getr(0, low[name])
    elif name in high:
        value = getr(1, high[name])
    else:
        raise Exception('bad name: {}!'.format(name))
    return value

def read_float(cmd):
    tx_buf = parse_cmd(cmd)
    errc = crc(bytearray(tx_buf)) 
    for bit in errc:
        tx_buf.append(bit)
    print('tx: ',tx_buf)

    rs485 = serial.Serial("/dev/ttyS0")
    rs485.timeout = .1

    GPIO.output(DIR_RS485, TX)  # Set Direction Control to Tx

    time.sleep(DIR_DELAY)  # 10 mSec delay to settle TX Line
    rs485.write(bytearray(tx_buf))
    time.sleep(
        DIR_DELAY*10
    )  # 50 mSec Delay to allow last byte of Checksum and character delay

    GPIO.output(DIR_RS485, RX)  # Set Direction Control to Rx

    read_bytes = 9  # Expected return bytes
    rx_buf = rs485.read(read_bytes)

    rs485.flushInput()  # Flush the seriel Input buffer
    rs485.close()  # Close the port
    print('rx :',rx_buf)

    return resp_to_float(rx_buf)

def _crc16(data, no):
    ''' bytearray data, no bytes -> checksum
    '''
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

def crc(buf):
    '''compute 2 CRC bits from bytearray of 6 byte command
    '''
    checksum = _crc16(buf, 6)
    hi = checksum & 0x00ff
    lo = (checksum >> 8) & 0xff
    return (hi, lo)

