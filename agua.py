'''
This module encapsulates domain logic:
    safety restraints
    knowledge about irrigation hardware configuration
'''

import requests
from datetime import time

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

from models import db, Relay, SensorReading, WateringEvent, AppState

def add_schedule(day, start, stop, valves):
    assert stop > start, 'START MUST PRECEDE STOP'
    assert len(valves) > 0, 'AT LEAST ONE VALVE MUST BE OPEN'

    potential_conflicts = WateringEvent.query.filter_by(day=day).all()
    for event in potential_conflicts:
        print(event)

        if start < event.start:
            assert stop < event.start, 'OVERLAP: STOP BEFORE {}'.format(event.start)
        else:
            assert start > event.stop, 'OVERLAP: START AFTER {}'.format(event.stop)

    event = WateringEvent.create(day, start, stop, valves)
    db.session.add(event)
    db.session.commit()

def remove_schedule(id):
    event = WateringEvent.query.get(id)
    if event.in_progress:
        reset()
    db.session.delete(event)
    db.session.commit()

def apply_schedule():
    state = AppState.query.one()

    if state.state != AppState.State.operational:
        print('bypassing')
        return

    moment = now()
    day = WateringEvent.Days(moment.weekday())
    time = moment.time()

    current_task = WateringEvent.query.filter(
        WateringEvent.in_progress==True,
    ).all()
    
    next_task = WateringEvent.query.filter(
        WateringEvent.in_progress==False,
        WateringEvent.day == day,
        WateringEvent.start < time,
        WateringEvent.stop > time,
    ).all()

    if current_task:
        print(current_task)
        assert len(current_task) == 1
        current_task = current_task[0]

        # be carefule w/ midnight behaviour
        should_continue = current_task.day == day and current_task.stop > time
        if not should_continue:
            reset()
            current_task.in_progress = False
            db.session.commit()

    if next_task:
        reset() #this line should be redundant; for safety
        print(next_task)
        assert len(next_task) == 1
        next_task = next_task[0]

        next_task.in_progress = True
        db.session.commit()
        start_watering(next_task)

def start_watering(event):
    for valve in event.valves:
        turn_valve_on(valve)
    turn_pump_on()


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

def suspend():
    state = AppState.query.one()
    state.state = AppState.State.suspended
    db.session.commit()
    reset()

def resume():
    state = AppState.query.one()
    state.state = AppState.State.operational
    db.session.commit()

def reset():
    if PI:
        for driver in drivers.values():
            driver.reset()
    Relay.query.update(dict(is_on=False))
    WateringEvent.query.update(dict(in_progress=False))
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

import click
from flask.cli import with_appcontext

@click.command('agua_init')
@with_appcontext
def agua_init():
    db.create_all()
    drivers = [('kmt', 8), ('mod4ko', 4)]
    db.session.add(AppState(state=AppState.State.operational))
    db.session.add(SensorReading(board='mod8di', idx=0, data=0, time=now()))
    for driver, size in drivers:
        for i in range(size):
            db.session.add(Relay(board=driver, idx=i, is_on=False))
    for day in WateringEvent.Days:
        for valve in WateringEvent.Valves:
            hour = valve + 12
            db.session.add(WateringEvent.create(day,time(hour, 0),time(hour, 59), [valve]))  
    db.session.commit()
    return
