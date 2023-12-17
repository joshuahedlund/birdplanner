import requests
import pandas as pd

#LocID = "L2198738"


def getTopSpecies(LocID, month, freqMin):

    # Load text from file if it exists
    try:
        tbody = open("data/{}.html".format(LocID)).read()
    except:
        print("getting data from ebird.org")
        url = "https://ebird.org/barchart?r={}&byr=2018&eyr=2023".format(LocID)
        html = requests.get(url).text

        # Parse html to table class="barChart"
        table = html.split('<table class="barChart')[1].split('</table>')[0]
        tbody = table.split('<tbody>')[1].split('</tbody>')[0]

        # Save text to file
        open("data/{}.html".format(LocID), "w").write(tbody)

    if not tbody:
        print("tbody is empty")
        return None

    speciesList = []

    for row in tbody.split('<tr class="rC')[1:]:

        td = row.split('</td>')[0]
        if '<a ' not in td:
            # probably domestic/hybrid species
            continue

        speciesName = td.split('<a ')[-1].split('">')[1].split('</a>')[0].strip()

        # Get December charts from last td
        lastTd = row.split('</td>')[2 + month]

        # Get class for every div in lastTd
        freqSum = 0
        for div in lastTd.split('<div class="')[1:]:
            divClass = div.split('"')[0]
            if divClass == 'sp': # No sightings
                continue
            freqSum += int(divClass[1])
        freqAvg = freqSum / 4

        if (freqAvg >= freqMin):
            speciesList.append((freqAvg, speciesName))

    # Convert to df
    speciesList = pd.DataFrame(speciesList, columns=['freq', 'species'])

    # Sort by frequency
    speciesList = speciesList.sort_values(by=['freq'], ascending=False, ignore_index=True)

    return speciesList
