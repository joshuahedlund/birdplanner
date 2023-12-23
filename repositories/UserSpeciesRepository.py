from sqlalchemy.orm.session import Session

from models.base import init_engine
from models.Species import Species
from models.UserSpecies import UserSpecies


def getUserSpeciesNames(userId: int) -> list:
    with Session(init_engine()) as session:
        userSpecies = session.query(UserSpecies) \
            .filter(UserSpecies.userId == userId) \
            .join(UserSpecies.species) \
            .with_entities(Species.name) \
            .all()

    speciesNames = [x[0] for x in userSpecies]

    return speciesNames