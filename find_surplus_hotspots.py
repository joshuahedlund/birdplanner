import pandas as pd
from sqlalchemy.orm import Session

from models.base import init_engine
from repositories.HotspotRepository import getTopHotspotsNotConsideredForTrip
from repositories.TripRepository import getTrip
from topbars import getTopSpecies

TRIP_ID = 1
FREQ_MIN = 70

engine = init_engine()

# Load month from trip
with Session(engine) as session:
    trip = getTrip(session, TRIP_ID)

if not trip:
    print('Trip not found.')
    exit()

# Load species from trip matrix
tripMatrix = pd.read_csv(f'data/tripmatrix/trip{TRIP_ID}_{FREQ_MIN}.csv')

# Load top hotspots not already included in trip matrix
with Session(engine) as session:
    hotspots = getTopHotspotsNotConsideredForTrip(session, TRIP_ID, trip.latitude, trip.longitude)

if not hotspots:
    print('No hotspots found')
    exit()

for hotspot in hotspots:
    shouldRetrieve = hotspot.speciesFreqUpdatedAt is None
    speciesList = getTopSpecies(hotspot.id, month=trip.month, freq=FREQ_MIN, retrieve=shouldRetrieve)

    # Find species in speciesList that are not in tripMatrix
    speciesList = speciesList[~speciesList['species'].isin(tripMatrix['species'])]
    print(hotspot.name, len(speciesList))
    if len(speciesList) > 0:
        print(speciesList)