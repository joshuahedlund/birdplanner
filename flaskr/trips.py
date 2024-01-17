from datetime import datetime

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app as app
)
from flaskr.auth import login_required
import pandas as pd

from models.Trips import Trip

from repositories.HotspotRepository import *
from repositories.SpeciesFreqRepository import getSpeciesFreqs, getUniqueTargetCount
from repositories.TripRepository import getTrip

bp = Blueprint('trips', __name__)


@bp.route('/trip/<int:id>')
@login_required
def show(id: int):
    FREQ_MIN = 70  # todo make this a parameter

    db = app.db
    trip = getTrip(db.session, id)
    if trip is None or trip.userId != g.user.id:
        flash(f"Trip not found.")
        return redirect(url_for("home.home"))

    tripHotspots = getAllHotspotsForTrip(db.session, id, trip.month, FREQ_MIN)

    skipHotspots = [h for h in tripHotspots if h.status == 'skip']
    tripHotspots = [h for h in tripHotspots if h.status != 'skip']
    moreHotspots = getTopHotspotsNotConsideredForTrip(
        db.session,
        id,
        trip.month,
        minFreq=FREQ_MIN,
        lat=trip.latitude,
        lng=trip.longitude,
        dist=0.5,
        limit=50
    )

    uniqueTargetCount = getUniqueTargetCount(db.session, [h.id for h in tripHotspots], trip.month, FREQ_MIN)

    return render_template(
        'trips/show.html',
        trip=trip,
        tripHotspots=tripHotspots,
        skipHotspots=skipHotspots,
        moreHotspots=moreHotspots,
        uniqueTargetCount=uniqueTargetCount
    )


@bp.route('/trip/new')
@login_required
def create():
    trip = Trip()
    trip.id = 0
    trip.name = ''
    trip.latitude = ''
    trip.longitude = ''
    trip.month = 0
    trip.year = ''
    return render_template('trips/edit.html', trip=trip)


@bp.route('/trip/store', methods=('GET', 'POST'))
@login_required
def store():
    if request.method != 'POST':
        return redirect(url_for("trips.create"))

    db = app.db

    trip = Trip()

    if request.form['name'] == '':
        flash(f"Name is required.")
        return redirect(url_for("trips.create"))

    if request.form['latitude'] == '' or request.form['longitude'] == '':
        flash(f"Latitude and longitude are required.")
        return redirect(url_for("trips.create"))

    trip.name = request.form['name']
    trip.month = request.form['month']
    trip.year = request.form['year']
    trip.latitude = request.form['latitude']
    trip.longitude = request.form['longitude']

    trip.userId = g.user.id
    trip.createdAt = datetime.now()
    trip.updatedAt = datetime.now()

    db.session.add(trip)
    flash(f"Trip created.")

    db.session.commit()

    return redirect(url_for("trips.show", id=trip.id))

@bp.route('/trip/<int:id>/edit')
@login_required
def edit(id: int):
    db = app.db
    trip = getTrip(db.session, id)
    if trip is None or trip.userId != g.user.id:
        flash(f"Trip not found.")
        return redirect(url_for("home.home"))

    return render_template('trips/edit.html', trip=trip)


@bp.route('/trip/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id: int):
    if request.method != 'POST':
        return redirect(url_for("trips.show", id=id))

    db = app.db
    trip = getTrip(db.session, id)
    if trip is None or trip.userId != g.user.id:
        return redirect(url_for("home.home"))

    if request.form['name'] == '':
        flash(f"Name is required.")
        return redirect(url_for("trips.edit", id=id))

    if request.form['latitude'] == '' or request.form['longitude'] == '':
        flash(f"Latitude and longitude are required.")
        return redirect(url_for("trips.edit", id=id))


    trip.name = request.form['name']
    trip.month = request.form['month']
    trip.year = request.form['year']
    trip.latitude = request.form['latitude']
    trip.longitude = request.form['longitude']
    trip.updatedAt = datetime.now()
    db.session.commit()

    return redirect(url_for("trips.show", id=id))


@bp.route('/trip/<int:id>/matrix')
@login_required
def matrix(id: int):
    FREQ_MIN = 70  # todo make this a parameter

    db = app.db
    trip = getTrip(db.session, id)
    if trip is None or trip.userId != g.user.id:
        flash(f"Trip not found.")
        return redirect(url_for("home.home"))

    hotspots = getTripHotspotsWithFreqs(db.session, id)
    curatedHotspots = []
    for hotspot in hotspots:
        speciesFreqs = getSpeciesFreqs(db.session, hotspot.id, trip.month)
        speciesList = pd.DataFrame(speciesFreqs, columns=['species', 'freq'])
        curatedHotspots.append(
            {'name': '<a target="_blank" href="https://ebird.org/hotspot/' + hotspot.locId + '">' + hotspot.name + '</a>',
             'species': speciesList,
             'count': len(speciesList)
             }
        )

    # sort hotspots by count
    curatedHotspots = sorted(curatedHotspots, key=lambda x: x['count'], reverse=True)

    # build dataframe of hotspots grouped by species
    hotspotMatrix = pd.DataFrame()
    for hotspot in curatedHotspots:
        # Rename freq column as the hotspot name
        hotspot['species'] = hotspot['species'].rename(columns={'freq': hotspot['name']})

        # join on species
        if hotspotMatrix.empty:
            hotspotMatrix = hotspot['species']
        else:
            hotspotMatrix = hotspotMatrix.merge(hotspot['species'], how='outer', on='species')

    # move species column to first column of dataframe
    hotspotMatrix = hotspotMatrix[['species'] + [col for col in hotspotMatrix.columns if col != 'species']]
    hotspotMatrix.rename(columns={'species': 'Species'}, inplace=True)

    # filter out species with a maximum value less than FREQ_MIN
    hotspotMatrix = hotspotMatrix[hotspotMatrix.iloc[:, 1:].max(axis=1) >= FREQ_MIN]

    # resort index starting with 1
    hotspotMatrix.index = range(1, len(hotspotMatrix) + 1)

    return render_template(
        'trips/matrix.html',
        trip=trip,
        matrixTable=hotspotMatrix.to_html(na_rep='', classes="table", float_format=lambda x: '%.0f' % x, escape=False)
    )


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