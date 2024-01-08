from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app as app
)

from repositories.HotspotRepository import getHotspotsForTrip
from repositories.TripRepository import getTrip

bp = Blueprint('trips', __name__)

@bp.route('/trip/<int:id>')
def show(id):
    db = app.db
    trip = getTrip(db.session, id)
    if trip is None or trip.userId != g.user.id:
        flash(f"Trip not found.")
        return redirect(url_for("home.home"))

    tripHotspots = getHotspotsForTrip(db.session, id)

    return render_template('trips/show.html', trip=trip, tripHotspots=tripHotspots)
