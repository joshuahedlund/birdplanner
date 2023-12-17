from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass

def init_engine():
    return create_engine('mysql+pymysql://root@localhost:3306/birdplanner')

def init_db(engine):
    Base.metadata.create_all(engine)

