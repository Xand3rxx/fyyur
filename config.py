import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database


# TODO IMPLEMENT DATABASE URL
class DatabaseConfgurations:
    SECRET_KEY = SECRET_KEY
    DEBUG = DEBUG
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:my1love1@localhost:5433/fyyur'
    # SQLALCHEMY_DATABASE_URI = '<Put your local database url>'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
