from sqlalchemy.orm import Session

from models.base import init_engine

from repositories.HotspotRepository import getTopHotspotsNearby

from topbars import getTopSpecies

MONTH = 12
FREQ_MIN = 70

lat = 34.0536909
lng = -118.242766


engine = init_engine()
with Session(engine) as session:
    # Get hotspots for trip
    hotspots = getTopHotspotsNearby(session, lat, lng, 50)

    curated_hotspots = []
    curated_species = []
    for hotspot in hotspots:
        print(hotspot.name, hotspot.numSpeciesAllTime)

        speciesList = getTopSpecies(hotspot, month=MONTH, freq=FREQ_MIN)

        # surplusSpeciesList = speciesList[~speciesList['species'].isin(curated_species)]
        # curated_species.extend(surplusSpeciesList['species'])
        #
        # print(len(surplusSpeciesList))
        # if len(surplusSpeciesList) > 0:
        #     print(surplusSpeciesList)
        #
        # curated_hotspots.append({
        #     'name': hotspot.name,
        #     'species': speciesList,
        #     'speciesCount': len(speciesList),
        #     'surplus': surplusSpeciesList,
        #     'surplusCount': len(surplusSpeciesList)
        # })