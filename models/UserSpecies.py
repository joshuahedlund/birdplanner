from sqlalchemy import ForeignKeyConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base

class UserSpecies (Base):
    __tablename__ = 'user_species'

    id: Mapped[int] = mapped_column(primary_key=True)
    userId: Mapped[int] = mapped_column('user_id')
    speciesId: Mapped[int] = mapped_column('species_id')

    species: Mapped["Species"] = relationship()

    def __repr__(self) -> str:
        return f'<UserSpecies(id={self.id}, userId={self.userId}, speciesId={self.speciesId}>'

Index('user_id', UserSpecies.userId)
ForeignKeyConstraint([UserSpecies.speciesId], ['species.id'], name='fk_us_species_id')