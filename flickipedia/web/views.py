"""
Module implementing the view portion of the MVC pattern.
"""

# Fixes issue with jinja template encoding in unicode
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import json
import time
import hashlib

from flickipedia.parse import parse_strip_elements, parse_convert_links, \
    handle_photo_integrate, format_title_link, add_formatting_generic
from flickipedia.redisio import DataIORedis, _decode_dict
from flickipedia.mysqlio import DataIOMySQL

from flickipedia.config import log, settings, schema
from flickipedia.web import app, login_manager
from flickipedia.web.rest import api_method_endorse_event, \
    api_method_endorse_fetch, api_method_exclude_event, \
    api_method_exclude_fetch
from flickipedia.sources import flickr

from flickipedia.model.articles import ArticleModel, ArticleContentModel
from flickipedia.model.photos import PhotoModel
from flickipedia.model.likes import LikeModel
from flickipedia.rank import order_photos_by_rank

from flickipedia.error import WikiAPICallError, FlickrAPICallError

import wikipedia
from wikipedia.exceptions import DisambiguationError, PageError

from flask import render_template, redirect, url_for, \
    request, escape, flash, g, session, Response

__author__ = 'Ryan Faulkner'
__date__ = "2014-03-30"


# Flask Login Code - https://flask-login.readthedocs.org/en/latest/

from flickipedia.redisio import hmac
from flask.ext.login import login_required, logout_user, \
    confirm_login, login_user, fresh_login_required, current_user, UserMixin, \
    AnonymousUserMixin
# from werkzeug.security import generate_password_hash,\
#     check_password_hash

NUM_PHOTOS = 20

API_METHOD_ENDORSE_EVENT = 'api_photo_endorse_event'
API_METHOD_EXCLUDE_EVENT = 'api_photo_exclude_event'
API_METHOD_ENDORSE_FETCH = 'api_photo_endorse_fetch'
API_METHOD_EXCLUDE_FETCH = 'api_photo_exclude_fetch'


class User(UserMixin):
    """
        Extends USerMixin.  User class for flask-login.  Implements a way
        to add user credentials with _HMAC and salting.

        .. HMAC_: http://tinyurl.com/d8zbbem

    """
    def __init__(self, userid):

        mysql_inst = DataIOMySQL()
        mysql_inst.connect()

        try:
            user = mysql_inst.sess.query(schema.User).filter(schema.User._id == userid)[0]
        except (KeyError, IndexError) as e:
            user = None
            log.info('User not found "%s": %s' % (userid, e.message))

        if user:
            self.id = unicode(user._id)
            self.name = unicode(user.handle)
            self.handle = unicode(user.handle)
            self.active = True
            self.pw_hash = str(user.password)
            self.authenticated = True

        else:
            self.id = -1
            self.name = "anon"
            self.handle = "anon"
            self.active = False
            self.pw_hash = None
            self.authenticated = False

    @staticmethod
    def get(userid):
        return User(userid)

    def is_active(self):
        """
        Returns True if this is an active user - in addition to being
        authenticated, they also have activated their account, not been
        suspended, or any condition your application has for rejecting an
        account. Inactive accounts may not log in (without being forced of
        course).
        """
        return self.active

    def is_authenticated(self):
        """
        Returns True if the user is authenticated, i.e. they have provided
        valid credentials. (Only authenticated users will fulfill the
        criteria of login_required.)
        """
        return self.authenticated

    def is_anonymous(self):
        """
        Returns True if this is an anonymous user. (Actual users should
        return False instead.)
        """
        return False

    def authenticate(self, password):
        password = escape(str(password))
        if self.check_password(password):
            self.authenticated = True
        else:
            self.authenticated = False
        return self.authenticated

    def get_id(self):
        """
        Returns a unicode that uniquely identifies this user, and can be used
        to load the user from the user_loader callback. Note that this must
        be a unicode - if the ID is natively an int or some other type, you
        will need to convert it to unicode.
        """
        return self.id

    def check_password(self, password):

        if self.pw_hash:
            try:
                password = escape(str(password))
                return self.pw_hash == hmac(password)
            except (TypeError, NameError) as e:
                log.error(__name__ +
                              ' :: Hash check error - ' + e.message)
                return False
        else:
            return False


class Anonymous(AnonymousUserMixin):
    name = u'Anonymous'


@login_manager.user_loader
def load_user(userid):
    return User.get(userid)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST' and 'username' in request.form:

        username = escape(str(request.form['username'].strip()))
        passwd = escape(str(request.form['password'].strip()))
        remember = request.form.get('remember', 'no') == 'yes'

        log.info('Attempting login for "%s"' % username)

        # Initialize user
        mysql_inst = DataIOMySQL()
        mysql_inst.connect()

        try:
            user = mysql_inst.sess.query(schema.User).filter(schema.User.handle == username)[0]
        except (KeyError, IndexError) as e:
            log.info('On login - User not found "%s": %s' % (username, e.message))
            flash('Login failed.')
            return render_template('login.html')

        user_ref = User(user._id)
        user_ref.authenticate(passwd)

        if user_ref.is_authenticated():
            login_user(user_ref, remember=remember)
            flash('Logged in.')
            return redirect(request.args.get('next')
                            or url_for('home'))
        else:
            flash('Login failed.')
    return render_template('login.html')


@app.route('/logout')
def logout():
    logout_user()
    flash('Logged out.')
    return redirect(url_for('home'))


def home():
    """ View for root url - API instructions """
    accessed = [a.article_name
                for a in ArticleModel().get_most_recently_accessed(5)]
    # liked = LikeModel().get_most_likes(5)
    return render_template('index.html', accessed=accessed)


def register():
    return render_template('register.html')


def register_process():
    """
    Handles user registration
    """

    handle = escape(str(request.form['handle'].strip()))
    firstname = escape(str(request.form['fname'].strip()))
    lastname = escape(str(request.form['lname'].strip()))
    email = escape(str(request.form['email'].strip()))
    passwd = escape(str(request.form['passwd'].strip()))

    mysql_inst = DataIOMySQL()
    mysql_inst.connect()

    # TODO - check for duplicates / additional validation
    mysql_inst.insert(
        'User',
        handle=handle,
        email=email,
        firstname=firstname,
        lastname=lastname,
        password=hmac(passwd),
        date_join=int(time.time())
    )

    # TODO - error condition
    return render_template('login.html')


def about():
    return render_template('about.html')


def contact():
    return render_template('contact.html')


def version():
    return render_template('version.html', version=settings.__version__)


def mashup():

    # DataIORedis().connect()
    mysql_inst = DataIOMySQL()
    mysql_inst.connect()

    # Check for POST otherwise GET
    refresh = False
    if request.form:
        article = str(request.form['article']).strip()
        article = '_'.join(article.split())
        log.debug('Processing POST - ' + article)

    else:
        article = str(request.args.get(settings.GET_VAR_ARTICLE)).strip()
        if 'refresh' in request.args:
            refresh = True
        article = '_'.join(article.split())
        log.debug('Processing GET - ' + article)


    # key = hmac(article)
    article_obj = ArticleModel().get_article_by_name(article)
    try:
        body = ArticleContentModel().get_article_content(
            article_obj._id).markup
        # body = DataIORedis().read(key)
    except Exception as e:
        log.error('Article markup not found: "%s"' % e.message)
        body = ''

    if not body or refresh:

        # Calls to Wiki & Flickr APIs
        try:
            wiki = call_wiki(article)
        except WikiAPICallError as e:
            return render_template(e.template, error=e.message)
        try:
            res_json = call_flickr(article)
        except FlickrAPICallError as e:
            return render_template(e.template, error=e.message)

        # Extract photo data
        photos = []
        for i in xrange(NUM_PHOTOS):
            try:
                photos.append(
                    {
                        'owner': res_json['photos']['photo'][i]['owner'],
                        'photo_id': res_json['photos']['photo'][i]['id'],
                        'farm': res_json['photos']['photo'][i]['farm'],
                        'server': res_json['photos']['photo'][i]['server'],
                        'title': res_json['photos']['photo'][i]['title'],
                        'secret': res_json['photos']['photo'][i]['secret'],
                    },
                )

            except (IndexError, KeyError) as e:
                log.error('No more photos to process for "%s" - "%s"' % (
                    article, e.message))

            log.debug('Photo info for %s: %s' % (article, str(photos)))

        if not photos:
            render_template('index.html', error="Couldn't find any photos "
                                                "for '{0}'!".format(article))

        #   Extract Article data
        #   ====================
        if not article_obj:
            if ArticleModel().insert_article(article, wiki.pageid):
                article_obj = ArticleModel().get_article_by_name(article)
            else:
                log.error('Couldn\'t insert article: "%s"' % article)
                return render_template(
                    'index.html', error="Error processing '{0}'.".format(
                        article))
        article_id = article_obj._id

        # rank photos according to UGC
        photos = order_photos_by_rank(article_id, photos)

        # Photo & markup parsing
        html = parse_strip_elements(wiki.html())
        html = parse_convert_links(html)
        html = add_formatting_generic(html)
        photo_ids = process_photos(article_id, photos)
        html = handle_photo_integrate(photos, html)
        page_content = {
            'title': format_title_link(wiki.title, article),
            'content': html,
            'section_img_class': settings.SECTION_IMG_CLASS,
            'num_photos': len(photos),
            'article_id': article_id,
            'user_id': current_user.get_id(),
            'photo_ids': photo_ids
        }
        try:
            # DataIORedis().write(key, json.dumps(page_content))
            if not body:
                ArticleContentModel().insert_article(article_obj._id,
                                                     json.dumps(page_content))
            else:
                ArticleContentModel().update_article(article_obj._id,
                                                     json.dumps(page_content))
        except Exception as e:
            log.error('Failed to insert article content: "%s"' % e.message)

    else:
        page_content = json.loads(body, object_hook=_decode_dict)
        page_content['user_id'] = current_user.get_id() # refresh the user id

    # Update last_access
    ArticleModel().update_last_access(page_content['article_id'])

    # Handle generating ids for anonymous users
    if not page_content['user_id']:
        anon_key = request.headers.get('User-Agent') + request.remote_addr
        page_content['user_id'] = str(int(hashlib.md5(
            str(anon_key)).hexdigest(), 16))[:18]

    log.info('Rendering article "%s"' % article)
    return render_template('mashup.html', **page_content)


def process_photos(article_id, photos):
    """Handles linking photo results with the model and returns a list of
        Flickr photo ids to pass to templating

        :param photos:  list of photos

        :return:    List of Flickr photo ids
    """
    pm = PhotoModel()
    lm = LikeModel()
    photo_ids = []

    for photo in photos:

        # Ensure that each photo is modeled
        photo_obj = pm.get_photo(photo['photo_id'], article_id)
        if not photo_obj:
            log.info('Processing photo: "%s"' % str(photo))
            if pm.insert_photo(photo['photo_id'], article_id):
                photo_obj = PhotoModel().get_photo(
                    photo['photo_id'], article_id)
                if not photo_obj:
                    log.error('DB Error: Could not retrieve or '
                              'insert: "%s"' % str(photo))
                    continue
            else:
                log.error('Couldn\'t insert photo: "%s"'  % (
                    photo['photo_id']))

        photo['id'] = photo_obj._id
        photo['votes'] = photo_obj.votes

        # Retrieve like data
        if lm.get_like(article_id, photo_obj._id, current_user.get_id()):
            photo['like'] = True
        else:
            photo['like'] = False

        photo_ids.append(photo['photo_id'])
    return photo_ids


def call_flickr(search_str):
    """Handles calling the flickr API via the local model

        :param search_str:
        :return:
    """
    try:
        res = flickr.call('photos_search',
                          {'text': ' '.join(search_str.split('_')),
                           'format': 'json',
                           'sort': 'relevance',
                           'license': "4,5,7,8"
                           })
    except Exception as e:
        log.error('Flickr api.photos.search failed with: "%s"' % e.message)
        raise FlickrAPICallError(
            template='index.html',
            message='Flickr search request failed "%s"' % search_str,
        )
    return json.loads(res[14:-1])


def call_wiki(article):
    """Handles calling the wikipedia API via the local model

        :param article:
        :return:
    """
    try:
        return wikipedia.page(article, preload=True)
    except DisambiguationError as e:
        raise WikiAPICallError(
            template='disambiguate.html',
            message='Received disambiguation list.',
            options=e.options
        )
    except PageError as e:
        raise WikiAPICallError(
            template='index.html',
            message='Couldn\'t find the content for "%s".' % article,
        )
    except (KeyError, TypeError) as e:
        log.error('Couldn\'t find %s: "%s"'  % (article, str(e)))
        raise WikiAPICallError(
            template='index.html',
            message='Couldn\'t find the content for "%s".' % article,
        )
    except Exception as e:
        log.error('Couldn\'t fetch "%s" from api: "%s"' % (
            article, str(e)))
        raise WikiAPICallError(
            template='index.html',
            message='Underlying API could not be reached for "%s".' % article,
        )


def api(method):
    """REST interface for flickipedia - swtches on method calls"""

    # Extract photo-id, article-id, user-id
    article_id = request.args.get('article-id')
    user_id = request.args.get('user-id')
    photo_id = request.args.get('photo-id')

    if method == API_METHOD_ENDORSE_EVENT:
        log.info('On %s getting (article, user, photo) = (%s, %s, %s)' % (
            API_METHOD_ENDORSE_EVENT, article_id, user_id, photo_id))
        api_method_endorse_event(article_id, user_id, photo_id)
        return Response(json.dumps(['endorse-event']),  mimetype='application/json')

    elif method == API_METHOD_ENDORSE_FETCH:
        log.info('On %s getting (article, user, photo) = (%s, %s, %s)' % (
            API_METHOD_ENDORSE_FETCH, article_id, user_id, photo_id))
        res = api_method_endorse_fetch(article_id, user_id, photo_id)
        return Response(json.dumps({'endorse-fetch': res}),  mimetype='application/json')

    elif method == API_METHOD_EXCLUDE_EVENT:
        api_method_exclude_event(article_id, user_id, photo_id)
        return Response(json.dumps(['exclude-event']),  mimetype='application/json')

    elif method == API_METHOD_EXCLUDE_FETCH:
        log.info('On %s getting (article, user, photo) = (%s, %s, %s)' % (
            API_METHOD_EXCLUDE_FETCH, article_id, user_id, photo_id))
        res = api_method_exclude_fetch(article_id, user_id, photo_id)
        return Response(json.dumps({'exclude-fetch': res}),  mimetype='application/json')

    else:
        return Response(json.dumps(['no-content']),  mimetype='application/json')


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
    register_process.__name__: register_process,
    api.__name__: api
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
    api.__name__: app.route('/rest/<method>', methods=['GET', 'POST']),
}

# Dict stores flag for login required on view
views_with_anonymous_access = [
    home.__name__,
    about.__name__,
    contact.__name__,
    mashup.__name__,
    register.__name__,
    register_process.__name__,
    api.__name__
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