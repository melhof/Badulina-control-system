
from flask import render_template, request
from sqlalchemy import desc

from models import Relay, SensorReading, WateringEvent

from agua import (
    time_from_str,
    add_schedule,
    remove_schedule,
    drivers,
    set_relay,
    turn_pump_on,
    turn_pump_off,
    turn_valve_on,
    turn_valve_off,
    current_flow_rate,
)

def index():
    context = {
        'navigation': [
            '/',
            'admin',
            'relays',
            'status',
        ],
    }
    return render_template('agua.html', **context)

def relays():
    if request.method == 'POST':
        for key, value in request.form.items():
            board, idx = key.split(':')
            idx = int(idx)
            value = value == 'True'
            set_relay(board, idx, value)

    context = {
        'boards': [],
    }
    for driver in drivers:
        context['boards'].append({
            'name': driver,
            'relays': Relay.query.filter_by(board=driver).all(),
        })
    return render_template('relays.html', **context)

def status():
    context = {}
    if request.method == 'POST':
        for key, value in request.form.items():
            value = value == 'True'
            try:
                if key == 'pump':
                    if value: 
                        turn_pump_on()
                    else:
                        turn_pump_off()
                elif 'valve:' in key:
                    idx = int(key.split(':')[1])
                    if value: 
                        turn_valve_on(idx)
                    else:
                        turn_valve_off(idx)
            except AssertionError:
                context['ERR'] = True


    context.update({ 
        'pump': Relay.query.filter_by(board='mod4ko', idx=0).one(),
        'valves': Relay.query.filter_by(board='kmt').all(),
        'current_flow': current_flow_rate(),
        'last_flow': SensorReading.query.order_by(desc('time')).first(),
    })
    return render_template('status.html', **context)

def schedule():
    context = {}
    if request.method == 'POST':
        form = request.form
        print(form)
        if 'delete' in form:
            remove_schedule(int(form['delete']))
        else:
            day = int(request.form['day'])
            start = time_from_str(form['start'])
            stop = time_from_str(form['stop'])
            valves = []

            for key, value in form.items():
                if value == 'on' and 'valve' in key:
                    idx = int(key.split(':')[1])
                    valves.append(idx)

            try:
                add_schedule(day, start, stop, valves)
            except AssertionError as err:
                context['ERR'] = True
                context['ERRMSG'] = str(err)
    events = sorted(WateringEvent.query.all(), key=lambda event: (event.day.value, event.start))
    context.update({ 
        'schema': WateringEvent,
        'events': events,
    })
    return render_template('schedule.html', **context)
