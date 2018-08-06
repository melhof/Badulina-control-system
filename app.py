#! bin/python
'''
This module composites the other layers:
    models
    agua
    views
    templates
to form a fully functioning web application
'''

import os

from flask import Flask
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

import models
from models import db

import views

os.environ['FLASK_ENV'] = 'development' # trigger debug mode for webserver
os.environ['WERKZEUG_DEBUG_PIN'] = 'off' # no password for interactive web debugger console
#current_dir = os.getcwd()

app = Flask(__name__)

# set basic app config
app.secret_key = '|1_CtCNnbJ%<F:oL' #randomly generated
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}/db.sqlite'.format(current_dir)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'.format(current_dir)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db.init_app(app)

# register models with admin
admin = Admin(app, name='agua', template_mode='bootstrap3')
admin.add_view(ModelView(models.AppState, db.session))
admin.add_view(ModelView(models.Relay, db.session))
admin.add_view(ModelView(models.SensorReading, db.session))
admin.add_view(ModelView(models.WateringEvent, db.session))

# register views with router
app.add_url_rule(rule='/', view_func=views.index)
app.add_url_rule(rule='/relays/', view_func=views.relays, methods=('GET', 'POST'))
app.add_url_rule(rule='/status/', view_func=views.status, methods=('GET', 'POST'))
app.add_url_rule(rule='/schedule/', view_func=views.schedule, methods=('GET', 'POST'))

from agua import agua_init 
app.cli.add_command(agua_init)

if __name__ == '__main__':
    app.run('0.0.0.0', 5000) # run webserver
