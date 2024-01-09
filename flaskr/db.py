from flask_sqlalchemy import SQLAlchemy
from config import DATABASE_URI


def init_app(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
    db = SQLAlchemy(app)
    app.db = db