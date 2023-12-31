import os
import sys
sys.path.append(os.path.dirname(os.getcwd()))

from datetime import datetime
from sqlalchemy.orm import Session

from models.Trips import Trip


def getTrip(session: Session, tripId: int) -> Trip:

    trip = session.query(Trip) \
        .filter(Trip.id == tripId) \
        .first()

    return trip


def getTripsForUser(session: Session, userId: int) -> list:
        trips = session.query(Trip) \
            .filter(Trip.userId == userId) \
            .all()

        return trips


def storeTrip(session: Session, userId: int, name: str, lat: float, lng: float, year: int, month: int) -> Trip:

    trip = Trip(userId=userId, name=name, latitude=lat, longitude=lng, year=year, month=month)
    trip.createdAt = datetime.now()
    trip.updatedAt = datetime.now()
    session.add(trip)
    session.commit()

    return trip