
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

from app import Relay, db

def set_relay(board, idx, value):
    relay = Relay.query.filter_by(board=board, idx=idx).one()
    if PI:
        drivers[board].send(idx, value)
    else:
        print('NOT PI: faking {}[{}] to {}'.format(board, idx, value))
    relay.is_on = value
    db.session.add(relay)
    db.session.commit()

def seed_db():
    for driver in drivers:
        for i in range(drivers[driver].size):
            db.session.add(Relay(board=driver, idx=i, is_on=False))
    db.session.commit()
