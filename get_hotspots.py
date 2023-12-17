from datetime import datetime
import requests

from sqlalchemy.orm import Session

from config import *

from models.base import init_engine
from models.hotspots import Hotspot

MONTH = 12
FREQ_MIN = 8

lat = -33.61
lng = 150.46
dist = 30

url = f"https://api.ebird.org/v2/ref/hotspot/geo?fmt=json&back=14&lat={lat}&lng={lng}&dist={dist}"

# get json data from url
response = requests.get(url, headers = {"X-eBirdApiToken": API_KEY})

# sort response by number of species
response = sorted(response.json(), key=lambda x: x['numSpeciesAllTime'], reverse=True)

engine = init_engine()
with Session(engine) as session:

    for row in response:
        hotspot = session.query(Hotspot).filter(Hotspot.locId == row['locId']).first()
        if hotspot:
            # If hotspot already exists, update it
            hotspot.name = row['locName'][:64]
            hotspot.numSpeciesAllTime = row['numSpeciesAllTime']
            hotspot.updatedAt = datetime.now()
            session.commit()
        else:
            # Create new hotspot
            hotspot = Hotspot(
                name=row['locName'][:64],
                locId=row['locId'],
                latitude=row['lat'],
                longitude=row['lng'],
                numSpeciesAllTime=row['numSpeciesAllTime'],
                createdAt=datetime.now(),
                updatedAt=datetime.now()
            )
            session.add(hotspot)
            session.commit()
