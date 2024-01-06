import os
import sys
sys.path.append(os.path.dirname(os.getcwd()))

from pandas import DataFrame
from sqlalchemy.orm import Session

from models.Species import Species

def getSpeciesIds(session: Session, speciesNames: list) -> DataFrame:
    species = session.query(Species) \
        .filter(Species.name.in_(speciesNames)) \
        .with_entities(Species.id, Species.name) \
        .all()

    return DataFrame(species, columns=['id', 'name'])

def storeSpecies(session: Session, name: str) -> int:
    species = Species(name=name)
    session.add(species)
    session.flush()

    return species.id

def getAllSpecies(session: Session) -> list:
    species = session.query(Species) \
        .all()

    return species

def getSpecies(session: Session, speciesId: int) -> list:
    species = session.query(Species) \
        .filter(Species.id == speciesId) \
        .first()

    return species