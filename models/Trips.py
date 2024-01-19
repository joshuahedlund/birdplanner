import datetime
from sqlalchemy import String, ForeignKeyConstraint
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
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
    radiusKm: Mapped[int] = mapped_column('radius_km', default=50)
    freqMin: Mapped[int] = mapped_column('freq_min', default=70)
    parentTripId: Mapped[int] = mapped_column('parent_trip_id', nullable=True)
    createdAt: Mapped[datetime.datetime] = mapped_column('created_at')
    updatedAt: Mapped[datetime.datetime] = mapped_column('updated_at')

    def __repr__(self) -> str:
        return f'<Trip(id={self.id}, name={self.name}, year={self.year}, month={self.month}>'


ForeignKeyConstraint([Trip.userId], ['users.id'], name='fk_trip_user_id')
