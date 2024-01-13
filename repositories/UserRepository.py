import os
import sys
sys.path.append(os.path.dirname(os.getcwd()))

from datetime import datetime

from models.Users import User


def storeUser(session, email, password):
    user = User(email=email, password=password)
    user.createdAt = datetime.now()
    user.updatedAt = datetime.now()

    session.add(user)
    session.commit()

    return user


def getUserByEmail(session, email) -> User:
    user = session.query(User) \
        .filter(User.email == email) \
        .first()

    return user


def getUserById(session, userId) -> User:
    return session.query(User).get(userId)