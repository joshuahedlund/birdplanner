
from sqlalchemy import func
from sqlalchemy.orm import Session

from models.Species import Species
from models.SpeciesFreq import SpeciesFreq

def storeSpeciesFreq(session: Session, hotspotId: int, speciesId: int, freq: int, month: int):
    speciesFreq = SpeciesFreq(speciesId=speciesId, freq=freq, month=month, hotspotId=hotspotId)
    session.add(speciesFreq)

def getSpeciesFreqs(session: Session, hotspotId: int, month: int, freq: int = None) -> list:
    speciesFreqs = session.query(SpeciesFreq)\
        .filter(SpeciesFreq.hotspotId == hotspotId)\
        .filter(SpeciesFreq.month == month)
    if freq:
        speciesFreqs = speciesFreqs.filter(SpeciesFreq.freq >= freq)
    speciesFreqs = speciesFreqs.join(SpeciesFreq.species)\
        .with_entities(Species.id, Species.name, SpeciesFreq.freq)\
        .all()

    return speciesFreqs


def getTopHotspotsForSpecies(session: Session, speciesId: int, month: int, limit: int = 10, lat: float = None, lng: float = None) -> list:
    from models.Hotspots import Hotspot

    hotspots = session.query(Hotspot)\
        .join(SpeciesFreq)\
        .filter(SpeciesFreq.speciesId == speciesId)\
        .filter(SpeciesFreq.month == month)
    if lat and lng:
        hotspots = hotspots.filter(func.abs(Hotspot.latitude - lat) < 0.6)
    hotspots = hotspots.with_entities(Hotspot.id, Hotspot.name, Hotspot.locId, SpeciesFreq.freq)\
        .order_by(SpeciesFreq.freq.desc())\
        .limit(limit)\
        .all()

    return hotspots


def getUniqueTargetCount(session: Session, hotspotIds: list, month: int, minFreq: int) -> int:
    return session.query(SpeciesFreq.speciesId)\
        .filter(SpeciesFreq.month == month)\
        .filter(SpeciesFreq.freq >= minFreq)\
        .filter(SpeciesFreq.hotspotId.in_(hotspotIds))\
        .distinct()\
        .count()
