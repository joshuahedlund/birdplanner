from sqlalchemy.orm.session import Session

from models.base import init_engine
from models.Species import Species
from models.UserSpecies import UserSpecies


def getUserSpeciesList(session: Session, userId: int) -> list:
    userSpecies = session.query(UserSpecies) \
        .filter(UserSpecies.userId == userId) \
        .join(UserSpecies.species) \
        .with_entities(UserSpecies.id, UserSpecies.speciesId, Species.name) \
        .all()

    return userSpecies


def getUserSpecies(session: Session, userId: int, id: int) -> UserSpecies:
    userSpecies = session.query(UserSpecies) \
        .filter(UserSpecies.userId == userId) \
        .filter(UserSpecies.id == id) \
        .first()

    return userSpecies


def storeUserSpecies(session: Session, userId: int, speciesId: int) -> None:
    userSpecies = UserSpecies(userId=userId, speciesId=speciesId)
    session.add(userSpecies)
    session.commit()



# deprecated - only used by CLI script
def getUserSpeciesNames(userId: int) -> list:
    with Session(init_engine()) as session:
        userSpecies = session.query(UserSpecies) \
            .filter(UserSpecies.userId == userId) \
            .join(UserSpecies.species) \
            .with_entities(Species.name) \
            .all()

    speciesNames = [x[0] for x in userSpecies]

    return speciesNames