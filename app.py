#! bin/python

import os

from flask import Flask
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

import models
import views

os.environ['FLASK_ENV'] = 'development'
app = Flask(__name__)
app.secret_key = '|1_CtCNnbJ%<F:oL' #randomly generated

current_dir = os.getcwd()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}/db.sqlite'.format(current_dir)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

models.db.init_app(app)

admin = Admin(app, name='agua', template_mode='bootstrap3')
admin.add_view(ModelView(models.Relay, models.db.session))
admin.add_view(ModelView(models.SensorReading, models.db.session))

app.add_url_rule(rule='/', view_func=views.index)
app.add_url_rule(rule='/relays/', view_func=views.relays, methods=('GET', 'POST'))
app.add_url_rule(rule='/status/', view_func=views.status, methods=('GET', 'POST'))

if __name__ == '__main__':
    app.run('0.0.0.0', 5000)
