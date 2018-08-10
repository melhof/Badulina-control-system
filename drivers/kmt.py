'''
Driver for KMTRonic RS485 Relay
the board has 8 relays and a status command
'''
from . import rs485

size = 8 # no. relays

ID = 4 # id-select-switches currently toggled for ID4

stat_byte = 0xA0
byte1 = 0xFF

def status():
    byte2 = stat_byte + ID
    byte3 = 0x00

    cmd = bytearray([byte1, byte2, byte3])
    rs485.write(cmd)
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
