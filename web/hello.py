
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

try:
    from drivers import kmt, mod4ko
    PI = True
    drivers = {
        'kmt': kmt,
        'mod4ko': mod4ko,
    }
except:
    PI = False
    drivers = {
        'kmt': None,
        'mod4ko': None,
    }


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db' #TODO change
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

class Relay(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    board = db.Column(db.String(10), nullable=False)
    idx = db.Column(db.Integer, nullable=False)
    is_on = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return '<Relay: board:{} idx:{}>'.format(self.board, self.idx)

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
            relay = Relay.query.filter_by(board=board, idx=idx).one()
            if PI:
                ...
                #drivers[board].send(idx, value)
            else:
                print('NOT PI: NO-OP')
            relay.is_on = value
            db.session.add(relay)
            db.session.commit()

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

def seed_db():
    for driver in drivers:
        for i in range(drivers[driver].size):
            db.session.add(Relay(board=driver, idx=i, is_on=False))
    db.session.commit()
