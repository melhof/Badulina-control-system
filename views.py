'''
This module encapsulates webserver logic:
    definition of urls 
    encoding / decoding html and JSON data
    preparing the context for rendering the appropriate template
'''
from flask import render_template, request, redirect, url_for
from sqlalchemy import desc
from datetime import time, timedelta

from utils import now
from models import Relay, SensorReading, WateringEvent, AppState
from domain import (
    RELAY_BOARDS,
    suspend, 
    resume,
    add_schedule,
    remove_schedule,
    set_relay,
    turn_pump_on,
    turn_pump_off,
    turn_valve_on,
    turn_valve_off,
)

base_context = {
    'navigation': [
        'admin',
        'relays',
        'status',
        'schedule',
        'history',
    ],
}


def index():
    return redirect(url_for('status'))

def history():
    day_ago = now() - timedelta(days=1)
    last_day = SensorReading.query.filter(
        SensorReading.time > day_ago
    ).all()

    day_total = sum(reading.data for reading in last_day)

    context = {
        'schema': SensorReading,
        'totaldayagua' : day_total,
        'readings': SensorReading.query.order_by(desc('time')).all(),
    }
    
    context.update(base_context)

    return render_template('history.html', **context)


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
    for board, _ in RELAY_BOARDS:
        context['boards'].append({
            'name': board,
            'relays': Relay.query.filter_by(board=board).all(),
        })
    context.update(base_context)
    return render_template('relays.html', **context)

def status():
    context = {}
    if request.method == 'POST':
        context.update(post_status())

    state = AppState.query.one()
    context.update({ 
        'pump': Relay.query.filter_by(board='mod4ko', idx=0).one(),
        'valves': Relay.query.filter_by(board='kmt').all(),
        'last_flow': SensorReading.query.order_by(desc('time')).first(),
        'operational': state.state == AppState.State.operational,
        'modified': state.manually_modified,
    })
    context.update(base_context)
    return render_template('status.html', **context)

def post_status():
    context = {}
    if 'suspend' in request.form:
        suspend()
    elif 'resume' in request.form:
        resume()
    else:
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

        AppState.query.one().update(manually_modified=True)
    return context

def schedule():
    context = {}
    if request.method == 'POST':
        context.update(post_schedule())

    events = sorted(WateringEvent.query.all(), key=day_sort)

    state = AppState.query.one()
    context.update({ 
        'schema': WateringEvent,
        'events': events,
        'modified': state.manually_modified,
    })
    context.update(base_context)
    return render_template('schedule.html', **context)

def day_sort(event):
    return (event.day.value, event.start)

def post_schedule():
    context = {}
    form = request.form
    if 'delete' in form:
        remove_schedule(int(form['delete']))
    else:
        day = WateringEvent.Days(int(request.form['day']))

        start_hour = int(form['start-hour'])
        start_min = int(form['start-min'])
        stop_hour = int(form['stop-hour'])
        stop_min = int(form['stop-min'])

        start = time(start_hour, start_min)
        stop = time(stop_hour, stop_min)

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
    return context



