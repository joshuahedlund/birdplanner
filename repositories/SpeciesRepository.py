import os
import sys
sys.path.append(os.path.dirname(os.getcwd()))

from pandas import DataFrame
from sqlalchemy.orm import Session
def getSpeciesIds(session: Session, speciesNames: list) -> DataFrame:
    from models.Species import Species

    species = session.query(Species) \
        .filter(Species.name.in_(speciesNames)) \
        .with_entities(Species.id, Species.name) \
        .all()

    return DataFrame(species, columns=['id', 'name'])

def storeSpecies(session: Session, name: str) -> int:
    from models.Species import Species

    species = Species(name=name)
    session.add(species)
    session.flush()

    return species.id