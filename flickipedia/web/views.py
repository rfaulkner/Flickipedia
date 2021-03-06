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
import requests

from flickipedia.redisio import _decode_dict, DataIORedis
from flickipedia.mysqlio import DataIOMySQL
from flickipedia.sources.mediawiki import get_MW_redirect, get_MW_access_token

from flickipedia.config import log, settings
from flickipedia.web import app, login_manager
from flickipedia.web.rest import api_method_endorse_event, \
    api_method_endorse_fetch, api_method_exclude_event, \
    api_method_exclude_fetch, api_method_endorse_count, \
    api_method_exclude_count
from flickipedia.sources import flickr, mediawiki as mw

from flickipedia.model.articles import ArticleModel
from flickipedia.model.photos import PhotoModel
from flickipedia.model.uploads import UploadsModel
from flickipedia.model.users import UserModel
from flickipedia.mashup import get_article_count, get_article_stored_body, \
    get_flickr_photos, manage_article_storage, get_max_article_id, \
    order_photos_by_rank, handle_article_content_insert, prep_page_content, \
    handle_article_insert
from flickipedia.error import WikiAPICallError, FlickrAPICallError

import wikipedia
from wikipedia.exceptions import DisambiguationError, PageError

from flask import render_template, redirect, url_for, \
    request, escape, flash, Response

__author__ = 'Ryan Faulkner'
__date__ = "2014-03-30"


# Flask Login Code - https://flask-login.readthedocs.org/en/latest/

from flickipedia.redisio import hmac
from flask.ext.login import login_required, logout_user, \
    confirm_login, login_user, fresh_login_required, current_user, UserMixin, \
    AnonymousUserMixin
# from werkzeug.security import generate_password_hash,\
#     check_password_hash


API_METHOD_ENDORSE_EVENT = 'api_photo_endorse_event'
API_METHOD_EXCLUDE_EVENT = 'api_photo_exclude_event'
API_METHOD_ENDORSE_FETCH = 'api_photo_endorse_fetch'
API_METHOD_EXCLUDE_FETCH = 'api_photo_exclude_fetch'
API_METHOD_ENDORSE_COUNT = 'api_photo_endorse_count'
API_METHOD_EXCLUDE_COUNT = 'api_photo_exclude_count'


class User(UserMixin):
    """
        Extends USerMixin.  User class for flask-login.  Implements a way
        to add user credentials with _HMAC and salting.

        .. HMAC_: http://tinyurl.com/d8zbbem

    """
    def __init__(self, userid):

        with UserModel() as um:
            user = um.fetch_user_by_id(userid)

        if user:
            self.id = unicode(user._id)
            self.name = unicode(user.handle)
            self.handle = unicode(user.handle)
            self.active = True
            self.pw_hash = str(user.password)
            self.authenticated = True

        else:
            self.id = None
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
        if not self.id:
            anon_key = request.headers.get('User-Agent') + request.remote_addr
            return str(int(hashlib.md5(str(anon_key)).hexdigest(), 16))[:18]
        else:
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


def maintenance(view_func):
    """ Decorator method for invoking the maintenance template
    :param view_func:   view method to decorate
    :return:            the wrapper
    """
    def wrapper(*args):
        if settings.MAINTENANCE:
            return render_template('login.html')
        view_func(*args)
    return wrapper


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST' and 'username' in request.form:

        username = escape(str(request.form['username'].strip()))
        passwd = escape(str(request.form['password'].strip()))
        remember = request.form.get('remember', 'no') == 'yes'

        log.info('Attempting login for "%s"' % username)

        with UserModel() as um:
            user = um.fetch_user_by_name(username)
        if not user:
            log.info('On login - User not found "%s"' % username)
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
    with ArticleModel() as am:
        accessed = [a.article_name
                    for a in am.get_most_recently_accessed(5)]
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


def mwoauth():
    """Initiate the mw-auth for this user by sending them to MW
    :return:    template for view
    """
    id = User(current_user.get_id()).get_id()
    redirect = get_MW_redirect(id)
    return render_template('mwoauth.html', redirect=redirect)


def mwoauth_complete():
    """Complete the mw-auth for this user by storing their access token
    :return:    template for view
    """
    url = escape(str(request.form['callback_url'].strip()))
    id = User(current_user.get_id()).get_id()
    query_params = url.split('?')[-1]
    success = True
    try:
        get_MW_access_token(id, query_params)
    except Exception as e:
        log.error('Failed to generate access token: "%s"' % e.message)
        success = False
    return render_template('mwoauth_complete.html', success=success)


def upload():
    """GET, Renders the page for performing upload to mediawiki via api
    :return:    template for view
    """
    photourl = request.args.get(settings.GET_VAR_PHOTOURL)
    article = request.args.get(settings.GET_VAR_ARTICLE)
    flickr_photo_id = request.args.get(settings.GET_VAR_FLICKR_PHOTO_ID)
    articleurl = settings.SITE_URL + '/mashup?article=' + article
    return render_template('upload.html',
                           photourl=photourl,
                           articleurl=articleurl,
                           article=article,
                           flickr_photo_id=flickr_photo_id,
                           photo_width=settings.TEMPLATE_UPLOAD_PHOTO_WIDTH
                           )


def upload_complete():
    """POST, Renders the page for completing upload to mediawiki via api
    :return:    template for view
    """

    success = True

    msg = ''

    #  Attempt api upload
    uid = hmac(User(current_user.get_id()).get_id())

    log.info('Attempting upload to Commons for user: ' + uid)

    article = request.form['article']
    filename = request.form['filename']
    photourl = request.form['photourl']
    flickr_photo_id = request.form['flickr_photo_id']
    articleurl = settings.SITE_URL + '/mashup?article=' + article

    # Obtain access token if it exists
    acc_token = None
    try:
        acc_token = mw.get_serialized(settings.MWOAUTH_ACCTOKEN_PKL_KEY, uid)

    except IOError:
        msg = 'No mediawiki token for your user. See <a href="%s">MWOauth</a>' % (
            settings.SITE_URL + '/mwoauth')
        log.info('No mediawiki token for "%s"' % str(uid))
        success = False


    # If access token was successfully fetched talk to commons api
    if success:
        response = mw.api_upload_url(request.form['photourl'], acc_token, filename)


        # Validate the response
        if response.status_code != requests.codes.ok:
            success = False
            msg = str(response.status_code)
        elif 'error' in response.json():
            success = False
            msg = response.json()['error']['info']
        else:
            success = True
            msg = 'OK'

        # Determine if the photo has already been uploaded to commons
        with UploadsModel() as um:
            if um.get_upload(flickr_photo_id):
                msg = 'This photo has already been uploaded.'
                success = False

        # Ensure that upload model is updated
        if success:
            with ArticleModel() as am:
                article_data = am.get_article_by_name(article)
            with PhotoModel() as pm:
                photo_data = pm.get_photo(flickr_photo_id, article_data.id)
            with UploadsModel() as um:
                um.insert_upload(photo_data.id, flickr_photo_id, article_data.id, uid)

        log.info('UPLOAD RESPONSE: ' + str(response.json()))

    return render_template('upload_complete.html',
                           success=success,
                           articleurl=articleurl,
                           article=article,
                           photourl=photourl,
                           apierror=msg
                           )


def mashup():

    DataIORedis().connect()
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

    # Fetch article count and stored body (if exists)
    article_count = get_article_count()
    body = get_article_stored_body(article)

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
        photos = get_flickr_photos(res_json)
        if not photos:
            render_template('index.html', error="Couldn't find any photos "
                                                "for '{0}'!".format(article))

        # 1. Fetch the max article - Refresh periodically
        # 2. Remove a random article and replace, ensure that max has
        #       been fetched
        # 3. Article insertion and ORM fetch
        # 4. rank photos according to UGC
        # 5. Photo & markup parsing
        # 6. Article content insertion and ORM fetch
        max_aid = get_max_article_id()
        manage_article_storage(max_aid, article_count)
        article_id, insert_ok = handle_article_insert(article, wiki.pageid)
        photos = order_photos_by_rank(article_id, photos)
        page_content = prep_page_content(article_id, article, wiki, photos,
                                         User(current_user.get_id()))
        if insert_ok:
            handle_article_content_insert(article_id, page_content, not body)

    else:
        page_content = json.loads(body, object_hook=_decode_dict)
        # refresh the user id
        page_content['user_id'] = User(current_user.get_id()).get_id()

    # Update last_access
    with ArticleModel() as am:
        am.update_last_access(page_content['article_id'])

    log.info('Rendering article "%s"' % article)
    return render_template('mashup.html', **page_content)


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

    elif method == API_METHOD_ENDORSE_COUNT:
        log.info('On %s getting (article, photo) = (%s, %s)' % (
            API_METHOD_EXCLUDE_COUNT, article_id, photo_id))
        res = api_method_endorse_count(article_id, photo_id)
        return Response(json.dumps({'endorse-count': res}),  mimetype='application/json')

    elif method == API_METHOD_EXCLUDE_COUNT:
        log.info('On %s getting (article, photo) = (%s, %s)' % (
            API_METHOD_EXCLUDE_COUNT, article_id, photo_id))
        res = api_method_exclude_count(article_id, photo_id)
        return Response(json.dumps({'exclude-count': res}),  mimetype='application/json')

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
    api.__name__: api,
    mwoauth.__name__: mwoauth,
    mwoauth_complete.__name__: mwoauth_complete,
    upload.__name__: upload,
    upload_complete.__name__: upload_complete,
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
    mwoauth.__name__: app.route('/mwoauth', methods=['GET']),
    mwoauth_complete.__name__: app.route('/mwoauth_complete',
                                         methods=['POST']),
    upload.__name__: app.route('/mwupload', methods=['GET']),
    upload_complete.__name__: app.route('/mwupload_complete',
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
    api.__name__,
    mwoauth.__name__,
    mwoauth_complete.__name__,
    upload.__name__,
    upload_complete.__name__,
]


# Apply decorators to views
def init_views():
    for key in view_list:
        # Add maintenance wrapper
        # view_list[key] = maintenance(view_list[key])

        # wrap methods for login requirement
        if key not in views_with_anonymous_access:
            view_list[key] = login_required(view_list[key])

    for key in route_deco:
        route = route_deco[key]
        view_method = view_list[key]
        view_list[key] = route(view_method)

    log.info(__name__ + ' :: Registered views - {0}'.format(str(view_list)))