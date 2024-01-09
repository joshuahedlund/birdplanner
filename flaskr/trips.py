from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app as app
)

from flaskr.auth import login_required
from repositories.HotspotRepository import *
from repositories.TripRepository import getTrip

bp = Blueprint('trips', __name__)

@bp.route('/trip/<int:id>')
@login_required
def show(id):
    db = app.db
    trip = getTrip(db.session, id)
    if trip is None or trip.userId != g.user.id:
        flash(f"Trip not found.")
        return redirect(url_for("home.home"))

    tripHotspots = getHotspotsForTrip(db.session, id)

    skipHotspots = [h for h in tripHotspots if h.status == 'skip']
    tripHotspots = [h for h in tripHotspots if h.status != 'skip']
    moreHotspots = getTopHotspotsNotConsideredForTrip(
        db.session,
        id,
        lat=trip.latitude,
        lng=trip.longitude,
        dist=0.3,
        limit=50
    )

    return render_template(
        'trips/show.html',
        trip=trip,
        tripHotspots=tripHotspots,
        skipHotspots=skipHotspots,
        moreHotspots=moreHotspots
    )


@bp.route('/trip/<int:id>/matrix')
@login_required
def matrix(id):
    db = app.db
    trip = getTrip(db.session, id)
    if trip is None or trip.userId != g.user.id:
        flash(f"Trip not found.")
        return redirect(url_for("home.home"))

    return render_template('trips/matrix.html', trip=trip)


@bp.route('/trip/<int:id>/species')
@login_required
def species(id):
    db = app.db
    trip = getTrip(db.session, id)
    if trip is None or trip.userId != g.user.id:
        flash(f"Trip not found.")
        return redirect(url_for("home.home"))

    return render_template('trips/species.html', trip=trip)


@bp.route('/trip/<int:id>/skip/<int:hotspotId>')
@login_required
def skip(id, hotspotId):
    db = app.db
    trip = getTrip(db.session, id)
    if trip is None or trip.userId != g.user.id:
        flash(f"Trip not found.")
        return redirect(url_for("home.home"))

    skipHotspot(db.session, id, hotspotId)
    return redirect(url_for("trips.show", id=id))


@bp.route('/trip/<int:id>/visit/<int:hotspotId>')
@login_required
def visit(id, hotspotId):
    db = app.db
    trip = getTrip(db.session, id)
    if trip is None or trip.userId != g.user.id:
        flash(f"Trip not found.")
        return redirect(url_for("home.home"))

    visitHotspot(db.session, id, hotspotId)
    return redirect(url_for("trips.show", id=id))

@bp.route('/trip/<int:id>/add/<int:hotspotId>')
@login_required
def add(id, hotspotId):
    db = app.db
    trip = getTrip(db.session, id)
    if trip is None or trip.userId != g.user.id:
        flash(f"Trip not found.")
        return redirect(url_for("home.home"))

    addHotspot(db.session, id, hotspotId)
    return redirect(url_for("trips.show", id=id))