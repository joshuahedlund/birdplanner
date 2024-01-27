import os
import sys
sys.path.append(os.path.dirname(os.getcwd()))

from datetime import datetime
from sqlalchemy import or_
from sqlalchemy.orm import Session

from models.Trips import Trip


def getTrip(session: Session, tripId: int) -> Trip:
    return session.query(Trip).get(tripId)


def getTripsForUser(session: Session, userId: int) -> list:
        trips = session.query(Trip) \
            .filter(Trip.userId == userId) \
            .filter(or_(Trip.parentTripId == None, Trip.parentTripId == 0)) \
            .order_by(Trip.year.asc(), Trip.month.asc(), Trip.name.asc()) \
            .all()

        return trips

def getSubTripsForTrip(session: Session, tripId: int) -> list:
    trips = session.query(Trip) \
        .filter(Trip.parentTripId == tripId) \
        .order_by(Trip.id.asc()) \
        .all()

    return trips


def storeTrip(session: Session, userId: int, name: str, lat: float, lng: float, year: int, month: int) -> Trip:

    trip = Trip(userId=userId, name=name, latitude=lat, longitude=lng, year=year, month=month)
    trip.createdAt = datetime.now()
    trip.updatedAt = datetime.now()
    session.add(trip)
    session.commit()

    return trip