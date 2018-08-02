
import enum
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Days(enum.Enum):
    monday    = 0
    tuesday   = 1
    wednesday = 2
    thursday  = 3
    friday    = 4
    saturday  = 5
    sunday    = 6

class Relay(db.Model):
    id     = db.Column(db.Integer, primary_key=True)
    board  = db.Column(db.String(10), nullable=False)
    idx    = db.Column(db.Integer, nullable=False)
    is_on  = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return '<Relay: board:{} idx:{}>'.format(self.board, self.idx)

class SensorReading(db.Model):
    id     = db.Column(db.Integer, primary_key=True)
    board  = db.Column(db.String(10), nullable=False)
    idx    = db.Column(db.Integer, nullable=False)
    data   = db.Column(db.Integer, nullable=False)
    time   = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return '<SensorReading: board:{} idx:{}>'.format(self.board, self.idx)

class WateringEvent(db.Model):
    Days = Days
    Valves = range(8)

    id       = db.Column(db.Integer, primary_key=True)
    day      = db.Column(db.Enum(Days), nullable=False)
    start    = db.Column(db.Time, nullable=False)
    stop     = db.Column(db.Time, nullable=False)
    valves_  = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        return '<WateringEvent: day:{} start:{} stop:{}>'.format(self.day, self.start, self.stop)

    @property
    def valves(self):
        return [int(valve) for valve in self.valves_]

    @classmethod
    def create(cls, day, start, stop, valves):
        return cls(
            day=list(Days)[day],
            start=start,
            stop=stop,
            valves_=''.join(map(str, valves)),
        )
