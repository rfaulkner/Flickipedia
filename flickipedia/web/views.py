"""
Module implementing the view portion of the MVC pattern.
"""

# Fixes issue with jinja template encoding in unicode
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import json
import hashlib
import time

from flickipedia.parse import parse_strip_elements, parse_convert_links
from flickipedia.redisio import DataIORedis, _decode_list, _decode_dict
from flickipedia.mysqlio import DataIOMySQL

from flickipedia.config import log, settings
from flickipedia.web import app
from flickipedia.sources import flickr

import wikipedia
from wikipedia.exceptions import DisambiguationError, PageError

from flask import render_template, redirect, url_for, \
    request, escape, flash

__author__ = 'Ryan Faulkner'
__date__ = "2014-03-30"


# Flask Login views

from flickipedia.web.session import APIUser

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


def register():
    return render_template('register.html')


def register_process():

    handle = request.form['handle']
    firstname = request.form['fname']
    lastname = request.form['lname']
    email = request.form['email']
    passwd = request.form['passwd']

    mysql_inst = DataIOMySQL().connect_lite()
    # TODO - check for duplicates
    mysql_inst.insert('User',
                      handle=handle,
                      email=email,
                      firstname=firstname,
                      lastname=lastname,
                      password=hashlib.md5(passwd + settings.__secret_key__),
                      date_join=int(time.time()))

    return render_template('index_anon.html')


def about():
    return render_template('about.html')


def contact():
    return render_template('contact.html')


def version():
    return render_template('version.html', version=settings.__version__)


def mashup():

    DataIORedis().connect()

    # Check for POST otherwise GET
    # TODO - notify on failure of both
    if request.form:
        article = request.form['article']
        log.debug('Processing POST - ' + article)

    else:
        article = request.args.get(settings.GET_VAR_ARTICLE)
        log.debug('Processing GET - ' + article)

    key = hashlib.md5(article).hexdigest()
    body = DataIORedis().read(key)

    if not body:

        try:
            wiki = wikipedia.WikipediaPage(article, preload=True)
        except DisambiguationError as e:
             return render_template('disambiguate.html', options=e.options)
        except PageError as e:
            return render_template(
                'index_anon.html', error="Couldn't find the content for "
                                           "'{0}'.".format(article))

        html = parse_strip_elements(wiki.html())
        html = parse_convert_links(html)
        res = flickr.call('photos_search', {'text': article,
                                            'format': 'json',
                                            'sort': 'relevance',
                                            })
        res_json = json.loads(res[14:-1])

        # Extract data for the first photo returned
        owner = res_json['photos']['photo'][0]['owner']
        photo_id = res_json['photos']['photo'][0]['id']
        farm = res_json['photos']['photo'][0]['farm']
        server = res_json['photos']['photo'][0]['server']
        title = res_json['photos']['photo'][0]['title']
        secret = res_json['photos']['photo'][0]['secret']

        page_content = {
            'content': html,
            'owner': owner,
            'photo_id': photo_id,
            'farm': farm,
            'server': server,
            'title': title,
            'secret': secret
        }
        DataIORedis().write(key, json.dumps(page_content))

    else:
        page_content = json.loads(body, object_hook=_decode_dict)
        # page_content['content'] = unicode(page_content['content'])

    return render_template('mashup.html', **page_content)


# Add View Decorators
# ##

# Stores view references in structure
view_list = {
    home.__name__: home,
    about.__name__: about,
    contact.__name__: contact,
    version.__name__: version,
    mashup.__name__: mashup,
    register.__name__: register,
    register_process.__name__: register,
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
    mashup.__name__: app.route('/mashup',  methods=['GET', 'POST']),
    register.__name__: app.route('/register'),
    register_process.__name__: app.route('/register_process',
                                         methods=['POST']),
}

# Dict stores flag for login required on view
views_with_anonymous_access = [
    home.__name__,
    about.__name__,
    contact.__name__,
    mashup.__name__,
    register.__name__,
    register_process.__name__,
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