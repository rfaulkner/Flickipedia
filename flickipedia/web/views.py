"""
Module implementing the view portion of the MVC pattern.
"""

import os
# import datetime
import time

from versus.config import log
from versus.config.settings import AUTHORS, LICENSE, \
    __version__
from flickipedia.web import app

from flask import render_template, redirect, url_for, \
    request, escape, flash

__author__ = AUTHORS
__date__ = "2013-08-20"
__license__ = LICENSE


# Flask Login views

from versus.src.web.session import APIUser

from flask.ext.login import login_required, logout_user, \
    confirm_login, login_user, fresh_login_required, current_user

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST' and 'username' in request.form:

        username = escape(unicode(str(request.form['username'])))
        passwd = escape(unicode(str(request.form['password'])))
        remember = request.form.get('remember', 'no') == 'yes'

        # Initialize user
        user_ref = APIUser(username)
        user_ref.authenticate(passwd)

        log.debug(__name__ + ' :: Authenticating "{0}"/"{1}" ...'.
            format(username, passwd))

        if user_ref.is_authenticated():
            login_user(user_ref, remember=remember)
            flash('Logged in.')
            return redirect(request.args.get('next')
                            or url_for('api_root'))
        else:
            flash('Login failed.')
    return render_template('login.html')

@app.route('/reauth', methods=['GET', 'POST'])
@login_required
def reauth():
    if request.method == 'POST':
        confirm_login()
        flash(u'Reauthenticated.')
        return redirect(request.args.get('next') or url_for('api_root'))
    return render_template('reauth.html')

@app.route('/logout')
def logout():
    logout_user()
    flash('Logged out.')
    return redirect(url_for('api_root'))


def home():
    """ View for root url - API instructions """

    if current_user.is_anonymous():
        return render_template('index_anon.html')
    else:
        return render_template('index.html')


def about():
    return render_template('about.html')


def contact():
    return render_template('contact.html')


def version():
    return render_template('version.html', version=__version__)

# Add View Decorators
# ##

# Stores view references in structure
view_list = {
    home.__name__: home,
    about.__name__: about,
    contact.__name__: contact,
    version.__name__: version,
}

# Dict stores routing paths for each view

from werkzeug.routing import BaseConverter
class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]

app.url_map.converters['regex'] = RegexConverter

route_deco = {
    home.__name__: app.route('/'),
    about.__name__: app.route('/about/'),
    contact.__name__: app.route('/contact/'),
    version.__name__: app.route('/version'),
}

# Dict stores flag for login required on view
views_with_anonymous_access = [
    home.__name__,
    about.__name__,
    contact.__name__,
]

# Apply decorators to views
def init_views():
    for key in view_list:
        if key not in views_with_anonymous_access:
            view_list[key] = login_required(view_list[key])

    for key in route_deco:
        route = route_deco[key]
        view_method = view_list[key]
        view_list[key] = route(view_method)

    log.info(__name__ + ' :: Registered views - {0}'.format(str(view_list)))