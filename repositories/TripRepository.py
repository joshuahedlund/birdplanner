from datetime import datetime
import os
import sys
sys.path.append(os.path.dirname(os.getcwd()))

from sqlalchemy.orm import Session

from models.trips import Trip


def getTrip(session: Session, tripId: int) -> Trip:

    trip = session.query(Trip) \
        .filter(Trip.id == tripId) \
        .first()

    return trip


def storeTrip(session: Session, userId: int, name: str, lat: float, lng: float, year: int, month: int) -> Trip:

    trip = Trip(userId=userId, name=name, latitude=lat, longitude=lng, year=year, month=month)
    trip.createdAt = datetime.now()
    trip.updatedAt = datetime.now()
    session.add(trip)
    session.commit()

    return trip