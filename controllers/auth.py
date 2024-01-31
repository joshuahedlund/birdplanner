import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app as app
)
from werkzeug.security import check_password_hash, generate_password_hash

from repositories.UserRepository import storeUser, getUserByEmail, getUserById

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = getUserById(app.db.session, user_id)

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        db = app.db
        error = None

        if not email:
            error = 'Email is required.'
        elif not password:
            error = 'Password is required.'

        if len(password) < 8:
            error = 'Password must be at least 8 characters long.'

        if error is None:
            try:
                storeUser(db.session, email, generate_password_hash(password))
            except db.IntegrityError:
                app.logger.warning(str(db.IntegrityError))
                error = f"Email is already registered."
            else:
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        db = app.db
        error = None
        user = getUserByEmail(db.session, email)

        if user is None or not check_password_hash(user.password, password):
            error = 'Invalid login.'

        if error is None:
            session.clear()
            session['user_id'] = user.id
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view