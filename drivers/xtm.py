
import struct

import rs485

volts = lambda slave: sample(slave, 'volts')
amps  = lambda slave: sample(slave, 'amps')
watts = lambda slave: sample(slave, 'watts')
pf    = lambda slave: sample(slave, 'pf')
hz    = lambda slave: sample(slave, 'hz')
kwh   = lambda slave: sample(slave, 'kwh')

def sample(slave, name):
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
        value = getr(slave, 0, low[name])
    elif name in high:
        value = getr(slave, 1, high[name])
    else:
        raise Exception('bad name: {}!'.format(name))
    return value

def getr(slave, hi, low):
    base = '{} 04 {} {} 00 02'
    high = hexify(hi)
    low = hexify(low)
    cmd = base.format(slave, high, low)
    return read_float(cmd)

def hexify(n):
    return ("0x%0.2X" % n)[2:]

def parse_cmd(cmd):
    return [int(x, base=16) for x in cmd.split()]

def resp_to_float(resp):
    buf = bytearray(resp[3:7])
    floats = struct.unpack('>f', buf)
    return floats[0]

def scan():
    ret = []
    for idx in range(0, 0xff, 2):
         val = getr(idx)
         if val != 0.0:
             ret.append((idx, val)) 
    return ret


def read_float(cmd):
    tx_buf = parse_cmd(cmd)
    errc = crc(bytearray(tx_buf)) 
    for bit in errc:
        tx_buf.append(bit)
    print('tx: ',tx_buf)

    rs485.write(tx_buf)

    read_bytes = 9  # Expected return bytes
    rx_buf = rs485.read(read_bytes)

    print('rx :',rx_buf)

    return resp_to_float(rx_buf)

#def read_float_orig(cmd):
    #tx_buf = parse_cmd(cmd)
    #errc = crc(bytearray(tx_buf)) 
    #for bit in errc:
        #tx_buf.append(bit)
    #print('tx: ',tx_buf)

    #rs485 = serial.Serial("/dev/ttyS0")
    #rs485.timeout = .1

    #GPIO.output(DIR_RS485, TX)  # Set Direction Control to Tx

    #time.sleep(DIR_DELAY)  # 10 mSec delay to settle TX Line
    #rs485.write(bytearray(tx_buf))
    #time.sleep(
        #DIR_DELAY*10
    #)  # 50 mSec Delay to allow last byte of Checksum and character delay

    #GPIO.output(DIR_RS485, RX)  # Set Direction Control to Rx

    #read_bytes = 9  # Expected return bytes
    #rx_buf = rs485.read(read_bytes)

    #rs485.flushInput()  # Flush the seriel Input buffer
    #rs485.close()  # Close the port
    #print('rx :',rx_buf)

    #return resp_to_float(rx_buf)

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

