"""
Mediawiki oauth glue

    http://pythonhosted.org/mwoauth
    https://www.mediawiki.org/wiki/Extension:OAuth
"""

from flickipedia.redisio import DataIORedis, hmac
from mwoauth import ConsumerToken, Handshaker
from flickipedia.config import settings
import cPickle
import requests
import time
import random
import hashlib
import jwt
import urllib


def getPicklerFilename(type, key):
    """Formats the pickle filename
    :param type:    object type to pickle
    :param key:     unique id
    :return:        string filename
    """
    return settings.SERVER_ROOT + '/' + \
           settings.MWOAUTH_PKL_PATH + '/' + \
           type + '_' + key


def setSerialized(obj, type, key):
    """Sets the pickle file for this type/key
    :param obj:     object to serialize
    :param type:    object type to pickle
    :param key:     unique id
    """
    with open(getPicklerFilename(type, key), 'wb') as f:
        cPickle.dump(obj, f)


def getSerialized(type, key):
    """Retrieves the obj from pickle file for this type/key
    :param type:    object type to pickle
    :param key:     unique id
    :return:        serialized object
    """
    with open(getPicklerFilename(type, key), 'rb') as f:
        return cPickle.load(f)


def getMWRedirect(user):
    """Fetch redirect from mwoauth via consumer token for user
    :param user:    string, user
    :return:        string, redirect url for user
    """
    consumer_token = ConsumerToken(settings.MW_CLIENT_KEY,
                                   settings.MW_CLIENT_SECRET)

    # Construct handshaker with wiki URI and consumer
    url = "https://en.wikipedia.org/w/index.php"
    handshaker = Handshaker(url, consumer_token)

    # Step 1: Initialize -- ask MediaWiki for a temporary key/secret for user
    redirect, request_token = handshaker.initiate()

    # Pickle the handshaker & request token
    key = hmac(user)
    setSerialized(handshaker, settings.MWOAUTH_HANDSHAKER_PKL_KEY, key)
    setSerialized(request_token, settings.MWOAUTH_REQTOKEN_PKL_KEY, key)

    # Step 2: Authorize -- send user to MediaWiki to confirm authorization
    return redirect


def getMWAccessToken(user, response_query_string):
    """Generate Access token from MW auth query string + access token
    :param user:                    string, user
    :param handshaker:              Handshakerobject from mwoauth
    :param response_query_string:   Query string from MW auth
    :return:
    """
    key = hmac(user)

    # unpickle the handshaker
    handshaker = getSerialized(settings.MWOAUTH_HANDSHAKER_PKL_KEY, key)
    req_token = getSerialized(settings.MWOAUTH_REQTOKEN_PKL_KEY, key)

    # Obtain authorized key/secret for "resource owner"
    access_token = handshaker.complete(req_token, response_query_string)

    # Serialize access token in redis - ovewrite request token
    setSerialized(access_token, settings.MWOAUTH_ACCTOKEN_PKL_KEY, key)

    return access_token


def getMWidentity(user):
    """Get identifying information about the user
    :param user:            string, user
    :param handshaker:      Handshakerobject from mwoauth
    :return:                MW identity object
    """
    key = hmac(user)
    handshaker = getSerialized(settings.MWOAUTH_HANDSHAKER_PKL_KEY, key)
    access_token = getSerialized(settings.MWOAUTH_ACCTOKEN_PKL_KEY, key)
    return handshaker.identify(access_token)


def sign_request(method, url, params = None):
    """Signs an oauth request and returns signature
    :param method:      API method name
    :param url:         API url
    :param params:      optional parameters
    :return:            signature
    """
    raise NotImplementedError()


def api_upload_url(url, token, async=True):
    """ Wrapper around mediawiki api upload functionality

    :param url:     photo url
    :param token:   edit token
    :param async:   flag for asynchronous upload

    api.php?action=upload&url=http://www.google.com/intl/en_ALL/images/logo.gif&token=+\&asyncdownload=1

    :return:    success flag
    """
    rstr = hashlib.md5(str(time.time()) + str(random.randint(0, 99999999)))
    header = {
                 'oauth_consumer_key': settings.MW_CLIENT_KEY,
                 'oauth_token': token,
                 'oauth_version': 1.0,
                 'oauth_nonce': rstr.hexdigest(),
                 'oauth_timestamp': int(time.time()),
    }
    sig = sign_request('upload', url)
    header['oauth_signature'] = sig
    header = urllib.urlencode(header)
    header = 'Authorization: OAuth ' + ",".join(header)

    # call_url = 'https://en.wikipedia.org/w/api.php?action=upload&url=%s&token=%s'
    # if async:
    #     call_url += '&asyncdownload=1'


def api_upload_status():
    """
    api.php?action=upload&checkstatus=true&filekey=somekey1234.jpg&token=+\
    :return:
    """
    pass