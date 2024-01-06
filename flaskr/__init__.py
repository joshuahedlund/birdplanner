import os

from flask import Flask, g
from flask_sqlalchemy import SQLAlchemy

from . import db

from repositories.TripRepository import getTrip


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
    )
    db.init_app(app)

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


    # a simple page that says hello
    @app.route('/hello')
    def hello():
        trip = getTrip(app.db.session, 3)

        return 'Hello, World!' + str(trip.name)

    from . import species
    app.register_blueprint(species.bp)
    app.add_url_rule('/', endpoint='index')

    return app
