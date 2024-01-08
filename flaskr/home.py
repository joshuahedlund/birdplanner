from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app as app
)

from repositories.TripRepository import getTripsForUser

bp = Blueprint('home', __name__)

@bp.route('/')
def home():
    trips = []
    if g.user:
        trips = getTripsForUser(app.db.session, g.user.id)

    return render_template('index.html', trips=trips)