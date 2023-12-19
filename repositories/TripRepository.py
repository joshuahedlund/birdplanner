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