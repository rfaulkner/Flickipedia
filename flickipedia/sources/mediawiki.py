"""
Mediawiki oauth glue

    http://pythonhosted.org/mwoauth
    https://www.mediawiki.org/wiki/Extension:OAuth
"""

from flickipedia.redisio import DataIORedis, hmac
from mwoauth import ConsumerToken, Handshaker
from flickipedia.config import settings


def getMWRedirect(user):
    """Fetch redirect from mwoauth via consumer token for user
    :param user:    string, user
    :return:        string, redirect url for user
    """
    consumer_token = ConsumerToken(settings.MW_CLIENT_KEY,
                                   settings.MW_CLIENT_SECRET)

    # Construct handshaker with wiki URI and consumer
    handshaker = Handshaker("http://en.wikipedia.org/wiki/Main_Page",
                            consumer_token)

    # Step 1: Initialize -- ask MediaWiki for a temporary key/secret for user
    redirect, request_token = handshaker.initiate()

    # Store request_token in redis
    # TODO - ensure user and request_token are properly serialized
    key = hmac(user)
    DataIORedis().write(key, request_token)

    # Step 2: Authorize -- send user to MediaWiki to confirm authorization
    return redirect


def getMWAccessToken(user, handshaker, response_query_string):
    """Generate Access token from MW auth query string + access token
    :param user:                    string, user
    :param handshaker:              Handshakerobject from mwoauth
    :param response_query_string:   Query string from MW auth
    :return:
    """
    key = hmac(user)

    # Obtain authorized key/secret for "resource owner"
    request_token = DataIORedis().read(key)
    access_token = handshaker.complete(request_token, response_query_string)

    # Put access token in redis - ovewrite request token
    key = hmac(user)
    DataIORedis().write(key, request_token)

    return access_token


def getMWidentity(user, handshaker):
    """Get identifying information about the user
    :param user:            string, user
    :param handshaker:      Handshakerobject from mwoauth
    :return:                MW identity object
    """
    key = hmac(user)
    access_token = DataIORedis().read(key)
    return handshaker.identify(access_token)


def api_upload_url(url, token, async=True):
    """ Wrapper around mediawiki api upload functionality

    :param url:     photo url
    :param token:   edit token
    :param async:   flag for asynchronous upload

    api.php?action=upload&url=http://www.google.com/intl/en_ALL/images/logo.gif&token=+\&asyncdownload=1

    :return:    success flag
    """
    call_url = 'https://en.wikipedia.org/w/api.php?action=upload&url=%s&token=%s'
    if async:
        call_url += '&asyncdownload=1'


def api_upload_status():
    """
    api.php?action=upload&checkstatus=true&filekey=somekey1234.jpg&token=+\
    :return:
    """
    pass