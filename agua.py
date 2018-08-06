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

from models import (
    save,
    create_tables,
    Relay,
    SensorReading,
    WateringEvent,
    AppState,
)

def add_schedule(day, start, stop, valves):
    assert stop > start, 'START MUST PRECEDE STOP'
    assert len(valves) > 0, 'AT LEAST ONE VALVE MUST BE OPEN'

    potential_conflicts = WateringEvent.query.filter_by(day=day).all()
    for event in potential_conflicts:

        if start < event.start:
            assert stop < event.start, 'OVERLAP: STOP BEFORE {}'.format(event.start)
        else:
            assert start > event.stop, 'OVERLAP: START AFTER {}'.format(event.stop)

    WateringEvent.create(day, start, stop, valves)
    return

def remove_schedule(id):
    event = WateringEvent.query.get(id)
    if event.in_progress:
        reset()
    event.delete()
    return

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

    if len(current_task) > 0:
        assert len(current_task) == 1
        current_task = current_task[0]

        # be careful w/ midnight behaviour
        should_continue = current_task.day == day and current_task.stop > time
        if not should_continue:
            reset()
            current_task.update(in_progress=False)

    if len(next_task) > 0:
        reset() #this line should be redundant; for safety
        print(next_task)
        assert len(next_task) == 1
        next_task = next_task[0]

        next_task.in_progress = True
        next_task.update(in_progress=True)
        start_watering(next_task)

def start_watering(event):
    for valve in event.valves:
        turn_valve_on(valve)
    turn_pump_on()

def sample_flow_rate():
    '''get flow rate from by sampling digital imput D1 in L/s'''
    channel = 0
    sample_hz = 300
    n_seconds = 10
    n_samples = sample_hz * n_seconds
    signal = mod8di.build(channel, sample_hz, n_samples)
    raw = freq(signal, sample_hz)
    K = 1 # TODO: this parameter needs to be calibrated emperically
    value = raw * K
    return value

def melchiors_empirial_flowrate():
    channel = 0
    sample_hz = 300
    n_seconds = 10
    n_samples = sample_hz * n_seconds
    signal, actual = mod8di.build_with_timing(channel, sample_hz, n_samples)
    rate = freq_empirical(signal, actual)
    return rate

def current_flow_rate():
    '''get flow rate from node-red this should be in L/s'''
    response= requests.get('http://192.168.1.147:1880/water_flow_rate/')
    payload=response.json()
    freq=payload['freq']
    return freq 

def record_flow_rate():
    time = now()

    if PI:
        rate = sample_flow_rate()
    else:
        rate = current_flow_rate()

    SensorReading.create('mod8di', 0, rate, time)
    return

def set_relay(board, idx, value):
    relay = Relay.query.filter_by(board=board, idx=idx).one()
    if PI:
        drivers[board].send(idx, value)
    else:
        print('NOT PI: faking {}[{}] to {}'.format(board, idx, value))
    relay.update(is_on=value)
    return

def suspend():
    state = AppState.query.one()
    state.update(state=AppState.State.suspended)
    reset()

def resume():
    state = AppState.query.one()
    state.update(state=AppState.State.operational)

def reset():
    if PI:
        for driver in drivers.values():
            driver.reset()
    Relay.query.update(dict(is_on=False))
    WateringEvent.query.update(dict(in_progress=False))
    save()

def turn_pump_on():
    pump = Relay.query.filter_by(board='mod4ko', idx=0).one()
    if not pump.is_on:
        assert Relay.query.filter_by(board='kmt', is_on=False).count() < 8
        if PI:
            drivers['mod4ko'].turn_on(0)
        pump.update(is_on=True)
    return

def turn_pump_off():
    pump = Relay.query.filter_by(board='mod4ko', idx=0).one()
    if pump.is_on:
        if PI:
            drivers['mod4ko'].turn_off(0)
        pump.update(is_on=False)
    return

def turn_valve_on(idx):
    valve = Relay.query.filter_by(board='kmt', idx=idx).one()
    if not valve.is_on:
        if PI:
            drivers['kmt'].turn_on(idx)
        valve.update(is_on=True)
    return

def turn_valve_off(idx):
    valve = Relay.query.filter_by(board='kmt', idx=idx).one()
    if valve.is_on:
        pump = Relay.query.filter_by(board='mod4ko', idx=0).one()
        if pump.is_on:
            assert Relay.query.filter_by(board='kmt', is_on=False).count() < 7
        if PI:
            drivers['kmt'].turn_off(idx)
        valve.update(is_on=False)
    return

import click
from flask.cli import with_appcontext

@click.command('agua_init')
@with_appcontext
def agua_init():
    '''database initialization:
    run before db.sqlite exists
    to create tables and populate records
    '''
    create_tables()

    AppState.create(AppState.State.operational)
    SensorReading.create('mod8di', 0, 0, now())

    for driver, size in [('kmt', 8), ('mod4ko', 4)]:
        for i in range(size):
            Relay.create(driver, i)

    for day in WateringEvent.Days:
        for valve in WateringEvent.Valves:
            hour = valve + 12
            WateringEvent.create(day, time(hour, 0), time(hour, 59), [valve])
    return
