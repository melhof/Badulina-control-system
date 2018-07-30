
try:
    from drivers import kmt, mod4ko
    PI = True
    drivers = {
        'kmt': kmt,
        'mod4ko': mod4ko,
    }
except:
    PI = False
    drivers = ['kmt', 'mod4ko']

from models import Relay, db

def seed_db():
    for driver in drivers:
        for i in range(drivers[driver].size):
            db.session.add(Relay(board=driver, idx=i, is_on=False))
    db.session.commit()

def set_relay(board, idx, value):
    relay = Relay.query.filter_by(board=board, idx=idx).one()
    if PI:
        drivers[board].send(idx, value)
    else:
        print('NOT PI: faking {}[{}] to {}'.format(board, idx, value))
    relay.is_on = value
    db.session.add(relay)
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

def turn_pump_off():
    pump = Relay.query.filter_by(board='mod4ko', idx=0).one()
    if pump.is_on:
        pump.is_on = False
        if PI:
            drivers['mod4ko'].turn_off(0)
        db.session.add(pump)
        db.session.commit()

def turn_valve_on(idx):
    valve = Relay.query.filter_by(board='kmt', idx=idx).one()
    if not valve.is_on:
        if PI:
            drivers['kmt'].turn_on(idx)
        valve.is_on = True
        db.session.add(valve)
        db.session.commit()

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
