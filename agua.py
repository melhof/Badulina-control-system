
import datetime
import pytz

def now():
    return datetime.datetime.utcnow().replace(tzinfo=pytz.utc)

try:
    from drivers import kmt, mod4ko, mod8di
    PI = True
    drivers = {
        'kmt': kmt,
        'mod4ko': mod4ko,
    }
except:
    PI = False
    drivers = ['kmt', 'mod4ko']

from models import db, Relay, SensorReading 


def seed_db():
    drivers = [('kmt', 8), ('mod4ko', 4)]
    for driver, size in drivers:
        for i in range(size):
            db.session.add(Relay(board=driver, idx=i, is_on=False))
    db.session.commit()
    return


def offset(lst):
    return zip(lst, lst[1:])

def freq(signal, fs):
    idx = [i for i, (a,b) in enumerate(offset(signal)) if (a,b) == (0,1)]
    diff = [b-a for a,b in offset(idx)]
    if diff:
        mean = sum(diff) / len(diff)
        return fs / mean
    else:
        return 0

def get_flow_rate():
    channel = 0
    sample_hz = 300
    n_samples = 1000
    return freq(mod8di.build(channel, sample_hz, n_samples), sample_hz)

def record_flow_rate():
    time = now()
    rate = get_flow_rate()
    db.session.add(SensorReading(board='mod8di', idx=0, data=rate, time=time))
    db.session.commit()
    return

def set_relay(board, idx, value):
    relay = Relay.query.filter_by(board=board, idx=idx).one()
    if PI:
        drivers[board].send(idx, value)
    else:
        print('NOT PI: faking {}[{}] to {}'.format(board, idx, value))
    relay.is_on = value
    db.session.add(relay)
    db.session.commit()
    return

def turn_pump_on():
    pump = Relay.query.filter_by(board='mod4ko', idx=0).one()
    if not pump.is_on:
        assert Relay.query.filter_by(board='kmt', is_on=False).count() < 8
        if PI:
            drivers['mod4ko'].turn_on(0)
        pump.is_on = True
        db.session.add(pump)
        db.session.commit()
    return

def turn_pump_off():
    pump = Relay.query.filter_by(board='mod4ko', idx=0).one()
    if pump.is_on:
        pump.is_on = False
        if PI:
            drivers['mod4ko'].turn_off(0)
        db.session.add(pump)
        db.session.commit()
    return

def turn_valve_on(idx):
    valve = Relay.query.filter_by(board='kmt', idx=idx).one()
    if not valve.is_on:
        if PI:
            drivers['kmt'].turn_on(idx)
        valve.is_on = True
        db.session.add(valve)
        db.session.commit()
    return

def turn_valve_off(idx):
    valve = Relay.query.filter_by(board='kmt', idx=idx).one()
    if valve.is_on:
        pump = Relay.query.filter_by(board='mod4ko', idx=0).one()
        if pump.is_on:
            assert Relay.query.filter_by(board='kmt', is_on=False).count() < 7
        if PI:
            drivers['kmt'].turn_off(idx)
        valve.is_on = False
        db.session.add(valve)
        db.session.commit()
    return
