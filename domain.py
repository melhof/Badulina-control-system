'''
This module encapsulates domain logic:
    safety restraints
    knowledge about irrigation hardware configuration
'''

from datetime import time

from config import PI

if PI:
    from drivers import kmt, mod4ko, digiten

from utils import now
from models import (
    save,
    Relay,
    SensorReading,
    WateringEvent,
    AppState,
)

RELAY_BOARDS = [('kmt', 8), ('mod4ko', 4)]

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
    state = AppState.query.one()
    state.update(manually_modified=False)
    for valve in event.valves:
        turn_valve_on(valve)
    turn_pump_on()


def sample_flow_rate():
    '''
    take samples hz at n
    devide by 2 magnets / rotation
    calibration factor is K
    '''
    K = 1
    sample_hz = 300
    n_seconds = 10
    n_samples = sample_hz * n_seconds
    freq = digiten.flow_rate(sample_hz, n_samples)
    value = freq / 2
    return value * K

def record_flow_rate():
    pump = Relay.query.filter_by(board='mod4ko', idx=0).one()
    if not pump.is_on:
        return

    time = now()

    if PI:
        rate = sample_flow_rate()
    else:
        print('NOT PI: faking flow rate')
        rate = 0

    valves = []
    for valve in Relay.query.filter_by(board='kmt', is_on=True).all():
        valves.append(valve.idx)

    SensorReading.create('mod8di', 0, rate, time, valves)
    return

def set_relay(board, idx, value):
    relay = Relay.query.filter_by(board=board, idx=idx).one()
    if PI:
        if board == 'kmt':
            kmt.send(idx, value)
        elif board == 'mod4ko':
            mod4ko.send(idx, value)
        else:
            raise Exception('unknown board {}!'.format(board))
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
    state.update(
        state=AppState.State.operational,
        manually_modified=False,
    )

def reset():
    if PI:
        kmt.reset()
        mod4ko.reset()
    Relay.query.update(dict(is_on=False))
    WateringEvent.query.update(dict(in_progress=False))
    save()

def turn_pump_on():
    pump = Relay.query.filter_by(board='mod4ko', idx=0).one()
    if not pump.is_on:
        assert Relay.query.filter_by(board='kmt', is_on=False).count() < 8
        if PI:
            mod4ko.turn_on(0)
        pump.update(is_on=True)
    return

def turn_pump_off():
    pump = Relay.query.filter_by(board='mod4ko', idx=0).one()
    if pump.is_on:
        if PI:
            mod4ko.turn_off(0)
        pump.update(is_on=False)
    return

def turn_valve_on(idx):
    valve = Relay.query.filter_by(board='kmt', idx=idx).one()
    if not valve.is_on:
        if PI:
            kmt.turn_on(idx)
        valve.update(is_on=True)
    return

def turn_valve_off(idx):
    valve = Relay.query.filter_by(board='kmt', idx=idx).one()
    if valve.is_on:
        pump = Relay.query.filter_by(board='mod4ko', idx=0).one()
        if pump.is_on:
            assert Relay.query.filter_by(board='kmt', is_on=False).count() < 7
        if PI:
            kmt.turn_off(idx)
        valve.update(is_on=False)
    return

import click
from flask.cli import with_appcontext

@click.command('agua_init')
@with_appcontext
def agua_init():
    '''database initialization:
        populate records
        run after database & schema already created
    '''

    AppState.create(AppState.State.operational)
    SensorReading.create('mod8di', 0, 0, now(), [0])

    for driver, size in RELAY_BOARDS:
        for i in range(size):
            Relay.create(driver, i)

    for day in WateringEvent.Days:
        for valve in WateringEvent.Valves:
            hour = valve + 12
            WateringEvent.create(day, time(hour, 0), time(hour, 59), [valve])
    return
