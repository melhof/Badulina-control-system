'''
This module encapsulates database logic:
    creating tables
    inserting record
    deleing records
    querying records
'''
import enum
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_tables():
    db.create_all()

def save():
    db.session.commit()
    return

class AguaModel(db.Model):
    '''Abstract Base Application Model:
        a place to put common methods
    '''
    __abstract__ = True

    def __repr__(self):
        '''define the string representation of the model
        when printed in terminal
        '''
        table = self.__table__
        fields = ''
        for column in table.columns:
            fields += '{}={} '.format(column.name, getattr(self, column.name))

        return '<{}: {}>'.format(table.name, ''.join(fields))

    def insert(self):
        db.session.add(self)
        save()
        return

    def update(self, **keyword_arguments):
        for key, value in keyword_arguments.items():
            setattr(self, key, value)
        save()
        return

    def delete(self):
        db.session.delete(self)
        save()
        return

class AppState(AguaModel):
    class State(enum.Enum):
        operational = 0
        suspended = 1

    id = db.Column(db.Integer, primary_key=True)
    state = db.Column(db.Enum(State), nullable=False)

    @classmethod
    def create(cls, state):
        record = cls(state=state)
        record.insert()
        return

class Relay(AguaModel):
    id = db.Column(db.Integer, primary_key=True)
    board = db.Column(db.String(10), nullable=False)
    idx = db.Column(db.Integer, nullable=False)
    is_on = db.Column(db.Boolean, nullable=False, default=False)

    @classmethod
    def create(cls, board, idx):
        record = cls(board=board, idx=idx)
        record.insert()
        return

class SensorReading(AguaModel):
    id = db.Column(db.Integer, primary_key=True)
    board = db.Column(db.String(10), nullable=False)
    idx = db.Column(db.Integer, nullable=False)
    data = db.Column(db.Integer, nullable=False)
    time = db.Column(db.DateTime, nullable=False)

    @classmethod
    def create(cls, board, idx, data, time):
        record = cls(board=board, idx=idx, data=data, time=time)
        record.insert()
        return

class WateringEvent(AguaModel):
    class Days(enum.Enum):
        monday = 0
        tuesday = 1
        wednesday = 2
        thursday = 3
        friday = 4
        saturday = 5
        sunday = 6

    Valves = range(8)

    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.Enum(Days), nullable=False)
    start = db.Column(db.Time, nullable=False)
    stop = db.Column(db.Time, nullable=False)
    valves_ = db.Column(db.String(10), nullable=False)
    in_progress = db.Column(db.Boolean, nullable=False, default=False)

    @property
    def valves(self):
        return [int(valve) for valve in self.valves_]

    @classmethod
    def create(cls, day, start, stop, valves):
        record = cls(
            day=day,
            start=start,
            stop=stop,
            valves_=''.join(map(str, valves)),
        )
        record.insert()
        return
