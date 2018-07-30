
from flask import render_template, request

from models import Relay
from agua import drivers, set_relay

def index():
    context = {
        'name': 'taylor',
        'navigation': [
            {
                'href': '/relays',
                'caption': 'relays',
            },
        ],
    }
    return render_template('hello.html', **context)

def relays():
    if request.method == 'POST':
        for key, value in request.form.items():
            board, idx = key.split(':')
            idx = int(idx)
            value = value == 'True'
            set_relay(board, idx, value)

    context = {
        'name': 'taylor',
        'boards': [],
    }
    for driver in drivers:
        context['boards'].append({
            'name': driver,
            'relays': Relay.query.filter_by(board=driver).all(),
        })
    return render_template('relays.html', **context)
