from datetime import datetime
import requests

from config import *

from models.Hotspots import Hotspot

def find_hotspots(session, lat: float, lng: float, dist: int):

    url = f"https://api.ebird.org/v2/ref/hotspot/geo?fmt=json&back=30&lat={lat}&lng={lng}&dist={dist}"

    # get json data from url
    response = requests.get(url, headers = {"X-eBirdApiToken": EBIRD_API_KEY})

    # sort response by number of species
    response = sorted(response.json(), key=lambda x: x['numSpeciesAllTime'], reverse=True)

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