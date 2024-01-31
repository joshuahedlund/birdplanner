
from sqlalchemy import func, or_, and_
from sqlalchemy.orm import Session

from models.Species import Species
from models.SpeciesFreq import SpeciesFreq
from models.UserSpecies import UserSpecies


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


def getTopHotspotsForSpecies(session: Session, speciesId: int, month: int, limit: int = 10, zones: list = None) -> list:
    from models.Hotspots import Hotspot

    hotspots = session.query(Hotspot)\
        .join(SpeciesFreq)\
        .filter(SpeciesFreq.speciesId == speciesId)\
        .filter(SpeciesFreq.month == month)
    if zones:
        zoneFilters = (and_(func.abs(Hotspot.latitude - zone['lat']) < zone['radiusKm'] / 111.1, func.abs(Hotspot.longitude - zone['lng']) < zone['radiusKm'] / 111.1) for zone in zones)
        hotspots = hotspots.filter(or_(zoneFilters))

    hotspots = hotspots.with_entities(Hotspot.id, Hotspot.name, Hotspot.locId, SpeciesFreq.freq)\
        .order_by(SpeciesFreq.freq.desc())\
        .limit(limit)\
        .all()

    return hotspots


def getUniqueTargetCount(session: Session, hotspotIds: list, month: int, minFreq: int, userId: int) -> int:
    return session.query(SpeciesFreq.speciesId)\
        .filter(SpeciesFreq.month == month)\
        .filter(SpeciesFreq.freq >= minFreq)\
        .filter(SpeciesFreq.hotspotId.in_(hotspotIds))\
        .filter(SpeciesFreq.speciesId.notin_(
            session.query(UserSpecies.speciesId).filter(UserSpecies.userId == userId)
        ))\
        .distinct()\
        .count()


def getTargetSpeciesListForHotspots(session: Session, hotspotIds: list, month: int, minFreq: int, userId: int) -> list:
    return session.query(SpeciesFreq.speciesId)\
        .filter(SpeciesFreq.month == month)\
        .filter(SpeciesFreq.freq >= minFreq)\
        .filter(SpeciesFreq.hotspotId.in_(hotspotIds))\
        .filter(SpeciesFreq.speciesId.notin_(
            session.query(UserSpecies.speciesId).filter(UserSpecies.userId == userId)
        ))\
        .distinct()\
        .all()
