'''
This module encapsulates domain logic:
    safety restraints
    knowledge about irrigation hardware configuration
'''

import requests

from utils import now, freq

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

from models import db, Relay, SensorReading, WateringEvent

def add_schedule(day, start, stop, valves):
    assert day in range(7), 'MUST BE A VALID DAY'
    assert stop > start, 'START MUST PRECEDE STOP'
    assert len(valves) > 0, 'AT LEAST ONE VALVE MUST BE OPEN'

    event = WateringEvent.create(day, start, stop, valves)
    db.session.add(event)
    db.session.commit()

def remove_schedule(id):
    event = WateringEvent.query.get(id)
    db.session.delete(event)
    db.session.commit()

def seed_db():
    drivers = [('kmt', 8), ('mod4ko', 4)]
    for driver, size in drivers:
        for i in range(size):
            db.session.add(Relay(board=driver, idx=i, is_on=False))
    db.session.commit()
    return

def sample_flow_rate():
    channel = 0
    sample_hz = 300
    n_samples = 1000
    return freq(mod8di.build(channel, sample_hz, n_samples), sample_hz)

def current_flow_rate():
    return requests.get('http://192.168.1.147:1880/flow_meter/').json()['freq']

def record_flow_rate():
    time = now()

    if PI:
        rate = sample_flow_rate()
    else:
        rate = current_flow_rate()

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

def reset():
    if PI:
        for driver in drivers.values():
            driver.reset()
    Relay.query.update(dict(is_on=False))
    db.session.commit()

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
