import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from repositories.TripRepository import getTrip

from config import DATABASE_NAME, DATABASE_USER, DATABASE_HOST, DATABASE_PORT



def create_app(test_config=None):
    # create and configure the app
    db = SQLAlchemy()
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    app.config[
        'SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DATABASE_USER}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        trip = getTrip(db.session, 3)

        return 'Hello, World!' + str(trip.name)

    return app
