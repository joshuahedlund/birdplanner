import datetime
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.schema import Index
from sqlalchemy.dialects.mysql import SMALLINT, TINYINT

from models.base import Base

class Trip (Base):
    __tablename__ = 'trips'

    id: Mapped[int] = mapped_column(primary_key=True)
    userId: Mapped[int] = mapped_column('user_id')
    name: Mapped[str] = mapped_column(String(64))
    latitude: Mapped[float]
    longitude: Mapped[float]
    year: Mapped[int] = mapped_column(SMALLINT)
    month: Mapped[int] = mapped_column(TINYINT)
    createdAt: Mapped[datetime.datetime] = mapped_column('created_at')
    updatedAt: Mapped[datetime.datetime] = mapped_column('updated_at')

    def __repr__(self) -> str:
        return f'<Trip(id={self.id}, name={self.name}, year={self.year}, month={self.month}>'

Index('user_id', Trip.userId)
