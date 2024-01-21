from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app as app, Response
)
from flaskr.auth import login_required

from repositories.UserSpeciesRepository import *

bp = Blueprint('user', __name__)

@bp.route('/user')
@login_required
def show():
    userSpecies = getUserSpeciesList(app.db.session, g.user.id)

    return render_template('user/show.html', user=g.user, userSpecies=userSpecies)


@bp.route('/user/species/<int:id>/add', methods=('POST',))
@login_required
def addSpecies(id: int):
    userSpecies = getUserSpecies(app.db.session, g.user.id, id)
    if userSpecies is not None:
        return Response(status=404)

    storeUserSpecies(app.db.session, g.user.id, id)

    return Response(status=200)

@bp.route('/user/species/<int:id>/delete', methods=('POST',))
@login_required
def removeSpecies(id: int):
    userSpecies = getUserSpecies(app.db.session, g.user.id, id)
    if userSpecies is None:
        return Response(status=404)

    app.db.session.delete(userSpecies)
    app.db.session.commit()

    return Response(status=200)
