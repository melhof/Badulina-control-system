
import os
import getpass

PI = getpass.getuser() == 'pi'

if PI:
    SECRET_KEY = os.environ['FLASK_SECRET_KEY']
    ENV = 'production'
    DEBUG = False
    SERVER_NAME = '0.0.0.0:5000'
else:
    ENV = 'development'
    DEBUG = True
    SERVER_NAME = 'localhost:5000'

SQLALCHEMY_DATABASE_URI = 'sqlite:///db.sqlite'
SQLALCHEMY_TRACK_MODIFICATIONS = True # not really needed, just explicitly set to avoid warnings

PI_IP = os.environ['PI_IP']
