import pandas as pd
import time
from sqlalchemy.orm import Session

from get_species_freq import retrieveSpeciesFreqs
from models.base import init_engine
from models.Hotspots import Hotspot
from repositories.SpeciesFreqRepository import getSpeciesFreqs


def getTopSpecies(hotspot: Hotspot, month: int, freq: int = None) -> pd.DataFrame:
    with Session(init_engine()) as session:
        if hotspot.speciesFreqUpdatedAt is None:
            time.sleep(1) # be kind to ebird
            retrieveSpeciesFreqs(session, hotspot.id)
        speciesFreqs = getSpeciesFreqs(session, hotspot.id, month, freq)

    speciesList = pd.DataFrame(speciesFreqs, columns=['speciesId', 'speciesName', 'freq'])

    # Sort by frequency
    speciesList = speciesList.sort_values(by=['freq'], ascending=False, ignore_index=True)

    return speciesList
