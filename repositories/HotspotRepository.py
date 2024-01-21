import os
import sys

sys.path.append(os.path.dirname(os.getcwd()))

from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_

from models.Hotspots import Hotspot
from models.SpeciesFreq import SpeciesFreq
from models.UserSpecies import UserSpecies
from models.TripHotspots import TripHotspot


def getAllHotspotsForTrip(session: Session, tripId: int, tripMonth: int, minFreq: int, userId: int) -> list:
    hotspots = session.query(Hotspot) \
        .join(TripHotspot) \
        .join( # get target species that match trip criteria
            SpeciesFreq,
            and_(SpeciesFreq.hotspotId == Hotspot.id, SpeciesFreq.month == tripMonth, SpeciesFreq.freq >= minFreq),
            isouter=True
        ).filter(TripHotspot.tripId == tripId) \
        .filter(or_(SpeciesFreq.speciesId == None, SpeciesFreq.speciesId.notin_(  # exclude species already seen by user
            session.query(UserSpecies.speciesId).filter(UserSpecies.userId == userId)
        ))) \
        .order_by(func.count(SpeciesFreq.id).desc()) \
        .group_by(Hotspot.id) \
        .with_entities(
            func.any_value(Hotspot.id).label('id'),
            func.any_value(Hotspot.locId).label('locId'),
            func.any_value(Hotspot.name).label('name'),
            func.any_value(Hotspot.latitude).label('latitude'),
            func.any_value(Hotspot.longitude).label('longitude'),
            func.any_value(Hotspot.numSpeciesAllTime).label('numSpeciesAllTime'),
            func.any_value(Hotspot.speciesFreqUpdatedAt).label('speciesFreqUpdatedAt'),
            func.any_value(TripHotspot.status).label('status'),
            func.count(SpeciesFreq.id).label('numSpeciesTargets')
        )

    return hotspots.all()

def getHotspotIdsForTrip(session: Session, tripId: int) -> list:
    tripHotSpots = session.query(TripHotspot) \
        .filter(TripHotspot.tripId == tripId) \
        .filter(or_(TripHotspot.status.is_(None), TripHotspot.status == 'visit')) \
        .with_entities(TripHotspot.hotspotId) \
        .all()
    hotspotIds = [x[0] for x in tripHotSpots]

    return hotspotIds

def getTripHotspotsWithFreqs(session: Session, tripId: int) -> list:
    tripHotspots = session.query(TripHotspot) \
        .filter(TripHotspot.tripId == tripId) \
        .filter(Hotspot.speciesFreqUpdatedAt.isnot(None)) \
        .filter(or_(TripHotspot.status.is_(None), TripHotspot.status == 'visit')) \
        .join(Hotspot) \
        .with_entities(Hotspot.id, Hotspot.locId, Hotspot.name) \
        .all()

    return tripHotspots

def getTopHotspotsNotConsideredForTrip(
        session: Session,
        userId: int,
        tripId: int,
        tripMonth: int,
        lat: float,
        lng: float,
        limit: int=15,
        dist: float=50,
        minFreq: int=70,
    ) -> list:
    subquery = session.query(TripHotspot.hotspotId).filter(TripHotspot.tripId == tripId)

    distDeg = dist / 111.1 #convert km to degrees

    hotspots = session.query(Hotspot) \
        .join(
            SpeciesFreq,
            and_(SpeciesFreq.hotspotId == Hotspot.id, SpeciesFreq.month == tripMonth, SpeciesFreq.freq >= minFreq),
            isouter=True
        )\
        .filter(Hotspot.id.notin_(subquery)) \
        .filter(func.abs(Hotspot.latitude - lat) < distDeg) \
        .filter(func.abs(Hotspot.longitude - lng) < distDeg) \
        .filter(or_(SpeciesFreq.speciesId == None, SpeciesFreq.speciesId.notin_(  # exclude species already seen by user
            session.query(UserSpecies.speciesId).filter(UserSpecies.userId == userId)
        ))) \
        .order_by(Hotspot.numSpeciesAllTime.desc()) \
        .group_by(Hotspot.id) \
        .with_entities(
            func.any_value(Hotspot.id).label('id'),
            func.any_value(Hotspot.locId).label('locId'),
            func.any_value(Hotspot.name).label('name'),
            func.any_value(Hotspot.latitude).label('latitude'),
            func.any_value(Hotspot.longitude).label('longitude'),
            func.any_value(Hotspot.numSpeciesAllTime).label('numSpeciesAllTime'),
            func.any_value(Hotspot.speciesFreqUpdatedAt).label('speciesFreqUpdatedAt'),
            func.count(SpeciesFreq.id).label('numSpeciesTargets')
        ) \
        .limit(limit) \
        .all()

    return hotspots

def getTopHotspotsNearby(session: Session, lat: float, lng: float, limit: int) -> list:
    hotspots = session.query(Hotspot) \
        .filter(func.abs(Hotspot.latitude - lat) < 0.6) \
        .filter(func.abs(Hotspot.longitude - lng) < 0.6) \
        .order_by(Hotspot.numSpeciesAllTime.desc()) \
        .limit(limit) \
        .all()

    return hotspots


def skipHotspot(session: Session, tripId: int, hotspotId: int) -> None:
    tripHotspot = session.query(TripHotspot) \
        .filter(TripHotspot.tripId == tripId) \
        .filter(TripHotspot.hotspotId == hotspotId) \
        .first()

    tripHotspot.status = 'skip'
    session.commit()

def visitHotspot(session: Session, tripId: int, hotspotId: int) -> None:
    tripHotspot = session.query(TripHotspot) \
        .filter(TripHotspot.tripId == tripId) \
        .filter(TripHotspot.hotspotId == hotspotId) \
        .first()

    tripHotspot.status = 'visit'
    session.commit()

def addHotspot(session: Session, tripId: int, hotspotId: int) -> TripHotspot:
    tripHotspot = TripHotspot(tripId=tripId, hotspotId=hotspotId)
    session.add(tripHotspot)
    session.commit()

    return tripHotspot