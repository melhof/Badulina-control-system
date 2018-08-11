
import struct

from . import rs485

READ_INPUT_REGISTER = 4 # modbus function

def read_float_32(slave_address, register_address):
    '''
    read 32 bits of data (2 registers)
    as a floating point number
    '''
    no_registers = 2
    data = read_register(slave_address, register_address, no_registers)
    return bytes_to_float_32(data)

def bytes_to_float_32(resp):
    buf = bytearray(resp[3:7])
    floats = struct.unpack('>f', buf)
    return floats[0]

def read_register(slave_address, register_address, no_registers):
    fn = READ_INPUT_REGISTER
    tx_buf = create_payload(slave_address, fn, register_address, no_registers)
    rs485.write(tx_buf)
    read_bytes = 9  # Expected return bytes
    rx_buf = rs485.read(read_bytes)
    return rx_buf

def create_payload(slave_address, function, register_address, no_registers):
    mask = 0xff 
    reg_hi = register_address // mask
    reg_lo = register_address % mask

    nr_hi = no_registers // mask
    nr_lo = no_registers % mask

    payload = [
            slave_address,
            function,
            reg_hi,
            reg_lo,
            nr_hi,
            nr_lo,
    ]
    errc = checksum(bytearray(payload)) 
    for bit in errc:
        payload.append(bit)
    return payload

def checksum(buf):
    '''compute 2 CRC bits from bytearray of 6 byte command
    '''
    checksum = crc16(buf, 6)
    hi = checksum & 0x00ff
    lo = (checksum >> 8) & 0xff
    return (hi, lo)

def crc16(data, no):
    ''' bytearray data, no bytes -> checksum
    '''
    crc = 0xffff
    poly = 0xa001  # Polynomial used for Modbus RS485 applications
    temp = no

    while True:
        crc ^= data[temp - no]
        for i in range(0, 8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ poly
            else:
                crc >>= 1
        no -= 1
        if no == 0:
            break
    return crc & 0xffff

