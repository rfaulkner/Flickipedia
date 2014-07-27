"""
Mediawiki oauth glue

    http://pythonhosted.org/mwoauth
    https://www.mediawiki.org/wiki/Extension:OAuth
"""

from mwoauth import ConsumerToken, Handshaker
from flickipedia.config import settings


def getMWIdentity():
    consumer_token = ConsumerToken(settings.MW_CLIENT_KEY, settings.MW_CLIENT_SECRET)

    # Construct handshaker with wiki URI and consumer
    handshaker = Handshaker("http://commons.wikimedia.org/wiki/Main_Page",
                            consumer_token)

    # Step 1: Initialize -- ask MediaWiki for a temporary key/secret for user
    redirect, request_token = handshaker.initiate()

    # Step 2: Authorize -- send user to MediaWiki to confirm authorization
    print("Point your browser to: %s" % redirect) #
    response_qs = input("Response query string: ")

    # Step 3: Complete -- obtain authorized key/secret for "resource owner"
    access_token = handshaker.complete(request_token, response_qs)

    # Step 4: Identify -- (optional) get identifying information about the user
    identity = handshaker.identify(access_token)

    return identity


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