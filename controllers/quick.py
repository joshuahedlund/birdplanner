from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app as app
)


bp = Blueprint('quick', __name__)


@bp.route('/quick')
def quick():
    return render_template('quick.html')