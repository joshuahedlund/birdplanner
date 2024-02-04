import os
import sys

from sqlalchemy import or_, func

sys.path.append(os.path.dirname(os.getcwd()))

from pandas import DataFrame
from sqlalchemy.orm import Session

from models.Hotspots import Hotspot
from models.Species import Species
from models.SpeciesFreq import SpeciesFreq
from models.TripHotspots import TripHotspot

def getSpeciesIds(session: Session, speciesNames: list) -> DataFrame:
    species = session.query(Species) \
        .filter(Species.name.in_(speciesNames)) \
        .with_entities(Species.id, Species.name) \
        .all()

    return DataFrame(species, columns=['id', 'name'])

def storeSpecies(session: Session, name: str, urlId: str) -> int:
    species = Species(name=name, latinName='', urlId=urlId)
    session.add(species)
    session.flush()

    return species.id

def getAllSpecies(session: Session) -> list:
    species = session.query(Species) \
        .all()

    return species

def getSpecies(session: Session, speciesId: int) -> list:
    return session.query(Species).get(speciesId)

def getTripSpeciesByNameFragment(session: Session, nameFragment: str, month: int, lat: float, lng: float) -> list:
    species = session.query(Hotspot)\
        .join(SpeciesFreq)\
        .join(Species)\
        .filter(SpeciesFreq.month == month)\
        .filter(func.abs(Hotspot.latitude - lat) < 0.6)\
        .filter(func.abs(Hotspot.longitude - lng) < 0.6)\
        .filter(or_(Species.name.ilike(f"{nameFragment}%"), Species.name.ilike(f"% {nameFragment}%")))\
        .order_by(Species.name)\
        .group_by(Species.id, Species.name)\
        .with_entities(Species.id, Species.name)\
        .limit(10)\
        .all()

    return species