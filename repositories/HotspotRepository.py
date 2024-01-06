import os
import sys
sys.path.append(os.path.dirname(os.getcwd()))

from sqlalchemy.orm import Session
from sqlalchemy import func, or_

def getHotspotIdsForTrip(session: Session, tripId: int, ) -> list:
    from models.TripHotspots import TripHotspot

    tripHotSpots = session.query(TripHotspot) \
        .filter(TripHotspot.tripId == tripId) \
        .filter(or_(TripHotspot.status.is_(None), TripHotspot.status == 'visit')) \
        .with_entities(TripHotspot.hotspotId) \
        .all()
    hotspotIds = [x[0] for x in tripHotSpots]

    return hotspotIds

def getTopHotspotsNotConsideredForTrip(session: Session, tripId: int, lat: float, lng: float) -> list:
    from models.Hotspots import Hotspot
    from models.TripHotspots import TripHotspot

    subquery = session.query(TripHotspot.hotspotId).filter(TripHotspot.tripId == tripId)

    hotspots = session.query(Hotspot) \
        .filter(Hotspot.id.notin_(subquery)) \
        .filter(func.abs(Hotspot.latitude - lat) < 0.15) \
        .filter(func.abs(Hotspot.longitude - lng) < 0.15) \
        .order_by(Hotspot.numSpeciesAllTime.desc()) \
        .limit(15) \
        .all()

    return hotspots

def getTopHotspotsNearby(session: Session, lat: float, lng: float, limit: int) -> list:
    from models.Hotspots import Hotspot

    hotspots = session.query(Hotspot) \
        .filter(func.abs(Hotspot.latitude - lat) < 0.6) \
        .filter(func.abs(Hotspot.longitude - lng) < 0.6) \
        .order_by(Hotspot.numSpeciesAllTime.desc()) \
        .limit(limit) \
        .all()

    return hotspots