import pandas as pd
from sqlalchemy.orm import Session

from get_species_freq import retrieveSpeciesFreqs
from models.base import init_engine
from repositories.SpeciesFreqRepository import getSpeciesFreqs


def getTopSpecies(hotspotId: int, month: int, freq: int = None, retrieve: bool = False) -> pd.DataFrame:
    if retrieve:
        print("retrieving")
        retrieveSpeciesFreqs(hotspotId)
    with Session(init_engine()) as session:
        speciesFreqs = getSpeciesFreqs(session, hotspotId, month, freq)

    speciesList = pd.DataFrame(speciesFreqs, columns=['species', 'freq'])

    # Sort by frequency
    speciesList = speciesList.sort_values(by=['freq'], ascending=False, ignore_index=True)

    return speciesList
