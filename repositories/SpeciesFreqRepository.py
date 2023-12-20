
from sqlalchemy.orm import Session

from models.Species import Species


def storeSpeciesFreq(session: Session, hotspotId: int, speciesId: int, freq: int, month: int):
    from models.SpeciesFreq import SpeciesFreq

    speciesFreq = SpeciesFreq(speciesId=speciesId, freq=freq, month=month, hotspotId=hotspotId)
    session.add(speciesFreq)

def getSpeciesFreqs(session: Session, hotspotId: int, month: int, freq: int = None) -> list:
    from models.SpeciesFreq import SpeciesFreq

    speciesFreqs = session.query(SpeciesFreq)\
        .filter(SpeciesFreq.hotspotId == hotspotId)\
        .filter(SpeciesFreq.month == month)
    if freq:
        speciesFreqs = speciesFreqs.filter(SpeciesFreq.freq >= freq)
    speciesFreqs = speciesFreqs.join(SpeciesFreq.species)\
        .with_entities(Species.name, SpeciesFreq.freq)\
        .all()

    return speciesFreqs