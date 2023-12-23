from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase

from config import DATABASE_NAME, DATABASE_USER, DATABASE_HOST, DATABASE_PORT

class Base(DeclarativeBase):
    pass

def init_engine():
    return create_engine(f'mysql+pymysql://{DATABASE_USER}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}')

def init_db(engine):
    Base.metadata.create_all(engine)

