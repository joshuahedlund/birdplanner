import calendar

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app as app
)

from repositories.HotspotRepository import getHotspotIdsForTrip
from repositories.SpeciesFreqRepository import getTopHotspotsForSpecies
from repositories.SpeciesRepository import getAllSpecies, getSpecies
from repositories.TripRepository import getTrip

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

    TRIP_ID = 1 #todo get from user
    trip = getTrip(db.session, TRIP_ID)
    trip.month_name = calendar.month_name[trip.month]

    hotspots = getTopHotspotsForSpecies(
        db.session,
        species.id,
        trip.month,
        limit=20,
        lat=trip.latitude,
        lng=trip.longitude
    )

    tripHotspotIds = getHotspotIdsForTrip(db.session, TRIP_ID)

    return render_template(
        'species/show.html',
        name=species.name,
        trip=trip,
        hotspots=hotspots,
        tripHotspotIds=tripHotspotIds
    )
