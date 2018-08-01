
from flask import render_template, request
from sqlalchemy import desc

from models import Relay, SensorReading
from agua import (
    drivers,
    set_relay,
    turn_pump_on,
    turn_pump_off,
    turn_valve_on,
    turn_valve_off,
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
        print(request.form)
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
        'last_flow': SensorReading.query.order_by(desc('time')).first(),
    })
    return render_template('status.html', **context)
