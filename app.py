
import os

from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

current_dir = os.getcwd()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}/app.db'.format(current_dir)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)

class Relay(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    board = db.Column(db.String(10), nullable=False)
    idx = db.Column(db.Integer, nullable=False)
    is_on = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return '<Relay: board:{} idx:{}>'.format(self.board, self.idx)

from agua import drivers, set_relay # keep this line below app, db, Relay

@app.route('/')
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

@app.route('/relays/', methods=('GET', 'POST'))
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
