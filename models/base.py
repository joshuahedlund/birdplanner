from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase

from config import DATABASE_URI

class Base(DeclarativeBase):
    pass

def init_engine():
    return create_engine(DATABASE_URI)

def init_db(engine):
    Base.metadata.create_all(engine)

