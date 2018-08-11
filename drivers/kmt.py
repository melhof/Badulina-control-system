'''
Driver for KMTRonic RS485 Relay
the board has 8 relays and a status command

note: KMT status seems quite buggy
    (oscilloscope measures noisy response)


'''
from . import rs485

size = 8 # no. relays

ID = 4 # id-select-switches currently toggled for ID4

stat_byte = 0xA0
byte1 = 0xFF

def status():
    '''
    retry when dirty_status is bad
    of 1000 tries:
    994 were correct on second request
    '''
    n_tries = 100
    for _ in range(n_tries):
        msg = dirty_status()
        is_boolean = all(bit in range(2) for bit in msg)
        is_byte = len(msg) == 8
        if is_byte and is_boolean:
            return msg
    raise Exception('cannot get it!')

def dirty_status():
    '''
    has intermittent failures:

    In [83]: status()
    Out[83]: b'\x01\x00\x01\x00\x00\x00\x00\x00'

    In [84]: status()
    Out[84]: b'@@@@\x80\x80\x80\x00'
    '''
    byte2 = stat_byte + ID
    byte3 = 0x00

    cmd = bytearray([byte1, byte2, byte3])
    rs485.write(cmd, delay=1) # NOTE: delay is empirical from observed behavior
    response = rs485.read(8)

    return response

def send(idx, relay_on):
    id_offset = (ID - 1) * 8
    byte2 = idx + 1 + id_offset
    byte3 = relay_on

    cmd = bytearray([byte1, byte2, byte3])
    rs485.write(cmd)
    
def turn_on(idx):
    send(idx, True)

def turn_off(idx):
    send(idx, False)

def reset():
    for i in range(size):
        turn_off(i)
