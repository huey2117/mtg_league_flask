from urllib.parse import urlparse

from edh_league.db import get_db
from flask import Blueprint
from flask import abort
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for
from flask_login import login_user
from is_safe_url import is_safe_url
from werkzeug.security import check_password_hash

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required. '

        if error is None:
            try:
                db.execute(
                    "INSERT INTO users ()"
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {username} is already registered. "
            else:
                return redirect(url_for('auth.login'))

        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute('some stuff').fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            login_user(user)
            next = request.args.get('next')
            if next:
                if not is_safe_url(next, {urlparse(request.base_url).netloc}):
                    return abort(400)
            return redirect(next or url_for('index'))

        flash(error)
    return render_template('auth/login.html')


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))
