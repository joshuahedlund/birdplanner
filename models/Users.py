import datetime
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.schema import UniqueConstraint
from typing import List


from models.base import Base
from models.Trips import Trip
from models.UserSpecies import UserSpecies

class User (Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(64))
    password: Mapped[str] = mapped_column(String(255))
    createdAt: Mapped[datetime.datetime] = mapped_column('created_at')
    updatedAt: Mapped[datetime.datetime] = mapped_column('updated_at')

    userSpecies: Mapped[List["UserSpecies"]] = relationship()
    trips: Mapped[List["Trip"]] = relationship()

    def __repr__(self) -> str:
        return f'<User(id={self.id}, email={self.email}>'

UniqueConstraint('email', User.email)