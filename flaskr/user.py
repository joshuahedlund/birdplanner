from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app as app
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
        return

    storeUserSpecies(app.db.session, g.user.id, id)

    return redirect(url_for("user.show")) #todo change to ajax and have FE refresh current page

@bp.route('/user/species/<int:id>/delete', methods=('GET',)) #todo change to post
@login_required
def removeSpecies(id: int):
    userSpecies = getUserSpecies(app.db.session, g.user.id, id)
    if userSpecies is None:
        flash(f"Species not found.")
        return redirect(url_for("user.show"))

    app.db.session.delete(userSpecies)
    app.db.session.commit()

    flash(f"Species deleted.")
    return redirect(url_for("user.show"))