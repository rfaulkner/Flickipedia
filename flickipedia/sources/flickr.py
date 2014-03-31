"""
Hook into Fickr API via python client

    http://stuvel.eu/flickrapi
"""

import urllib2

import flickrapi
from flickipedia.config import log, settings


def call(args, params=None):
    """ Invokes API method """

    log.debug('API KEY = {0}, SECRET = {1}'.format(
        settings.FLICKR_API_KEY,
        settings.FLICKR_API_SECRET
    ))
    flickr = flickrapi.FlickrAPI(settings.FLICKR_API_KEY, secret=settings.FLICKR_API_SECRET)

    try:
        # Extract the api method
        log.debug('Calling method - ' + args.method)
        method = getattr(flickr, args.method)
    except Exception:
        log.error('No such API method.')
        return

    try:
        if params:
            return method(format='json')
        else:
            return method(params)
    except urllib2.HTTPError as e:
        log.error('Could not reach service.')
    except Exception as e:
        log.error(e.message())
        return None