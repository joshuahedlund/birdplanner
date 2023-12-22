from sqlalchemy.orm import Session

import pandas as pd

from models.base import init_engine
from models.Hotspots import Hotspot
from repositories.HotspotRepository import getHotspotIds

from topbars import getTopSpecies

MONTH = 12
FREQ_MIN = 70
TRIP_ID = 1


with Session(init_engine()) as session:
    # Get hotspots for trip
    hotspotIds = getHotspotIds(session, TRIP_ID)

    hotspots = session.query(Hotspot)\
        .filter(Hotspot.id.in_(hotspotIds))\
        .all()

if not hotspots:
    print('No hotspots found for trip')
    exit()

curated_hotspots = []
for hotspot in hotspots:
    print(hotspot.name, hotspot.numSpeciesAllTime)

    shouldRetrieve = hotspot.speciesFreqUpdatedAt is None
    speciesList = getTopSpecies(hotspot.id, month=MONTH, retrieve=shouldRetrieve)
    curated_hotspots.append({'name': hotspot.name, 'species': speciesList, 'count': len(speciesList)})


# sort hotspots by count
curated_hotspots = sorted(curated_hotspots, key=lambda x: x['count'], reverse=True)

# build dataframe of hotspots grouped by species
hotspotMatrix = pd.DataFrame()
for hotspot in curated_hotspots:
    # Rename freq column as the hotspot name
    hotspot['species'] = hotspot['species'].rename(columns={'freq': hotspot['name']})

    # join on species
    if hotspotMatrix.empty:
        hotspotMatrix = hotspot['species']
    else:
        hotspotMatrix = hotspotMatrix.merge(hotspot['species'], how='outer', on='species')

# move species column to first column of dataframe
hotspotMatrix = hotspotMatrix[ ['species'] + [ col for col in hotspotMatrix.columns if col != 'species' ] ]

# filter out species with a maximum value less than FREQ_MIN
hotspotMatrix = hotspotMatrix[hotspotMatrix.iloc[:, 1:].max(axis=1) >= FREQ_MIN]

# fill NaN with 0
hotspotMatrix = hotspotMatrix.fillna(0)

print(hotspotMatrix)

# write to csv
hotspotMatrix.to_csv(f'data/tripmatrix/trip{TRIP_ID}_{FREQ_MIN}.csv', index=False)
