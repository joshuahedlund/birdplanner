from flask_sqlalchemy import SQLAlchemy
from config import DATABASE_NAME, DATABASE_USER, DATABASE_HOST, DATABASE_PORT


def init_app(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DATABASE_USER}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}'
    db = SQLAlchemy(app)
    app.db = db