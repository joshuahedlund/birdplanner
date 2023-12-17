from sqlalchemy import ForeignKeyConstraint
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.dialects.mysql import ENUM

from models.base import Base

class TripHotspot (Base):
    __tablename__ = 'trip_hotspots'

    id: Mapped[int] = mapped_column(primary_key=True)
    tripId: Mapped[int] = mapped_column('trip_id')
    hotspotId: Mapped[int] = mapped_column('hotspot_id')
    status: Mapped[str] = mapped_column(ENUM('visit','skip'), nullable=True)

    def __repr__(self) -> str:
        return f'<TripHotspots(id={self.id}, tripId={self.tripId}, hotspotId={self.hotspotId}, status={self.status}>'

ForeignKeyConstraint([TripHotspot.tripId], ['trips.id'], name='fk_trip_id')
ForeignKeyConstraint([TripHotspot.hotspotId], ['hotspots.id'], name='fk_hotspot_id')