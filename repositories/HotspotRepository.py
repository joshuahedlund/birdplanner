import os
import sys
sys.path.append(os.path.dirname(os.getcwd()))

from sqlalchemy.orm import Session
from sqlalchemy import func, or_

from models.Hotspots import Hotspot
from models.TripHotspots import TripHotspot


def getHotspotsForTrip(session: Session, tripId: int) -> list:
    hotspots = session.query(Hotspot) \
        .join(TripHotspot) \
        .filter(TripHotspot.tripId == tripId) \
        .order_by((or_(TripHotspot.status.is_(None), TripHotspot.status == 'visit')).desc()) \
        .order_by(Hotspot.numSpeciesAllTime.desc()) \
        .with_entities(Hotspot.id, Hotspot.locId, Hotspot.name, Hotspot.latitude, Hotspot.longitude, Hotspot.numSpeciesAllTime, TripHotspot.status) \
        .all()

    return hotspots

def getHotspotIdsForTrip(session: Session, tripId: int, ) -> list:
    tripHotSpots = session.query(TripHotspot) \
        .filter(TripHotspot.tripId == tripId) \
        .filter(or_(TripHotspot.status.is_(None), TripHotspot.status == 'visit')) \
        .with_entities(TripHotspot.hotspotId) \
        .all()
    hotspotIds = [x[0] for x in tripHotSpots]

    return hotspotIds

def getTopHotspotsNotConsideredForTrip(
        session: Session,
        tripId: int,
        lat: float,
        lng: float,
        limit: int=15,
        dist: float=0.15
    ) -> list:
    subquery = session.query(TripHotspot.hotspotId).filter(TripHotspot.tripId == tripId)

    hotspots = session.query(Hotspot) \
        .filter(Hotspot.id.notin_(subquery)) \
        .filter(func.abs(Hotspot.latitude - lat) < dist) \
        .filter(func.abs(Hotspot.longitude - lng) < dist) \
        .order_by(Hotspot.numSpeciesAllTime.desc()) \
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