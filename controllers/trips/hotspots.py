
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app as app
)
from controllers.auth import login_required

from get_hotspots import find_hotspots

from repositories.HotspotRepository import *
from repositories.SpeciesFreqRepository import getSpeciesFreqs, getTargetSpeciesListForHotspots
from repositories.TripRepository import getTrip, getSubTripsForTrip
from repositories.UserSpeciesRepository import getUserSpeciesList


bp = Blueprint('trips-hotspots', __name__)

@bp.route('/trip/<int:id>/hotspots')
@login_required
def showHotspots(id: int):
    db = app.db
    trip = getTrip(db.session, id)
    if trip is None or trip.userId != g.user.id:
        flash(f"Trip not found.")
        return redirect(url_for("home.home"))

    subTrips = getSubTripsForTrip(db.session, id)

    tripHotspots = getAllHotspotsForTrip(db.session, id, trip.month, trip.freqMin, g.user.id)

    skipHotspots = [h for h in tripHotspots if h.status == 'skip']
    tripHotspots = [h for h in tripHotspots if h.status != 'skip']
    moreHotspots = getTopHotspotsNotConsideredForTrip(
        db.session,
        g.user.id,
        id,
        trip.month,
        minFreq=trip.freqMin,
        lat=trip.latitude,
        lng=trip.longitude,
        dist=trip.radiusKm,
        limit=80
    )
    if len(subTrips) > 0:
        for subTrip in subTrips:
            #TODO see if some queries can be combined
            subTripHotspots = getAllHotspotsForTrip(db.session, subTrip.id, subTrip.month, subTrip.freqMin, g.user.id)
            tripHotspots = tripHotspots + subTripHotspots
            skipHotspots = skipHotspots + [h for h in subTripHotspots if h.status == 'skip']
            moreHotspots = moreHotspots + getTopHotspotsNotConsideredForTrip(
                db.session,
                g.user.id,
                trip.id,
                subTrip.month,
                minFreq=subTrip.freqMin,
                lat=subTrip.latitude,
                lng=subTrip.longitude,
                dist=subTrip.radiusKm,
                limit=80
            )
        # Filter duplicates
        tripHotspots = list({h.id: h for h in tripHotspots}.values())
        skipHotspots = list({h.id: h for h in skipHotspots}.values())
        moreHotspots = list({h.id: h for h in moreHotspots}.values())

    userSpeciesList = getUserSpeciesList(db.session, g.user.id)
    userSpeciesIds = [s.speciesId for s in userSpeciesList]

    targetSpeciesList = getTargetSpeciesListForHotspots(db.session, [h.id for h in tripHotspots], trip.month, trip.freqMin, g.user.id)
    targetSpeciesIds = [s.speciesId for s in targetSpeciesList]
    uniqueTargetCount = len(targetSpeciesIds)

    skipHotspotWrap = []
    for hotspot in skipHotspots:
        speciesFreqs = getSpeciesFreqs(db.session, hotspot.id, trip.month, freq=trip.freqMin) #todo combine query
        surplusSpeciesIds = [s.id for s in speciesFreqs if s.id not in targetSpeciesIds and s.id not in userSpeciesIds]
        skipHotspotWrap.append({'hotspot': hotspot, 'surplusSpeciesCount': len(surplusSpeciesIds)})
        skipHotspotWrap = sorted(skipHotspotWrap, key=lambda x: x['surplusSpeciesCount'], reverse=True)

    moreHotspotWrap = []
    for hotspot in moreHotspots:
        speciesFreqs = getSpeciesFreqs(db.session, hotspot.id, trip.month, freq=trip.freqMin) #todo combine query
        surplusSpeciesIds = [s.id for s in speciesFreqs if s.id not in targetSpeciesIds and s.id not in userSpeciesIds]
        moreHotspotWrap.append({'hotspot': hotspot, 'surplusSpeciesCount': len(surplusSpeciesIds)})
        moreHotspotWrap = sorted(moreHotspotWrap, key=lambda x: x['surplusSpeciesCount'], reverse=True)

    return render_template(
        'trips/hotspots.html',
        page='hotspots',
        trip=trip,
        tripHotspots=tripHotspots,
        skipHotspots=skipHotspotWrap,
        moreHotspots=moreHotspotWrap,
        uniqueTargetCount=uniqueTargetCount
    )


@bp.route('/trip/<int:id>/find-hotspots', methods=["POST"])
@login_required
def findHotspots(id: int):
    db = app.db
    trip = getTrip(db.session, id)
    if trip is None or trip.userId != g.user.id:
        return redirect(url_for("home.home"))

    dist = trip.radiusKm
    find_hotspots(db.session, trip.latitude, trip.longitude, dist)

    return redirect(url_for("trips-hotspots.showHotspots", id=id))


@bp.route('/trip/<int:id>/skip/<int:hotspotId>')
@login_required
def skip(id, hotspotId):
    db = app.db
    trip = getTrip(db.session, id)
    if trip is None or trip.userId != g.user.id:
        flash(f"Trip not found.")
        return redirect(url_for("home.home"))

    skipHotspot(db.session, id, hotspotId)
    return redirect(url_for("trips-hotspots.showHotspots", id=id))


@bp.route('/trip/<int:id>/visit/<int:hotspotId>')
@login_required
def visit(id, hotspotId):
    db = app.db
    trip = getTrip(db.session, id)
    if trip is None or trip.userId != g.user.id:
        flash(f"Trip not found.")
        return redirect(url_for("home.home"))

    visitHotspot(db.session, id, hotspotId)
    return redirect(url_for("trips-hotspots.showHotspots", id=id))

@bp.route('/trip/<int:id>/add/<int:hotspotId>')
@login_required
def add(id, hotspotId):
    db = app.db
    trip = getTrip(db.session, id)
    if trip is None or trip.userId != g.user.id:
        flash(f"Trip not found.")
        return redirect(url_for("home.home"))

    addHotspot(db.session, id, hotspotId)
    return redirect(url_for("trips-hotspots.showHotspots", id=id))