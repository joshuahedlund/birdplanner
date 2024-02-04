from sqlalchemy import String, Index
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base

class Species (Base):
    __tablename__ = 'species'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64))
    latinName: Mapped[str] = mapped_column('latin_name', String(64))
    urlId: Mapped[str] = mapped_column('url_id', String(16))
    def __repr__(self) -> str:
        return f'<Species(id={self.id}, name={self.name}>'

Index('name_index', Species.name)