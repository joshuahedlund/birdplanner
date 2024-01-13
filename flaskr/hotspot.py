from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app as app
)
from flaskr.auth import login_required
from get_species_freq import retrieveSpeciesFreqs

bp = Blueprint('hotspot', __name__)

from models.Hotspots import Hotspot


@bp.route('/hotspot/<int:id>/get-freqs')
@login_required
def getFreqs(id):
    #TODO change to post and use ajax
    db = app.db
    hotspot = db.session.query(Hotspot).get(id)
    if hotspot is None:
        flash(f"Hotspot not found.")
        return redirect(url_for("home.home"))

    retrieveSpeciesFreqs(hotspot.id)
    return redirect(url_for("home.home"))