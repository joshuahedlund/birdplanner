from datetime import datetime

import pandas as pd
import requests

from sqlalchemy.orm import Session
from typing import Optional

from models.Hotspots import Hotspot
from repositories.SpeciesFreqRepository import storeSpeciesFreq
from repositories.SpeciesRepository import getSpeciesIds, storeSpecies


def parseSpeciesList(tbody: str, month: int, freqMin: float) -> pd.DataFrame:
    speciesList = []

    for row in tbody.split('<tr class="rC')[1:]:

        td = row.split('</td>')[0]

        if '<a ' not in td:
            # probably domestic/hybrid species
            continue

        speciesName = td.split('<a ')[-1].split('">')[1].split('</a>')[0].strip()
        speciesUrlId = td.split('<a ')[-1].split('href="/species/')[1].split('"')[0]

        # Get chart from month column
        lastTd = row.split('</td>')[2 + month]

        # Get class for every div in lastTd
        freqSum = 0
        for div in lastTd.split('<div class="')[1:]:
            divClass = div.split('"')[0]
            if divClass in ('bu', 'sp'):  # insufficient data
                continue
            freqSum += int(divClass[1])
        freqAvg = freqSum / 4

        if freqAvg >= freqMin:
            speciesList.append((freqAvg, speciesName, speciesUrlId))

    # Convert to df
    speciesList = pd.DataFrame(speciesList, columns=['freq', 'species', 'urlId'])

    return speciesList


def getTbodyFromLocID(LocID: str) -> Optional[str]:
    print("getting data from ebird.org")
    url = "https://ebird.org/barchart?r={}&byr=2018&eyr=2023".format(LocID)
    html = requests.get(url).text

    # Parse html to table class="barChart"
    table = html.split('<table class="barChart')[1].split('</table>')[0]
    tbody = table.split('<tbody>')[1].split('</tbody>')[0]

    return tbody

def retrieveSpeciesFreqs(session: Session, hotspotId: int) -> None:

    hotspot = session.query(Hotspot).get(hotspotId)

    tbody = getTbodyFromLocID(hotspot.locId)
    if not tbody:
        return None

    for month in range(1, 13):
        speciesList = parseSpeciesList(tbody, month, 0.1)

        # Get species ids that already exist from species names
        speciesNameMap = getSpeciesIds(session, speciesList['species'].tolist())

        for row in speciesList.itertuples(index=False):
            # Get or store species id
            speciesRow = speciesNameMap.loc[speciesNameMap['name'] == row.species, 'id']
            if not speciesRow.empty:
                speciesId = speciesRow.iloc[0]
            else:
                speciesId = storeSpecies(session, row.species, row.urlId)

            # Save species frequency
            storeSpeciesFreq(session, hotspot.id, speciesId, row.freq * 10, month)

    # Update hotspot speciesFreqUpdatedAt
    hotspot.speciesFreqUpdatedAt = datetime.now()

    session.commit()