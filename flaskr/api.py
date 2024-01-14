from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app as app
)
from flaskr.auth import login_required

from repositories.HotspotRepository import getHotspotIdsForTrip
from repositories.SpeciesRepository import getTripSpeciesByNameFragment, getSpecies
from repositories.SpeciesFreqRepository import getTopHotspotsForSpecies
from repositories.TripRepository import getTrip

bp = Blueprint('api', __name__, url_prefix='/api')


@bp.route('/trip/<int:id>/species-search')
@login_required
def speciesSearch(id: int):
    db = app.db
    trip = getTrip(db.session, id)
    if trip is None or trip.userId != g.user.id:
        flash(f"Trip not found.")
        return []

    search = request.args.get('query')
    if search is None or len(search) < 3:
        return []

    species = getTripSpeciesByNameFragment(db.session, search, trip.month, trip.latitude, trip.longitude)

    return [{'id': s.id, 'name': s.name} for s in species]


@bp.route('/trip/<int:tripId>/species/<int:speciesId>/hotspots')
@login_required
def speciesHotspots(tripId: int, speciesId: int):
    db = app.db
    trip = getTrip(db.session, tripId)
    if trip is None or trip.userId != g.user.id:
        return []

    species = getSpecies(db.session, speciesId)
    if species is None:
        return []

    hotspots = getTopHotspotsForSpecies(db.session, speciesId, month=trip.month, lat=trip.latitude, lng=trip.longitude)
    tripHotspotIds = getHotspotIdsForTrip(db.session, tripId)

    return [{'freq': h.freq, 'locId': h.locId, 'name': h.name, 'isInTrip': h.id in tripHotspotIds} for h in hotspots]