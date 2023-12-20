from sqlalchemy.orm import Session

from models.base import init_engine
from models.Hotspots import Hotspot
from models.TripHotspots import TripHotspot

from topbars import getTopSpecies

MONTH = 12
FREQ_MIN = 8
TRIP_ID = 1

engine = init_engine()
with Session(engine) as session:
    # Get hotspots for trip
    tripHotSpots = session.query(TripHotspot)\
        .filter(TripHotspot.tripId == TRIP_ID)\
        .with_entities(TripHotspot.hotspotId)\
        .all()
    hotspotIds = [x[0] for x in tripHotSpots]

    hotspots = session.query(Hotspot)\
        .filter(Hotspot.id.in_(hotspotIds))\
        .all()

    curated_hotspots = []
    for hotspot in hotspots:
        print(hotspot.name, hotspot.numSpeciesAllTime)

        speciesList = getTopSpecies(hotspot.id, MONTH, FREQ_MIN)
        curated_hotspots.append({'name': hotspot.name, 'species': speciesList, 'count': len(speciesList)})


    # sort hotspots by count
    curated_hotspots = sorted(curated_hotspots, key=lambda x: x['count'], reverse=True)
    topParkList = curated_hotspots[0]['species']

    # print top hotspot
    print(curated_hotspots[0]['name'], len(curated_hotspots[0]['species']))
    print('----------------')

    for hotspot in curated_hotspots[1:]:
        print(hotspot['name'])

        #Get species in this park that are not in top park
        speciesList = hotspot['species']
        speciesList = speciesList[~speciesList['species'].isin(topParkList['species'])]
        print(' surplus: ')
        print(speciesList)