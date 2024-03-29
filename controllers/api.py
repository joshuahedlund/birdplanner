from flask import (
    Blueprint, flash, g, request, current_app as app
)
from controllers.auth import login_required

from get_species_freq import retrieveSpeciesFreqs

from models.Hotspots import Hotspot
from models.Trips import Trip

from repositories.HotspotRepository import getHotspotIdsForTrip
from repositories.SpeciesRepository import getTripSpeciesByNameFragment, getSpecies
from repositories.SpeciesFreqRepository import getTopHotspotsForSpecies, getUniqueTargetCount
from repositories.TripRepository import getTrip, getSubTripsForTrip

bp = Blueprint('api', __name__, url_prefix='/api')


@bp.route('/species-search')
@login_required
def speciesSearch():
    db = app.db
    zones = []

    search = request.args.get('query')
    if search is None or len(search) < 3:
        return []

    month = int(request.args.get('month', default=0))

    tripId = int(request.args.get('tripId', default=0))
    if tripId > 0:
        trip = getTrip(db.session, tripId)
        if trip is None or trip.userId != g.user.id:
            flash(f"Trip not found.")
            return []

        month = trip.month

        subTrips = getSubTripsForTrip(db.session, tripId)
        allTrips = [trip] + subTrips

        zones = [{'lat': trip.latitude, 'lng': trip.longitude, 'radiusKm': trip.radiusKm} for trip in allTrips]

    species = getTripSpeciesByNameFragment(
        db.session,
        search,
        month=month,
        zones=zones
    )

    return [{'id': s.id, 'name': s.name} for s in species]


@bp.route('/hotspot-search/<int:speciesId>')
@login_required
def speciesHotspots(speciesId: int):
    db = app.db

    month = int(request.args.get('month', default=0))

    tripId = int(request.args.get('tripId', default=0))
    if tripId > 0:
        trip = getTrip(db.session, tripId)
        if trip is None or trip.userId != g.user.id:
            return []

        month = trip.month

        subTrips = getSubTripsForTrip(db.session, tripId)
        allTrips = [trip] + subTrips

        tripHotspotIds = getHotspotIdsForTrip(db.session, tripId)
    else:
        zone = Trip(
            latitude=float(request.args.get('lat')),
            longitude=float(request.args.get('lng')),
            radiusKm=int(request.args.get('radiusKm')),
        )
        allTrips = [zone]
        tripHotspotIds = []

    species = getSpecies(db.session, speciesId)
    if species is None:
        return []


    hotspots = getTopHotspotsForSpecies(
        db.session,
        speciesId,
        month=month,
        zones=[{'lat': trip.latitude, 'lng': trip.longitude, 'radiusKm': trip.radiusKm} for trip in allTrips]
    )

    return [{'freq': h.freq, 'locId': h.locId, 'name': h.name, 'isInTrip': h.id in tripHotspotIds} for h in hotspots]


@bp.route('/trip/<int:tripId>/hotspot/<int:hotspotId>/get-freqs')
@login_required
def getFreqs(tripId: int, hotspotId: int):
    db = app.db
    hotspot = db.session.query(Hotspot).get(hotspotId)
    if hotspot is None:
        return 'ERR'

    retrieveSpeciesFreqs(db.session, hotspot.id)

    #Get target count
    trip = getTrip(db.session, tripId)
    count = getUniqueTargetCount(db.session, [hotspotId], trip.month, trip.freqMin, g.user.id)

    return str(count)