import datetime
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.schema import UniqueConstraint

from models.base import Base


class Hotspot (Base):
    __tablename__ = 'hotspots'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64))
    locId: Mapped[str] = mapped_column(String(16))
    latitude: Mapped[float]
    longitude: Mapped[float]
    numSpeciesAllTime: Mapped[int]
    createdAt: Mapped[datetime.datetime]
    updatedAt: Mapped[datetime.datetime]

    def __repr__(self) -> str:
        return f'<Hotspot(id={self.id}, name={self.name}, locId={self.locId}>'

UniqueConstraint('locId', Hotspot.locId)
