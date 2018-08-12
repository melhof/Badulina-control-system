#! bin/python
'''
This module composites the other layers:
    models
    domain
    views
    templates
to form a fully functioning web application
'''
from flask import Flask
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_migrate import Migrate

import models
from models import db

import views

app = Flask(__name__)
app.config.from_object('config')

db.init_app(app)
migrate = Migrate(app, db)

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
app.add_url_rule(rule='/history/', view_func=views.history, methods=('GET', 'POST'))

from domain import agua_init 
app.cli.add_command(agua_init)

if __name__ == '__main__':
    app.run()
