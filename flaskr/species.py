from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app as app
)



from repositories.SpeciesRepository import getAllSpecies, getSpecies

bp = Blueprint('species', __name__)


@bp.route('/species')
def index():
    db = app.db
    species = getAllSpecies(db.session)
    return render_template('species/index.html', species=species)


@bp.route('/species/<int:id>')
def show(id):
    db = app.db
    species = getSpecies(db.session, id)

    return render_template('species/show.html', name=species.name)
