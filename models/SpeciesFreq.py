from sqlalchemy import ForeignKeyConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.mysql import TINYINT
from typing import List

from models.base import Base
class SpeciesFreq (Base):
    __tablename__ = 'species_freq'

    id: Mapped[int] = mapped_column(primary_key=True)
    hotspotId: Mapped[int] = mapped_column('hotspot_id')
    speciesId: Mapped[int] = mapped_column('species_id')
    month: Mapped[int] = mapped_column(TINYINT)
    freq: Mapped[int] = mapped_column(TINYINT)

    species: Mapped["Species"] = relationship()

    def __repr__(self) -> str:
        return f'<TripMatrix(hotspotId={self.hotspotId}, speciesId={self.speciesId}, month={self.month}, freq={self.freq}>'

ForeignKeyConstraint([SpeciesFreq.hotspotId], ['hotspots.id'], name='fk_sf_hotspot_id')
ForeignKeyConstraint([SpeciesFreq.speciesId], ['species.id'], name='fk_sf_species_id')
Index('month_index', SpeciesFreq.month)