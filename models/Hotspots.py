import datetime
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.schema import UniqueConstraint
from typing import List

from models.base import Base
from models.TripHotspots import TripHotspot


class Hotspot (Base):
    __tablename__ = 'hotspots'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64))
    locId: Mapped[str] = mapped_column('loc_id', String(16))
    latitude: Mapped[float]
    longitude: Mapped[float]
    numSpeciesAllTime: Mapped[int] = mapped_column('num_species_all_time')
    createdAt: Mapped[datetime.datetime] = mapped_column('created_at')
    updatedAt: Mapped[datetime.datetime] = mapped_column('updated_at')

    tripHotspots: Mapped[List["TripHotspot"]] = relationship()

    def __repr__(self) -> str:
        return f'<Hotspot(id={self.id}, name={self.name}, locId={self.locId}>'

UniqueConstraint('loc_id', Hotspot.locId)
