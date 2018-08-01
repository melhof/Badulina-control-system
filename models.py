
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Relay(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    board = db.Column(db.String(10), nullable=False)
    idx = db.Column(db.Integer, nullable=False)
    is_on = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return '<Relay: board:{} idx:{}>'.format(self.board, self.idx)

class SensorReading(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    board = db.Column(db.String(10), nullable=False)
    idx = db.Column(db.Integer, nullable=False)
    data = db.Column(db.Integer, nullable=False)
    time = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return '<SensorReading: board:{} idx:{}>'.format(self.board, self.idx)
