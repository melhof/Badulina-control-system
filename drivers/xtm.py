
from . import modbus

voltage = lambda slave: sample(slave, 'voltage')
current  = lambda slave: sample(slave, 'current')
power = lambda slave: sample(slave, 'power')
phase    = lambda slave: sample(slave, 'phase')
freq    = lambda slave: sample(slave, 'freq')
energy   = lambda slave: sample(slave, 'energy')

def sample(slave, name):
    ''' get param from electrical meter 1
    '''
    addresses = {
        'voltage' : 0 ,
        'current'  : 8 ,
        'power' : 18,
        'phase'    : 42,
        'freq'    : 54,
        'energy'   : 255,
    }
    address = addresses[name]
    return modbus.read_float_32(slave, address)

