from flask import (
    Blueprint, flash, g, request, current_app as app
)
from controllers.auth import login_required

from get_species_freq import retrieveSpeciesFreqs

from models.Hotspots import Hotspot

from repositories.HotspotRepository import getHotspotIdsForTrip
from repositories.SpeciesRepository import getTripSpeciesByNameFragment, getSpecies
from repositories.SpeciesFreqRepository import getTopHotspotsForSpecies, getUniqueTargetCount
from repositories.TripRepository import getTrip, getSubTripsForTrip

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

    subTrips = getSubTripsForTrip(db.session, tripId)
    allTrips = [trip] + subTrips

    hotspots = getTopHotspotsForSpecies(
        db.session,
        speciesId,
        month=trip.month,
        zones=[{'lat': trip.latitude, 'lng': trip.longitude, 'radiusKm': trip.radiusKm} for trip in allTrips]
    )
    tripHotspotIds = getHotspotIdsForTrip(db.session, tripId)

    return [{'freq': h.freq, 'locId': h.locId, 'name': h.name, 'isInTrip': h.id in tripHotspotIds} for h in hotspots]


@bp.route('/trip/<int:tripId>/hotspot/<int:hotspotId>/get-freqs')
@login_required
def getFreqs(tripId: int, hotspotId: int):
    FREQ_MIN = 70
    db = app.db
    hotspot = db.session.query(Hotspot).get(hotspotId)
    if hotspot is None:
        return 'ERR'

    retrieveSpeciesFreqs(hotspot.id)

    #Get target count
    trip = getTrip(db.session, tripId)
    count = getUniqueTargetCount(db.session, [hotspotId], trip.month, FREQ_MIN)
    return str(count)