"""
Mediawiki oauth glue

    http://pythonhosted.org/mwoauth
    https://www.mediawiki.org/wiki/Extension:OAuth
"""

import cPickle
import requests
from requests_oauthlib import OAuth1

from flickipedia.redisio import DataIORedis, hmac
from mwoauth import ConsumerToken, Handshaker
from flickipedia.config import settings, log


MW_API_URL = "https://en.wikipedia.org/w/api.php"

COMMONS_API_URL = "https://commons.wikimedia.org/w/api.php"
COMMONS_URL = "https://commons.wikimedia.org"

USER_AGENT = "Flickipedia 1.0"


def getPicklerFilename(type, key):
    """Formats the pickle filename
    :param type:    object type to pickle
    :param key:     unique id
    :return:        string filename
    """
    return settings.SERVER_ROOT + '/' + \
           settings.MWOAUTH_PKL_PATH + '/' + \
           type + '_' + key


def set_serialized(obj, type, key):
    """Sets the pickle file for this type/key
    :param obj:     object to serialize
    :param type:    object type to pickle
    :param key:     unique id
    """
    fname = getPicklerFilename(type, key)
    with open(fname, 'wb') as f:
        log.info('Setting pickle: ' + fname)
        cPickle.dump(obj, f)


def get_serialized(type, key):
    """Retrieves the obj from pickle file for this type/key
    :param type:    object type to pickle
    :param key:     unique id
    :return:        serialized object
    """
    fname = getPicklerFilename(type, key)
    with open(fname, 'rb') as f:
        log.info('Fetching pickle: ' + fname)
        return cPickle.load(f)


def get_MW_redirect(user):
    """Fetch redirect from mwoauth via consumer token for user
    :param user:    string, user
    :return:        string, redirect url for user
    """
    consumer_token = ConsumerToken(settings.MW_CLIENT_KEY,
                                   settings.MW_CLIENT_SECRET)

    # Construct handshaker with wiki URI and consumer
    url = "https://en.wikipedia.org/w/index.php"
    handshaker = Handshaker(COMMONS_URL, consumer_token)

    # Step 1: Initialize -- ask MediaWiki for a temporary key/secret for user
    redirect, request_token = handshaker.initiate()

    # Pickle the handshaker & request token
    key = hmac(user)
    set_serialized(handshaker, settings.MWOAUTH_HANDSHAKER_PKL_KEY, key)
    set_serialized(request_token, settings.MWOAUTH_REQTOKEN_PKL_KEY, key)

    # Step 2: Authorize -- send user to MediaWiki to confirm authorization
    return redirect


def get_MW_access_token(user, response_query_string):
    """Generate Access token from MW auth query string + access token
    :param user:                    string, user
    :param handshaker:              Handshakerobject from mwoauth
    :param response_query_string:   Query string from MW auth
    :return:
    """
    key = hmac(user)

    # unpickle the handshaker
    handshaker = get_serialized(settings.MWOAUTH_HANDSHAKER_PKL_KEY, key)
    req_token = get_serialized(settings.MWOAUTH_REQTOKEN_PKL_KEY, key)

    # Obtain authorized key/secret for "resource owner"
    access_token = handshaker.complete(req_token, response_query_string)

    # Serialize access token in redis - ovewrite request token
    set_serialized(access_token, settings.MWOAUTH_ACCTOKEN_PKL_KEY, key)

    return access_token


def get_MW_identity(user):
    """Get identifying information about the user
    :param user:            string, user
    :param handshaker:      Handshakerobject from mwoauth
    :return:                MW identity object
    """
    key = hmac(user)
    handshaker = get_serialized(settings.MWOAUTH_HANDSHAKER_PKL_KEY, key)
    access_token = get_serialized(settings.MWOAUTH_ACCTOKEN_PKL_KEY, key)
    return handshaker.identify(access_token)


def api_upload_url(photo_url, token, filename, async=True):
    """ Wrapper around mediawiki api upload functionality

    :param url:     photo url
    :param token:   access token
    :param async:   flag for asynchronous upload

    api.php?action=upload&url=http://www.google.com/intl/en_ALL/images/logo.gif&token=+\&asyncdownload=1

    :return:    success flag
    """
    # Create auth object
    auth1 = OAuth1(
        settings.MW_CLIENT_KEY,
        client_secret=settings.MW_CLIENT_SECRET,
        resource_owner_key=token.key,
        resource_owner_secret=token.secret
    )

    # Compose query params & header
    header = {'User-Agent': USER_AGENT}
    edittoken = api_fetch_edit_token(token)
    data = {
        'format': 'json',
        'action': 'upload',
        'url': photo_url,
        'token': edittoken,
        'filename': filename,
    }
    # DISABLED
    #
    # if async:
    #     data['asyncdownload'] = 1

    # Send request
    response = requests.post(COMMONS_API_URL, data, auth=auth1, headers=header)

    if response.status_code != requests.codes.ok:
        log.error('Bad response status: "%s"' % response.status_code)
    else:
        # TODO - Update the upload model
        log.info('upload photo url: %s' % photo_url)
        log.info('upload edit token: %s' % str(edittoken))
        pass
    return response


def api_fetch_edit_token(token):
    """Get an edit token"""
    auth1 = OAuth1(
        settings.MW_CLIENT_KEY,
        client_secret=settings.MW_CLIENT_SECRET,
        resource_owner_key=token.key,
        resource_owner_secret=token.secret
    )
    header = {'User-Agent': USER_AGENT}
    data = {
        'format': 'json',
        'action': 'tokens',
        'type': 'edit',
    }
    # Fetch token, send request
    response = requests.get(COMMONS_API_URL, params=data, auth=auth1, headers=header)
    if response.status_code != requests.codes.ok:
        log.error('Bad response status: "%s"' % response.status_code)

    try:
        return response.json()['tokens']['edittoken']
    except (ValueError, KeyError) as e:
        log.error("Missing Edit token: %s" % e.message)
        return None