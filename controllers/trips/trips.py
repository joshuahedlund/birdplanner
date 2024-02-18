from datetime import datetime

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app as app
)
from controllers.auth import login_required
import pandas as pd

from models.Trips import Trip

from repositories.HotspotRepository import *
from repositories.SpeciesFreqRepository import getSpeciesFreqs
from repositories.TripRepository import getTrip, getSubTripsForTrip
from repositories.UserSpeciesRepository import getUserSpeciesList

bp = Blueprint('trips', __name__)


@bp.route('/trip/new')
@login_required
def create():
    trip = Trip()
    trip.id = 0
    trip.parentTripId = 0
    trip.name = ''
    trip.latitude = ''
    trip.longitude = ''
    trip.month = 0
    trip.year = ''
    trip.freqMin = 50
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

    parentTripId = int(request.form['parentTripId'])
    if parentTripId > 0:
        parentTrip = getTrip(db.session, parentTripId)
        if parentTrip is None or parentTrip.userId != g.user.id:
            parentTripId = 0

    trip.name = request.form['name']
    trip.month = request.form['month']
    trip.year = request.form['year']
    trip.radiusKm = request.form['radiusKm']
    trip.freqMin = request.form['freqMin']
    trip.latitude = request.form['latitude']
    trip.longitude = request.form['longitude']

    trip.parentTripId = parentTripId
    trip.userId = g.user.id
    trip.createdAt = datetime.now()
    trip.updatedAt = datetime.now()

    db.session.add(trip)

    if parentTripId > 0:
        flash(f"Secondary zone created.")
    else:
        flash(f"Trip created.")

    db.session.commit()

    return redirect(url_for("trips.settings", id=trip.parentTripId or trip.id))

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
        return redirect(url_for("trips.settings", id=id))

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
    trip.radiusKm = request.form['radiusKm']
    trip.freqMin = request.form['freqMin']
    trip.latitude = request.form['latitude']
    trip.longitude = request.form['longitude']
    trip.updatedAt = datetime.now()
    db.session.commit()

    return redirect(url_for("trips.settings", id=trip.parentTripId or trip.id))


@bp.route('/trip/<int:id>/sub/new')
@login_required
def createSub(id: int):
    db = app.db
    trip = getTrip(db.session, id)
    if trip is None or trip.userId != g.user.id:
        return redirect(url_for("home.home"))

    sub = Trip()
    sub.id = 0
    sub.parentTripId = id
    sub.name = ''
    sub.latitude = ''
    sub.longitude = ''
    sub.month = trip.month
    sub.year = trip.year
    sub.radiusKm = trip.radiusKm
    sub.freqMin = trip.freqMin

    return render_template('trips/edit.html', trip=sub)


@bp.route('/trip/<int:id>/settings')
@login_required
def settings(id: int):
    db = app.db
    trip = getTrip(db.session, id)
    subTrips = getSubTripsForTrip(db.session, id)

    if trip is None or trip.userId != g.user.id:
        flash(f"Trip not found.")
        return redirect(url_for("home.home"))

    return render_template(
        'trips/settings.html',
        page='settings',
        trip=trip,
        subTrips=subTrips
)


@bp.route('/trip/<int:id>/matrix')
@login_required
def matrix(id: int):
    db = app.db
    trip = getTrip(db.session, id)
    if trip is None or trip.userId != g.user.id:
        flash(f"Trip not found.")
        return redirect(url_for("home.home"))

    hotspots = getTripHotspotsWithFreqs(db.session, id)

    if len(hotspots) == 0:
        flash(f"Add hotspots to your trip to view species matrix.")
        return redirect(url_for("trips-hotspots.showHotspots", id=id))

    curatedHotspots = []
    speciesHashMap = {}
    for hotspot in hotspots:
        speciesFreqs = getSpeciesFreqs(db.session, hotspot.id, trip.month)
        speciesHashMap = {**speciesHashMap, **{s.id: s.name for s in speciesFreqs}}

        # make dataframe of species id and freqs but drop name
        speciesList = pd.DataFrame(speciesFreqs).drop(columns=['name'])
        speciesList = speciesList.rename(columns={'id': 'speciesId'})

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
            hotspotMatrix = hotspotMatrix.merge(hotspot['species'], how='outer', on='speciesId')

    # filter out species with a maximum value less than min freq
    hotspotMatrix = hotspotMatrix[hotspotMatrix.iloc[:, 1:].max(axis=1) >= trip.freqMin]

    # filter out species user has already seen
    excludeSpecies = getUserSpeciesList(db.session, trip.userId)
    excludeSpeciesIds = [s.speciesId for s in excludeSpecies]
    hotspotMatrix = hotspotMatrix[~hotspotMatrix['speciesId'].isin(excludeSpeciesIds)]

    # move species column to first column of dataframe
    hotspotMatrix = hotspotMatrix[['speciesId'] + [col for col in hotspotMatrix.columns if col != 'speciesId']]

    # resort index starting with 1
    hotspotMatrix.index = range(1, len(hotspotMatrix) + 1)

    # create list of dicts of species ids and the corresponding matrix row
    speciesRows = []
    for index, row in hotspotMatrix.iterrows():
        hotspots = row[1:].to_dict()
        speciesRows.append({
            'index': index,
            'speciesId': int(row['speciesId']),
            'speciesName': speciesHashMap[row['speciesId']],
            'freq': [int(x) if x == x else '' for x in row[1:].values]
        })

    return render_template(
        'trips/matrix.html',
        page='matrix',
        trip=trip,
        hotspots=hotspots,
        speciesRows=speciesRows
    )


@bp.route('/trip/<int:id>/species')
@login_required
def species(id):
    db = app.db
    trip = getTrip(db.session, id)
    if trip is None or trip.userId != g.user.id:
        flash(f"Trip not found.")
        return redirect(url_for("home.home"))

    return render_template(
        'trips/species.html',
        page='species',
        trip=trip
    )