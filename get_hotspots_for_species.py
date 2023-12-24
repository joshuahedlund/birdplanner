from sqlalchemy.orm import Session

from models.base import init_engine
from repositories.SpeciesFreqRepository import getTopHotspotsForSpecies

SPECIES_ID = 199
MONTH = 12

lat = -33.87
lng = 151.21

engine = init_engine()
with Session(engine) as session:
    hotspots = getTopHotspotsForSpecies(session, SPECIES_ID, MONTH, limit=10, lat=lat, lng=lng)
    print(hotspots)