"""
This module defines exception classes for flickipedia
"""

class WikiAPICallError(Exception):
    """ Basic exception class for Wiki api calls """
    def __init__(self, message="Wiki api call error."):
        Exception.__init__(self, message)


class FlickrAPICallError(Exception):
    """ Basic exception class for Flickr api calls"""
    def __init__(self, message="Flickr api call error."):
        Exception.__init__(self, message)
